import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import pandas as pd
from datetime import datetime
import os

# --- DEBUGGING START ---
# Ye check karega ki Secrets sahi load ho rahe hain ya nahi
client_id = os.environ.get('SPOTIPY_CLIENT_ID', '')
client_secret = os.environ.get('SPOTIPY_CLIENT_SECRET', '')

print(f"DEBUG CHECK:")
print(f"PLAYLIST_ID used: '37i9dQZEVXbMDoHDwVN2tF'")
print(f"Client ID Length: {len(client_id)} (Should be 32)")
print(f"Client Secret Length: {len(client_secret)} (Should be 32)")

if len(client_id) > 32:
    print("❌ ERROR: Client ID me koi lamba Link/Text paste ho gaya hai!")
if 'http' in client_id or 'http' in client_secret:
    print("❌ ERROR: Secrets me 'http' link detect hua hai. Please remove it.")
# --- DEBUGGING END ---

# Original Logic
CLIENT_ID = client_id
CLIENT_SECRET = client_secret
PLAYLIST_ID = '37i9dQZEVXbMDoHDwVN2tF'
FILE_NAME = 'spotify_history.csv'

auth_manager = SpotifyClientCredentials(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
sp = spotipy.Spotify(auth_manager=auth_manager)

# Baki code same rahega...
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
