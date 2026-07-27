import json
import os
import pathlib
import pickle
import re
import socket
import sys
import traceback

import google_auth_oauthlib.flow
import googleapiclient
import googleapiclient.http
import googleapiclient.discovery
import googleapiclient.errors
import google.auth.transport.requests
import tqdm

import recorder


UPLOAD_LOG_PATTERN = re.compile(r'uploaded:\s+(?P<path>.+?)\s+->\s+(?P<video_id>\S+)')
CAPTION_UPLOAD_SUCCESS = 'uploaded'
CAPTION_UPLOAD_FAILED = 'failed'
CAPTION_UPLOAD_QUOTA_EXCEEDED = 'quota_exceeded'
YOUTUBE_QUOTA_REASONS = frozenset(('quotaExceeded', 'dailyLimitExceeded'))
YOUTUBE_DURATION_PATTERN = re.compile(
    r'^PT(?:(?P<hours>\d+)H)?(?:(?P<minutes>\d+)M)?(?:(?P<seconds>\d+(?:\.\d+)?)S)?$'
)


def _split_validate_video_name(filename):
    separators = []
    for separator in (recorder.video_name_sep, '|', '__'):
        if separator not in separators:
            separators.append(separator)

    for separator in separators:
        if separator in filename:
            video_id, video_filename = filename.split(separator, 1)
            if video_id and video_filename:
                return video_id, video_filename

    return None, None


def _video_index_key_from_path(video_path):
    video_path = pathlib.PurePath(video_path)
    parts = video_path.parts
    if len(parts) < 4:
        return None

    return parts[-3], parts[-2], parts[-1]


def _build_validate_video_index(validate_root):
    validate_root = pathlib.Path(validate_root)
    video_index = {}

    if not validate_root.exists():
        return video_index

    for video_path in sorted(validate_root.glob('*/*/*.mp4')):
        video_id, video_filename = _split_validate_video_name(video_path.name)
        if not video_id:
            continue

        source_type = video_path.parent.parent.name
        source_name = video_path.parent.name
        video_index[(source_type, source_name, video_filename)] = video_id

    return video_index


def _build_uploaded_video_log_index(log_path):
    if not log_path:
        return {}

    log_path = pathlib.Path(log_path)
    if not log_path.exists():
        return {}

    video_index = {}
    with log_path.open(encoding='utf8') as fp:
        for line in fp:
            match = UPLOAD_LOG_PATTERN.search(line)
            if not match:
                continue

            key = _video_index_key_from_path(match.group('path'))
            if not key:
                continue

            video_index[key] = match.group('video_id')

    return video_index


def find_missing_caption_uploads(caption_root, video_root, source_type=None, source_name=None, log_path=None):
    caption_root = pathlib.Path(caption_root)
    video_root = pathlib.Path(video_root)
    validate_index = _build_validate_video_index(video_root / 'validate')
    log_index = _build_uploaded_video_log_index(log_path)

    search_root = caption_root
    if source_type:
        search_root = search_root / source_type
    if source_type and source_name:
        search_root = search_root / source_name

    if not search_root.exists():
        return []

    results = []
    for caption_path in sorted(search_root.glob('**/*.mp4.vtt')):
        try:
            relative_path = caption_path.relative_to(caption_root)
            current_source_type = relative_path.parts[0]
            current_source_name = relative_path.parts[1]
        except (ValueError, IndexError):
            results.append({
                'caption_path': str(caption_path),
                'video_id': None,
                'status': 'unmatched',
                'message': 'caption path is not under source_type/source_name',
            })
            continue

        if source_type and current_source_type != source_type:
            continue
        if source_name and current_source_name != source_name:
            continue

        video_filename = caption_path.name[:-len('.vtt')]
        index_key = (current_source_type, current_source_name, video_filename)
        video_id = validate_index.get(index_key) or log_index.get(index_key)

        results.append({
            'caption_path': str(caption_path),
            'video_id': video_id,
            'source_type': current_source_type,
            'source_name': current_source_name,
            'video_filename': video_filename,
            'status': 'pending' if video_id else 'unmatched',
        })

    return results


def _print_caption_upload_results(results):
    counts = {}
    for result in results:
        status = result.get('status', 'unknown')
        counts[status] = counts.get(status, 0) + 1
        video_id = result.get('video_id') or '-'
        source_type = result.get('source_type') or '-'
        source_name = result.get('source_name') or '-'
        caption_path = result.get('caption_path') or '-'
        message = result.get('message')
        suffix = f' ({message})' if message else ''
        print(f'{status}: {source_type}/{source_name}: {caption_path} -> {video_id}{suffix}')

    summary = ', '.join(f'{status}={count}' for status, count in sorted(counts.items()))
    print(f'summary: total={len(results)}' + (f', {summary}' if summary else ''))


def _caption_exists(captions, language, caption_name):
    for caption in captions:
        snippet = caption.get('snippet', {})
        if snippet.get('language') == language and snippet.get('name') == caption_name:
            return True

    return False


def _youtube_duration_seconds(duration):
    if not isinstance(duration, str):
        raise ValueError(f'Unsupported YouTube duration: {duration!r}')

    match = YOUTUBE_DURATION_PATTERN.fullmatch(duration)
    if not match or not any(match.groupdict().values()):
        raise ValueError(f'Unsupported YouTube duration: {duration!r}')

    hours = int(match.group('hours') or 0)
    minutes = int(match.group('minutes') or 0)
    seconds = float(match.group('seconds') or 0)
    return hours * 3600 + minutes * 60 + seconds


def _http_error_reasons(exception):
    reasons = set()

    def collect(value, accept_string=False):
        if isinstance(value, dict):
            reason = value.get('reason')
            if isinstance(reason, str):
                reasons.add(reason)
            for key in ('error', 'errors', 'detail', 'details'):
                if key in value:
                    collect(value[key], accept_string=True)
        elif isinstance(value, (list, tuple)):
            for item in value:
                collect(item, accept_string=accept_string)
        elif accept_string and isinstance(value, str):
            try:
                parsed = json.loads(value)
            except (TypeError, ValueError):
                reasons.add(value)
            else:
                if parsed == value:
                    reasons.add(value)
                else:
                    collect(parsed, accept_string=True)

    collect(getattr(exception, 'error_details', None), accept_string=True)

    content = getattr(exception, 'content', None)
    if isinstance(content, bytes):
        try:
            content = content.decode('utf8')
        except UnicodeDecodeError:
            content = None
    if isinstance(content, str):
        try:
            content = json.loads(content)
        except (TypeError, ValueError):
            pass
    collect(content, accept_string=True)

    return reasons


def _is_quota_error(exception):
    return bool(_http_error_reasons(exception) & YOUTUBE_QUOTA_REASONS)


def _resolve_path_from_base(path):
    path = pathlib.Path(path)
    if path.is_absolute():
        return path

    return pathlib.Path(recorder.base_path) / path


def upload_missing_captions_from_roots(
    youtube,
    caption_root,
    video_root,
    dry_run=True,
    source_type=None,
    source_name=None,
    caption_name='via_recorder_vtt',
    check_remote=False,
    delete_skipped=False,
    log_path=None,
    print_results=False,
):
    results = find_missing_caption_uploads(caption_root, video_root, source_type, source_name, log_path)
    quota_exceeded = False

    for result in results:
        if result['status'] != 'pending':
            continue

        if quota_exceeded:
            result['status'] = 'skipped_quota_exceeded'
            continue

        caption_path = result['caption_path']
        if check_remote:
            try:
                remote_captions = youtube.list_captions(result['video_id'])
            except Exception as exception:
                result['status'] = 'failed_remote_check'
                result['message'] = str(exception)
                continue

            if _caption_exists(remote_captions, Youtube.DEFAULT_CAPTION_LANGUAGE, caption_name):
                result['status'] = 'skipped_remote_exists'
                if delete_skipped and not dry_run:
                    pathlib.Path(caption_path).unlink()
                continue

        if dry_run:
            result['status'] = 'dry_run'
            continue

        add_caption = getattr(youtube, 'add_caption_result', youtube.add_caption)
        upload_result = add_caption(result['video_id'], caption_path, caption_name)
        if upload_result is True or upload_result == CAPTION_UPLOAD_SUCCESS:
            pathlib.Path(caption_path).unlink()
            result['status'] = CAPTION_UPLOAD_SUCCESS
        elif upload_result == CAPTION_UPLOAD_QUOTA_EXCEEDED:
            result['status'] = CAPTION_UPLOAD_QUOTA_EXCEEDED
            result['message'] = 'YouTube API quota exceeded'
            quota_exceeded = True
        else:
            result['status'] = CAPTION_UPLOAD_FAILED

    if print_results:
        _print_caption_upload_results(results)

    return results


def upload_missing_captions(
    dry_run=True,
    caption_root=None,
    video_root=None,
    source_type=None,
    source_name=None,
    delete_skipped=False,
    check_remote=False,
    log_path=None,
):
    caption_root = _resolve_path_from_base(caption_root or recorder.config['app']['danmaku_path'])
    video_root = _resolve_path_from_base(video_root or recorder.config['app']['video_path'])
    log_path = _resolve_path_from_base(log_path or 'recorder.log')

    youtube = None
    if not dry_run or check_remote:
        youtube = Youtube(recorder.config.get('youtube'))

    upload_missing_captions_from_roots(
        youtube,
        caption_root,
        video_root,
        dry_run=dry_run,
        source_type=source_type,
        source_name=source_name,
        delete_skipped=delete_skipped,
        check_remote=check_remote,
        log_path=log_path,
        print_results=True,
    )

    return None


class Youtube:
    # Always retry when a googleapiclient.errors.HttpError with one of these status codes is raised.
    RETRYABLE_STATUS_CODES = [500, 502, 503, 504]

    # Always retry when these exceptions are raised.
    RETRYABLE_EXCEPTIONS = (IOError, socket.timeout)

    DEFAULT_CAPTION_LANGUAGE = 'zh-Hans'

    DEFAULT_CATEGORY_ID = 20

    def __init__(self, config):
        scopes = [
            'https://www.googleapis.com/auth/youtube.readonly',
            'https://www.googleapis.com/auth/youtube.upload',
            'https://www.googleapis.com/auth/youtube.force-ssl'
        ]
        api_service_name = 'youtube'
        api_version = 'v3'
        client_secrets_file = config['client_secrets_file']
        credentials_file = config['credentials_file']

        credentials = None
        # The file token.pickle stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists(credentials_file):
            with open(credentials_file, 'rb') as token:
                credentials = pickle.load(token)
        # If there are no (valid) credentials available, let the user log in.
        if not credentials or not credentials.valid:
            if credentials and credentials.expired and credentials.refresh_token:
                credentials.refresh(google.auth.transport.requests.Request())
            else:
                flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
                    client_secrets_file, scopes
                )
                credentials = flow.run_local_server()
            # Save the credentials for the next run
            with open(credentials_file, 'wb') as token:
                pickle.dump(credentials, token)

        self.youtube = googleapiclient.discovery.build(
            api_service_name, api_version, credentials=credentials, cache_discovery=False
        )

    def upload(
        self,
        video_path,
        title,
        description='',
        chunk_size=googleapiclient.http.DEFAULT_CHUNK_SIZE,
        *,
        max_retryable_errors=None,
        raise_errors=False,
    ):
        body = {
            'snippet': {
                'title': title, 'description': description
            }
        }

        insert_request = self.youtube.videos().insert(
            part=','.join(body.keys()),
            body=body,
            media_body=googleapiclient.http.MediaFileUpload(
                video_path, chunksize=chunk_size, resumable=True, mimetype='application/octet-stream'
            )
        )

        progress_bar = None
        last_progress = 0  # last known iteration, start at 0
        status = None
        response = None
        retryable_errors = 0
        while True:
            error = None
            retryable_exception = None
            try:
                status, response = insert_request.next_chunk()
            except googleapiclient.errors.HttpError as exception:
                if exception.resp.status in self.RETRYABLE_STATUS_CODES:
                    retryable_exception = exception
                    error = 'A retryable HTTP error {0} occurred:\n{1}'.format(
                        exception.resp.status, exception.content
                    )
                elif exception.resp.status == 403:
                    if raise_errors and not _is_quota_error(exception):
                        raise
                    return False
                else:
                    raise
            except self.RETRYABLE_EXCEPTIONS as exception:
                retryable_exception = exception
                error = 'A retryable error occurred: {}'.format(exception)

            if error is not None:
                retryable_errors += 1
                if max_retryable_errors is not None and retryable_errors > max_retryable_errors:
                    raise retryable_exception
                print(error)
                continue

            if status:
                if progress_bar is None:
                    progress_bar = tqdm.tqdm(
                        total=status.total_size, unit='B', unit_scale=True
                    )
                progress_bar.update(status.resumable_progress - last_progress)
                last_progress = status.resumable_progress

            if response and ('id' in response):
                if progress_bar is not None:
                    # todo: 100%???
                    progress_bar.close()
                return response['id']

    def update(self, video_id, title, description, category_id=None, *, raise_errors=False):
        try:
            self.youtube.videos().update(
                part='snippet',
                body={
                    'id': video_id,
                    'snippet': {
                        'title': title,
                        'description': description,
                        'categoryId': category_id if category_id else self.DEFAULT_CATEGORY_ID
                    }
                }
            ).execute()
        except (OSError, googleapiclient.errors.Error):
            if raise_errors:
                raise
            traceback.print_exc()
            return False

        return True

    def get_processing_status(self, video_id, *, raise_errors=False):
        try:
            response = self.youtube.videos().list(
                part='status', id=video_id
            ).execute()
        except (OSError, googleapiclient.errors.Error):
            if raise_errors:
                raise
            traceback.print_exc()
            return False

        if not response.get('items'):
            return {
                'upload_status': 'missing',
                'failure_reason': None,
                'rejection_reason': None,
            }

        status = response['items'][0].get('status', {})
        return {
            'upload_status': status.get('uploadStatus'),
            'failure_reason': status.get('failureReason'),
            'rejection_reason': status.get('rejectionReason'),
        }

    def check_processed(self, video_id, *, raise_errors=False):
        status = self.get_processing_status(video_id, raise_errors=raise_errors)
        if not status:
            return False

        return status['upload_status'] == 'processed'

    def insert_into_playlist(self, video_id, playlist_id, *, raise_errors=False):
        try:
            self.youtube.playlistItems().insert(
                part='snippet',
                body={
                    'snippet': {
                        'playlistId': playlist_id,
                        'resourceId': {
                            'kind': 'youtube#video',
                            'videoId': video_id
                        }
                    }
                }
            ).execute()
        except (OSError, googleapiclient.errors.Error):
            if raise_errors:
                raise
            traceback.print_exc()
            return False

        return True

    def list_captions(self, video_id):
        response = self.youtube.captions().list(
            part='snippet', videoId=video_id
        ).execute()

        return response.get('items', [])

    def caption_exists(self, video_id, caption_name='via_recorder_vtt'):
        return _caption_exists(
            self.list_captions(video_id), self.DEFAULT_CAPTION_LANGUAGE, caption_name
        )

    def playlist_contains(self, video_id, playlist_id):
        response = self.youtube.playlistItems().list(
            part='contentDetails',
            playlistId=playlist_id,
            videoId=video_id,
            maxResults=1,
        ).execute()
        return bool(response.get('items', []))

    def list_recent_uploads(self, max_results=50):
        channels_response = self.youtube.channels().list(
            part='contentDetails', mine=True
        ).execute()
        channels = channels_response.get('items', [])
        if not channels:
            return []

        uploads_playlist_id = (
            channels[0].get('contentDetails', {}).get('relatedPlaylists', {}).get('uploads')
        )
        if not uploads_playlist_id:
            return []

        uploads_response = self.youtube.playlistItems().list(
            part='snippet,contentDetails',
            playlistId=uploads_playlist_id,
            maxResults=max_results,
        ).execute()
        uploads = uploads_response.get('items', [])
        if not uploads:
            return []

        video_ids = [item['contentDetails']['videoId'] for item in uploads]
        videos_response = self.youtube.videos().list(
            part='contentDetails', id=','.join(video_ids), maxResults=50
        ).execute()
        durations = {
            item['id']: _youtube_duration_seconds(item['contentDetails']['duration'])
            for item in videos_response.get('items', [])
        }

        return [
            {
                'video_id': item['contentDetails']['videoId'],
                'title': item['snippet']['title'],
                'published_at': item['snippet']['publishedAt'],
                'duration_seconds': durations.get(item['contentDetails']['videoId']),
            }
            for item in uploads
        ]

    def add_caption_result(
        self, video_id, caption_path, caption_name='via_recorder', *, raise_errors=False
    ):
        try:
            self.youtube.captions().insert(
                part='snippet',
                body={
                    'snippet': {
                        'language': self.DEFAULT_CAPTION_LANGUAGE,
                        'name': caption_name,
                        'videoId': video_id
                    }
                },
                media_body=googleapiclient.http.MediaFileUpload(caption_path)
            ).execute()
        except googleapiclient.errors.HttpError as exception:
            if _is_quota_error(exception):
                print(
                    f'quota_exceeded: {caption_path} -> {video_id} (YouTube API quota exceeded)',
                    file=sys.stderr
                )
                return CAPTION_UPLOAD_QUOTA_EXCEEDED

            if raise_errors:
                raise
            traceback.print_exc()
            return CAPTION_UPLOAD_FAILED
        except (OSError, googleapiclient.errors.Error):
            if raise_errors:
                raise
            traceback.print_exc()
            return CAPTION_UPLOAD_FAILED

        return CAPTION_UPLOAD_SUCCESS

    def add_caption(self, video_id, caption_path, caption_name='via_recorder'):
        return self.add_caption_result(video_id, caption_path, caption_name) == CAPTION_UPLOAD_SUCCESS


if __name__ == '__main__':
    import fire


    def add_caption_and_delete(video_id, caption_path):
        youtube = Youtube(recorder.config.get('youtube'))
        if youtube.add_caption(video_id, caption_path):
            print('The caption has been added to YouTube and removed from the local file')
            os.unlink(caption_path)


    fire.Fire({
        'add_caption_and_delete': add_caption_and_delete,
        'upload_missing_captions': upload_missing_captions,
    })
