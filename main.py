import os
import sys
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import pandas as pd
from datetime import datetime

# --- Configuration ---
# Spotipy automatically looks for SPOTIPY_CLIENT_ID and SPOTIPY_CLIENT_SECRET 
# in your environment variables, so we don't even need to pass them explicitly.

PLAYLIST_ID = '37i9dQZEVXbMDoHDwVN2tF'  # Global Top 50
OUTPUT_FILE = 'spotify_history.csv'

def main():
    print("--- Starting Spotify Archiver (Spotipy Version) ---")

    # 1. Authenticate
    # This single line handles the entire auth flow
    try:
        auth_manager = SpotifyClientCredentials()
        sp = spotipy.Spotify(auth_manager=auth_manager)
    except Exception as e:
        print(f"Authentication Error: {e}")
        sys.exit(1)

    # 2. Fetch Playlist Data
    try:
        # We use playlist_tracks to get just the tracks pagination object
        # limit=50 ensures we get the top 50
        results = sp.playlist_tracks(PLAYLIST_ID, limit=50)
    except Exception as e:
        print(f"API Fetch Error: {e}")
        sys.exit(1)

    # 3. Process Data
    tracks_list = []
    today_date = datetime.now().strftime('%Y-%m-%d')
    
    if 'items' not in results:
        print("Error: No items found in playlist.")
        sys.exit(1)

    for idx, item in enumerate(results['items']):
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
    
    # 4. Save to CSV
    new_df = pd.DataFrame(tracks_list)
    
    if os.path.exists(OUTPUT_FILE):
        try:
            existing_df = pd.read_csv(OUTPUT_FILE)
            
            # Check if today's date is already there
            if today_date in existing_df['Date'].astype(str).values:
                print(f"Skipping: Data for {today_date} already exists.")
            else:
                new_df.to_csv(OUTPUT_FILE, mode='a', header=False, index=False)
                print(f"Success: Appended {len(new_df)} rows for {today_date}.")
        except Exception as e:
            print(f"Error updating CSV: {e}")
            sys.exit(1)
    else:
        new_df.to_csv(OUTPUT_FILE, mode='w', header=True, index=False)
        print(f"Success: Created {OUTPUT_FILE} with {len(new_df)} rows.")

    print("--- Process Completed ---")

if __name__ == "__main__":
    main()
