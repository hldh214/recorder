import os
import pickle
import socket
import traceback

import google_auth_oauthlib.flow
import googleapiclient
import googleapiclient.http
import googleapiclient.discovery
import googleapiclient.errors
import google.auth.transport.requests
import tqdm

import recorder.utils


class Youtube:
    # Always retry when an googleapiclient.errors.HttpError with one of these status
    # codes is raised.
    RETRYABLE_STATUS_CODES = [500, 502, 503, 504]

    # Always retry when these exceptions are raised.
    RETRYABLE_EXCEPTIONS = (IOError, socket.timeout)

    DEFAULT_CAPTION_LANGUAGE = 'zh-Hans'

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
                credentials = flow.run_console()
            # Save the credentials for the next run
            with open(credentials_file, 'wb') as token:
                pickle.dump(credentials, token)

        self.youtube = googleapiclient.discovery.build(
            api_service_name, api_version, credentials=credentials
        )

    def upload(self, video_path, title, description='', chunk_size=googleapiclient.http.DEFAULT_CHUNK_SIZE):
        body = {
            'snippet': {
                'title': title, 'description': description
            }
        }

        insert_request = self.youtube.videos().insert(
            part=','.join(body.keys()),
            body=body,
            media_body=googleapiclient.http.MediaFileUpload(
                video_path, chunksize=chunk_size, resumable=True,
                mimetype='application/octet-stream'
            )
        )

        progress_bar = None
        last_progress = 0  # last known iteration, start at 0
        status = None
        response = None
        while True:
            error = None
            try:
                status, response = insert_request.next_chunk()
            except googleapiclient.errors.HttpError as exception:
                if exception.resp.status in self.RETRYABLE_STATUS_CODES:
                    error = 'A retryable HTTP error {0} occurred:\n{1}'.format(
                        exception.resp.status, exception.content
                    )
                elif exception.resp.status == 403:
                    return False
                else:
                    raise
            except self.RETRYABLE_EXCEPTIONS as exception:
                error = 'A retryable error occurred: {}'.format(exception)

            if error is not None:
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

    def check_processed(self, video_id):
        try:
            response = self.youtube.videos().list(
                part='status',
                id=video_id
            ).execute()
        except (OSError, googleapiclient.errors.Error):
            traceback.print_exc()
            return False

        if not response['items']:
            return False

        item = response['items'][0]

        upload_status = item['status']['uploadStatus']

        return upload_status == 'processed'

    def insert_into_playlist(self, video_id, playlist_id):
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
            traceback.print_exc()
            return False

        return True

    def add_caption(self, video_id, caption_path, caption_name='via_recorder'):
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
        except (OSError, googleapiclient.errors.Error):
            traceback.print_exc()
            return False

        return True


if __name__ == '__main__':
    import sys

    youtube = Youtube(recorder.utils.get_config().get('youtube'))

    if len(sys.argv) == 1:
        print('Usage: python3 youtube.py <video_id> <caption_path>')

    if len(sys.argv) == 2:
        print(youtube.check_processed(sys.argv[1]))

    if len(sys.argv) == 3:
        print(youtube.add_caption(sys.argv[1], sys.argv[2]))
