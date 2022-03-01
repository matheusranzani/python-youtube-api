import os
import pickle
import isodate
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

credentials = None

if os.path.exists('token.pickle'):
    print('Loading credentials from file...')
    with open('token.pickle', "rb") as token:
        credentials = pickle.load(token)

if not credentials or not credentials.valid:
    if credentials and credentials.expired and credentials.refresh_token:
        print('Refreshing access token...') 
        credentials.refresh(Request())
    else:
        print('Fetching new tokens')
        
        flow = InstalledAppFlow.from_client_secrets_file(
            'client_secrets.json',
            scopes=['https://www.googleapis.com/auth/youtube']
        )

        flow.run_local_server(port=8080, prompt='consent', authorization_prompt_message='')
        credentials = flow.credentials

        with open('token.pickle', 'wb') as f:
            print('Saving credentials for future use...')
            pickle.dump(credentials, f)

youtube = build('youtube', 'v3', credentials=credentials)

playlistRequest = youtube.playlistItems().list(
    part='contentDetails',
    playlistId='PLCOFU1_NJkY-CBLpP8YHl2j47OAvin_cC',
    maxResults=200
)

playlistResponse = playlistRequest.execute()

videoIdList = []

for item in playlistResponse['items']:
    videoIdList.append(item['contentDetails']['videoId'])

videoRequest = youtube.videos().list(
    part='contentDetails',
    id=videoIdList
)

videoResponse = videoRequest.execute()

videoDurationList = []

for item in videoResponse['items']:
    videoDurationList.append(isodate.parse_duration(item['contentDetails']['duration']).total_seconds())

playlistTotalSeconds = sum(videoDurationList)

output = ''

if playlistTotalSeconds < 60:
    output = f'The playlist lasts {int(playlistTotalSeconds)} seconds'
else:
    playlistSeconds = playlistTotalSeconds % 60

    if playlistTotalSeconds < 3600:
        playlistMinutes = playlistTotalSeconds // 60
        output = f'The playlist lasts {int(playlistMinutes)} minutues {int(playlistSeconds)} seconds'
    else:
        playlistHours = playlistTotalSeconds // (60 * 60);
        playlistMinutes = (playlistTotalSeconds // 60) % 60 
        output = f'The playlist lasts {int(playlistHours)} hours {int(playlistMinutes)} minutes {int(playlistSeconds)} seconds'

print(output)

youtube.close()
