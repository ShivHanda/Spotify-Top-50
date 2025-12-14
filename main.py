import os
import sys
import requests
import pandas as pd
from datetime import datetime
import base64
from bs4 import BeautifulSoup

# --- Configuration ---
CLIENT_ID = os.environ.get('SPOTIPY_CLIENT_ID')
CLIENT_SECRET = os.environ.get('SPOTIPY_CLIENT_SECRET')
CSV_FILE = 'spotify_history.csv'

def get_access_token():
    """Spotify se Login Token leta hai (Client Credentials Flow)."""
    auth_url = 'https://accounts.spotify.com/api/token'
    auth_str = f"{CLIENT_ID}:{CLIENT_SECRET}"
    b64_auth_str = base64.b64encode(auth_str.encode()).decode()
    
    headers = {
        'Authorization': f'Basic {b64_auth_str}',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    data = {'grant_type': 'client_credentials'}
    
    try:
        response = requests.post(auth_url, headers=headers, data=data)
        response.raise_for_status()
        return response.json()['access_token']
    except Exception as e:
        print(f"Error extracting token: {e}")
        sys.exit(1)

def scrape_top_50_ids():
    """
    Kworb.net se Global Top 50 songs ki Spotify IDs churata hai.
    Kyunki Spotify API ne direct playlist access block kar diya hai.
    """
    url = "https://kworb.net/spotify/country/global_daily.html"
    print(f"Scraping Top 50 IDs from {url}...")
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        track_ids = []
        rows = soup.select('table.sortable tbody tr')
        
        for row in rows[:50]: # Sirf Top 50 chahiye
            link_tag = row.find('a', href=True)
            # URL structure: .../track/TRACK_ID.html
            if link_tag and '/track/' in link_tag['href']:
                full_href = link_tag['href']
                track_id = full_href.split('/track/')[1].replace('.html', '')
                track_ids.append(track_id)
        
        if not track_ids:
            raise Exception("Kworb se IDs nahi mili. Structure change ho gaya hoga.")
            
        print(f"Successfully scraped {len(track_ids)} track IDs.")
        return track_ids
        
    except Exception as e:
        print(f"Error scraping Kworb: {e}")
        sys.exit(1)

def get_tracks_metadata(token, track_ids):
    """
    In IDs ke liye Spotify se official details mangta hai.
    Ye endpoint (v1/tracks) allowed hai.
    """
    ids_string = ",".join(track_ids)
    url = f"https://api.spotify.com/v1/tracks?ids={ids_string}"
    headers = {'Authorization': f'Bearer {token}'}
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()['tracks']
    except Exception as e:
        print(f"Error fetching track details: {e}")
        sys.exit(1)

def process_data():
    if not CLIENT_ID or not CLIENT_SECRET:
        print("Error: Secrets missing. Github Settings check karein.")
        sys.exit(1)

    # 1. Scrape IDs (Jugaad to bypass Ban)
    track_ids = scrape_top_50_ids()

    # 2. Login
    print("Authenticating with Spotify...")
    token = get_access_token()
    
    # 3. Get Details
    print("Fetching metadata for tracks...")
    tracks_data = get_tracks_metadata(token, track_ids)
    
    today_date = datetime.now().strftime('%Y-%m-%d')
    extracted_data = []

    for idx, track in enumerate(tracks_data):
        if not track:
            continue
            
        # Artists ke naam combine karna
        artists = ", ".join([artist['name'] for artist in track.get('artists', [])])
        
        # Album Cover URL
        album_images = track.get('album', {}).get('images', [])
        cover_url = album_images[0]['url'] if album_images else None

        row = {
            'Date': today_date,
            'Position': idx + 1,
            'Song': track.get('name'),
            'Artist': artists,
            'Popularity': track.get('popularity'),
            'Duration_MS': track.get('duration_ms'),
            'Album_Type': track.get('album', {}).get('album_type'),
            'Total_Tracks': track.get('album', {}).get('total_tracks'),
            'Release_Date': track.get('album', {}).get('release_date'),
            'Is_Explicit': track.get('explicit'),
            'Album_Cover_URL': cover_url
        }
        extracted_data.append(row)

    new_df = pd.DataFrame(extracted_data)

    # 4. Save Logic (Duplicate Check)
    if os.path.exists(CSV_FILE):
        try:
            existing_df = pd.read_csv(CSV_FILE)
            if today_date in existing_df['Date'].values:
                print(f"Aaj ({today_date}) ka data pehle se hai. Kuch nahi kiya.")
                sys.exit(0)
            
            updated_df = pd.concat([existing_df, new_df], ignore_index=True)
            updated_df.to_csv(CSV_FILE, index=False)
            print(f"Data appended for {today_date}.")
        except pd.errors.EmptyDataError:
            new_df.to_csv(CSV_FILE, index=False)
            print("File khali thi, naya data dala.")
    else:
        new_df.to_csv(CSV_FILE, index=False)
        print(f"Nayi file banayi: {CSV_FILE}")

if __name__ == "__main__":
    process_data()
