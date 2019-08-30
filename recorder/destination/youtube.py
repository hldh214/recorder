import os
import pathlib
import pickle

import google_auth_oauthlib.flow
import googleapiclient.discovery
import google.auth.transport.requests
import toml


class Youtube:
    def __init__(self, config_path):
        config = toml.load(config_path)

        scopes = [
            'https://www.googleapis.com/auth/youtube.readonly',
            'https://www.googleapis.com/auth/youtube.upload'
        ]
        api_service_name = 'youtube'
        api_version = 'v3'
        client_secrets_file = config['youtube']['client_secrets_file']
        credentials_file = config['youtube']['credentials_file']

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

    def upload(self):
        pass

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
    youtube = Youtube(os.path.join(
        pathlib.Path(os.path.abspath(__file__)).parent.parent.parent, 'config.toml'
    ))
    print(youtube.check_uploaded('EkYec3Vwico'))
