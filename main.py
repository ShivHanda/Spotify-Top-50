import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import pandas as pd
from datetime import datetime
import os

# Secrets (Ye hum GitHub Settings me dalenge)
CLIENT_ID = os.environ.get('SPOTIPY_CLIENT_ID')
CLIENT_SECRET = os.environ.get('SPOTIPY_CLIENT_SECRET')
PLAYLIST_ID = '37i9dQZEVXbMDoHDwVN2tF'
FILE_NAME = 'spotify_history.csv' # Simple filename, no C:/ path

auth_manager = SpotifyClientCredentials(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
sp = spotipy.Spotify(auth_manager=auth_manager)

results = sp.playlist(PLAYLIST_ID)
tracks = results['tracks']['items']
current_date = datetime.now().strftime("%Y-%m-%d")

data_list = []
for i, item in enumerate(tracks):
    track = item['track']
    row = {
        'Date': current_date,
        'Position': i + 1,
        'Song': track['name'],
        'Artist': ", ".join([artist['name'] for artist in track['artists']]),
        'Popularity': track['popularity'],
        'Duration_MS': track['duration_ms'],
        'Album_Type': track['album']['album_type'],
        'Total_Tracks': track['album']['total_tracks'],
        'Release_Date': track['album']['release_date'],
        'Is_Explicit': track['explicit'],
        'Album_Cover_URL': track['album']['images'][0]['url'] if track['album']['images'] else ""
    }
    data_list.append(row)

new_df = pd.DataFrame(data_list)

if os.path.exists(FILE_NAME):
    old_df = pd.read_csv(FILE_NAME)
    if current_date not in old_df['Date'].values:
        final_df = pd.concat([old_df, new_df], ignore_index=True)
        final_df.to_csv(FILE_NAME, index=False)
        print(f"Updated data for {current_date}")
    else:
        print("Data already exists.")
else:
    new_df.to_csv(FILE_NAME, index=False)
    print("Created new file.")
