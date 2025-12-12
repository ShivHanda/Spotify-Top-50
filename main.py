import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import pandas as pd
from datetime import datetime
import os

# ==========================================
# 🛑 FORCE FIX: Proxy & Environment Cleaning
# ==========================================
# Ye lines kisi bhi ghalat internet setting ko delete kar dengi
if 'http_proxy' in os.environ: del os.environ['http_proxy']
if 'https_proxy' in os.environ: del os.environ['https_proxy']
if 'HTTP_PROXY' in os.environ: del os.environ['HTTP_PROXY']
if 'HTTPS_PROXY' in os.environ: del os.environ['HTTPS_PROXY']

# --- CONFIGURATION ---
# Secrets GitHub se uthayenge
CLIENT_ID = os.environ.get('SPOTIPY_CLIENT_ID')
CLIENT_SECRET = os.environ.get('SPOTIPY_CLIENT_SECRET')
PLAYLIST_ID = '37i9dQZEVXbMDoHDwVN2tF'
FILE_NAME = 'spotify_history.csv'

# --- MAIN LOGIC ---
try:
    auth_manager = SpotifyClientCredentials(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
    sp = spotipy.Spotify(auth_manager=auth_manager)

    print("Attempting to fetch playlist...")
    results = sp.playlist(PLAYLIST_ID)
    print("Playlist fetched successfully!")
    
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
        # Check if date exists
        if current_date not in old_df['Date'].values:
            final_df = pd.concat([old_df, new_df], ignore_index=True)
            final_df.to_csv(FILE_NAME, index=False)
            print(f"✅ Success! Updated data for {current_date}")
        else:
            print("⚠️ Data for today already exists. No changes made.")
    else:
        new_df.to_csv(FILE_NAME, index=False)
        print("✅ Success! Created new file.")

except Exception as e:
    print(f"❌ Error occurred: {e}")
    # Error ko fail karne ke liye raise karna zaroori hai taaki GitHub Red Cross dikhaye
    raise e
