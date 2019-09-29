import os
import pathlib
import pickle
import socket

import apiclient
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
import google.auth.transport.requests
import toml
import tqdm


class Youtube:
    # Always retry when an apiclient.errors.HttpError with one of these status
    # codes is raised.
    RETRYABLE_STATUS_CODES = [500, 502, 503, 504]

    # Always retry when these exceptions are raised.
    RETRYABLE_EXCEPTIONS = (IOError, socket.timeout)

    def __init__(self, config):
        scopes = [
            'https://www.googleapis.com/auth/youtube.readonly',
            'https://www.googleapis.com/auth/youtube.upload'
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

    def upload(
            self, video_path, title, description='',
            chunk_size=4 * 1024 * 1024
    ):
        body = {
            'snippet': {
                'title': title, 'description': description
            }
        }

        insert_request = self.youtube.videos().insert(
            part=','.join(body.keys()),
            body=body,
            media_body=apiclient.http.MediaFileUpload(
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
                    progress_bar.close()
                return response['id']

    def check_uploaded(self, video_id):
        response = self.youtube.videos().list(
            part='processingDetails',
            id=video_id
        ).execute()

        if not response['items']:
            return False

        item = response['items'][0]

        processing_status = item['processingDetails']['processingStatus']

        if processing_status == 'succeeded':
            return True

        return False


if __name__ == '__main__':
    youtube = Youtube(toml.load(os.path.join(
        pathlib.Path(os.path.abspath(__file__)).parent.parent.parent, 'config.toml'
    )))
    print(youtube.check_uploaded('EkYec3Vwico'))
