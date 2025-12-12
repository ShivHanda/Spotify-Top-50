import os
import sys
import base64
import requests
import pandas as pd
from datetime import datetime

# --- Configuration & Constants ---
CLIENT_ID = os.getenv('SPOTIPY_CLIENT_ID')
CLIENT_SECRET = os.getenv('SPOTIPY_CLIENT_SECRET')
PLAYLIST_ID = '37i9dQZEVXbMDoHDwVN2tF'  # Global Top 50
OUTPUT_FILE = 'spotify_history.csv'

# Official Spotify Endpoints
AUTH_URL = 'https://accounts.spotify.com/api/token'
API_BASE_URL = 'https://api.spotify.com/v1/playlists/'

def get_access_token():
    """Authenticates with Spotify using Client Credentials Flow."""
    if not CLIENT_ID or not CLIENT_SECRET:
        print("Error: Environment variables SPOTIPY_CLIENT_ID or SPOTIPY_CLIENT_SECRET are missing.")
        sys.exit(1)

    # Encode Client ID and Secret
    auth_str = f'{CLIENT_ID}:{CLIENT_SECRET}'
    b64_auth_str = base64.b64encode(auth_str.encode()).decode()

    headers = {
        'Authorization': f'Basic {b64_auth_str}',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    data = {'grant_type': 'client_credentials'}

    try:
        response = requests.post(AUTH_URL, headers=headers, data=data)
        response.raise_for_status()
        return response.json()['access_token']
    except requests.exceptions.RequestException as e:
        print(f"Authentication Failed: {e}")
        sys.exit(1)

def fetch_playlist_data(token):
    """Fetches tracks from the specific playlist."""
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    # We ask for specific fields to optimize the payload
    url = f"{API_BASE_URL}{PLAYLIST_ID}"
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"API Request Failed: {e}")
        sys.exit(1)

def process_data(data):
    """Extracts required columns from the JSON response."""
    tracks_list = []
    today_date = datetime.now().strftime('%Y-%m-%d')
    
    # Check if 'tracks' and 'items' exist
    if 'tracks' not in data or 'items' not in data['tracks']:
        print("Error: Unexpected JSON structure.")
        sys.exit(1)

    for idx, item in enumerate(data['tracks']['items']):
        track = item.get('track')
        if not track:
            continue
            
        # Extract Artists (comma separated)
        artists = ", ".join([artist['name'] for artist in track.get('artists', [])])
        
        # Safe extraction of nested dictionary fields
        album = track.get('album', {})
        images = album.get('images', [])
        cover_url = images[0]['url'] if images else None

        track_data = {
            'Date': today_date,
            'Position': idx + 1,
            'Song': track.get('name'),
            'Artist': artists,
            'Popularity': track.get('popularity'),
            'Duration_MS': track.get('duration_ms'),
            'Album_Type': album.get('album_type'),
            'Total_Tracks': album.get('total_tracks'),
            'Release_Date': album.get('release_date'),
            'Is_Explicit': track.get('explicit'),
            'Album_Cover_URL': cover_url
        }
        tracks_list.append(track_data)
        
    return pd.DataFrame(tracks_list)

def update_csv(new_df):
    """Updates the CSV file, preventing duplicate dates."""
    today_date = datetime.now().strftime('%Y-%m-%d')

    if os.path.exists(OUTPUT_FILE):
        try:
            # Check existing dates without loading the whole file if possible, 
            # but for safety/simplicity with pandas we load headers or unique dates.
            # Here we load the file to ensure schema consistency.
            existing_df = pd.read_csv(OUTPUT_FILE)
            
            # Check if today's date already exists
            if today_date in existing_df['Date'].astype(str).values:
                print(f"Skipping: Data for {today_date} already exists in {OUTPUT_FILE}.")
                return
            else:
                # Append without writing header
                new_df.to_csv(OUTPUT_FILE, mode='a', header=False, index=False)
                print(f"Success: Appended {len(new_df)} rows for {today_date}.")
        except Exception as e:
            print(f"Error reading/writing CSV: {e}")
            sys.exit(1)
    else:
        # Create new file with headers
        new_df.to_csv(OUTPUT_FILE, mode='w', header=True, index=False)
        print(f"Success: Created {OUTPUT_FILE} with {len(new_df)} rows for {today_date}.")

def main():
    print("--- Starting Spotify Archiver ---")
    
    # 1. Authenticate
    token = get_access_token()
    
    # 2. Fetch Data
    raw_data = fetch_playlist_data(token)
    
    # 3. Process Data
    df = process_data(raw_data)
    
    # 4. Save to CSV
    update_csv(df)
    
    print("--- Process Completed Successfully ---")

if __name__ == "__main__":
    main()
