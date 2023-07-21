import spotipy
import json
import pandas as pd
import requests
import re
from bs4 import BeautifulSoup
from credentials import *
import pprint
from spotipy.oauth2 import SpotifyClientCredentials
from IPython.display import clear_output
import random
import time
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score


def convert_ms_to_min_sec(milliseconds):
    seconds = int(milliseconds / 1000)
    minutes = seconds // 60
    seconds %= 60
    return f"{minutes:02d}:{seconds:02d}"



def search_song_api(Title: str, Artist: str):
    
    """
    Gets a tuple (Title, Artist) and retrieves it will retrieve a list of possible songs, from the Spotify API for the user to choose from.
    Then will give us its ID. 
    If the Song isn't in the API, it will remove the song from the databases, printing an empty string as ID.
    
    Args:
    
    Title, Artist = Tuple
    
    Returns:
    
    A list of dictionaries to the user to choose from, and to the program an ID to use later
    """
    
    
    # searching info from API
    sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=client_id, client_secret=client_secret))

    query = ("track:"+Title if Title != "" else "")+" "+("artist:"+Artist if Artist != "" else "")
    
    if len(query) > 0:
        try:
            raw_results = sp.search(q=query,type="track,artist",limit=5)
            raw_results = raw_results['tracks']['items'] 
        except Exception as e:
            print("Error:", e)
    else:
        raw_results = []
        
    results = []  
    
    for index, item in enumerate(raw_results):
        duration = convert_ms_to_min_sec(item['duration_ms'])
        results.append({'track_id': item['id'],
                        'href': item['href'],
                        'track_link': item['external_urls']['spotify'],
                        'track_name': item['name'],
                        'artist': item['album']['artists'][0]['name'],
                        'album_name': item['album']['name'],
                        'album_release_year': item['album']['release_date'],
                        'track_duration': duration,
                        'album_image': item['album']['images'][1]['url']})
        
    return results



def get_song_data(df: pd.DataFrame) -> pd.DataFrame:
    '''
    Given a DataFrame with three columns: title and artist and hot_or_not,
    this function returns a new df with track data 
    using Spotipy, Spotify's API.
    
    Input:
    df: pandas DataFrame with songs
    
    Output:
    DataFrame with the track data
    
    '''
    
    # Define loop pauses to avoid API server blockage by overflow
    sleep_time = 15 # seconds of sleep time
    loop_count = 100 # tracks per sleep loop
    
    # Define an empty array to append results
    sp_songs = []
    
    loop_counter = 0 # counter to track loop
    counter = 0 # counter to track progress
    fail_counter = 0 # counter to track failed matches
                 
    for index, row in df.iterrows():
        
        counter += 1 # Add one to the global song counter
        
        # Clear last print and print next progress
        clear_output(wait=True)
        print('Downloading song Data...', round(((index + 1) / df.shape[0])*100), '%')
        
        # Get the current row song title and artist. Fix to maximum 30 chars to avoid API error.
        song_name = str(row['Title'])[:30]
        artist_name = str(row['Artist'])[:30]
        
        try:
            sp_data = search_song_api(song_name, artist_name) # Call search_song function to get data
            if len(sp_data) > 0:
                sp_songs.append(sp_data[0]) # If there is data, append to global variable
            else:
                fail_counter += 1 # If there is no data, add 1 to fail_counter
        except Exception as e:
            # Log error and add counter
            print("Error:", e)
            fail_counter += 1
        
        # Sleep to avoid API overflow...
        loop_counter += 1
        if loop_counter >= loop_count:
            loop_counter = 0
            # Generate a random sleep timer based on sleep_time
            random_sleep_timer = random.randint(int(sleep_time*0.5), int(sleep_time*1.5))
            print('Sleeping for', random_sleep_timer, 's...') # Print sleep time
            time.sleep(random_sleep_timer) # Sleep -> pause download to simulate human behavior

    # Print download summary
    clear_output(wait=True)
    print("Song data download complete.", "Success rate:", round(((counter-fail_counter)/counter)*100), "%")
    print("Succesful downloads:",counter-fail_counter,"Failed downloads:",fail_counter)
    
    # Convert list of dictionaries to DataFrame
    sp_songs = pd.DataFrame(sp_songs)
    
    # Drop result_index column: used for single songs searches in search_song() function
    #sp_songs.drop(inplace=True, columns='result_index')
    
    return sp_songs


# Create a function to search a given single song in the Spotify API: search_song(title, artist).

def get_audio_features(track_ids: list) -> pd.DataFrame:
    '''
    Given a list of track IDs, this function returns 
    track audio features such as danceability, energy or tempo
    using Spotipy, Spotify's API.
    
    Input:
    track_ids: list of Spotipy track_ids
    
    Output:
    DataFrame with the track_ids and audio features
    
    '''
    
    # Define loop pauses to avoid API server blockage by overflow
    sleep_time = 20 # seconds of sleep time
    loop_count = 100 # tracks per sleep loop
    
    # Initialize SpotiPy with user credentias
    sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=client_id,
                                                           client_secret=client_secret))

    # Define result variable
    clean_results = []
    
    loop_counter = 0 # counter to track loop
    counter = 0 # counter to track progress
    fail_counter = 0 # counter to track failed matches
    
    # Loop through track_ids to get relevant audio features
    for index, track_id in enumerate(track_ids):
        
        counter += 1 # Add 1 to global counter
        clear_output(wait=True) # Clear print output to update progress
        print('Downloading audio features...', round(((index + 1) / len(track_ids))*100), '%') # Print progress
        
        try:
            # Get audio features from Spotipy
            api_result = sp.audio_features(track_id)[0]
            
            # Add features to track variable
            track = {'track_id': track_id,
                     'acousticness': api_result['acousticness'],
                     'danceability': api_result['danceability'],
                     'energy': api_result['energy'],
                     'instrumentalness': api_result['instrumentalness'],
                     'key': api_result['key'],
                     'liveness': api_result['liveness'],
                     'loudness': api_result['loudness'],
                     'mode': api_result['mode'],
                     'speechiness': api_result['speechiness'],
                     'tempo': api_result['tempo'],
                     'time_signature': api_result['time_signature'],
                     'valence': api_result['valence'],
            }
            
            # Append track results to results list
            clean_results.append(track)
            
        except Exception as e:
            # If there is an error:
            print("Error:", e)
            fail_counter += 1
        
        # Sleep to avoid API overflow...
        loop_counter += 1
        if loop_counter >= loop_count:
            loop_counter = 0
            # Generate a random sleep timer based on sleep_time
            random_sleep_timer = random.randint(int(sleep_time*0.5), int(sleep_time*1.5))
            print('Sleeping for', random_sleep_timer, 's...')
            time.sleep(random_sleep_timer) # Sleep
            
    
    clear_output(wait=True)
    print("Audio features download complete.", "Success rate:", round(((counter-fail_counter)/counter)*100), "%")
    print("Succesful downloads:",counter-fail_counter,"Failed downloads:",fail_counter)
    
    # Convert list of dictionaries to DataFrame
    clean_results = pd.DataFrame(clean_results)

    return clean_results




if __name__ == "__main__":
    main()