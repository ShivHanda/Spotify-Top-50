import requests
import pandas as pd
from datetime import datetime
import os
import base64

# ==========================================
# 🛡️ ROBUST SETUP: Official Spotify Endpoints
# ==========================================

CLIENT_ID = os.environ.get('SPOTIPY_CLIENT_ID')
CLIENT_SECRET = os.environ.get('SPOTIPY_CLIENT_SECRET')
PLAYLIST_ID = '37i9dQZEVXbMDoHDwVN2tF'
FILE_NAME = 'spotify_history.csv'

def get_access_token(client_id, client_secret):
    """Spotify se Official Token maangne ka function"""
    # ⬇️ CORRECT URL: Ye Spotify ka asli darwaza hai
    auth_url = 'https://accounts.spotify.com/api/token'
    
    auth_header = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
    headers = {'Authorization': f'Basic {auth_header}'}
    data = {'grant_type': 'client_credentials'}
    
    response = requests.post(auth_url, headers=headers, data=data)
    
    if response.status_code != 200:
        raise Exception(f"❌ Auth Failed! Status: {response.status_code}, Msg: {response.text}")
    
    return response.json()['access_token']

def get_playlist_data(token, playlist_id):
    """Playlist fetch karne ka function"""
    # ⬇️ CORRECT URL: Ye API ka asli address hai
    api_url = f'https://api.spotify.com/v1/playlists/{playlist_id}'
    
    headers = {'Authorization': f'Bearer {token}'}
    
    response = requests.get(api_url, headers=headers)
    
    if response.status_code != 200:
        raise Exception(f"❌ Playlist Fetch Failed! Status: {response.status_code}, Msg: {response.text}")
        
    return response.json()

# --- MAIN EXECUTION ---
try:
    print("🚀 Starting Connection to OFFICIAL Spotify API...")
    
    # Step 1: Get Token
    token = get_access_token(CLIENT_ID, CLIENT_SECRET)
    print("✅ Authentication Successful!")
    
    # Step 2: Get Data
    data = get_playlist_data(token, PLAYLIST_ID)
    print("✅ Playlist Data Received!")
    
    tracks = data['tracks']['items']
    current_date = datetime.now().strftime("%Y-%m-%d")

    data_list = []
    for i, item in enumerate(tracks):
        track = item['track']
        # Safe extraction handles missing images/albums
        album_img = track['album']['images'][0]['url'] if track['album']['images'] else ""
        
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
            'Album_Cover_URL': album_img
        }
        data_list.append(row)

    # Step 3: Save Data
    new_df = pd.DataFrame(data_list)

    if os.path.exists(FILE_NAME):
        old_df = pd.read_csv(FILE_NAME)
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
    print(f"❌ CRITICAL ERROR: {e}")
    raise e
