import streamlit as st
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from functions import search_song_api, get_audio_features

# Load the existing DataFrame with track data
df = pd.read_csv('full_song_data.csv')

# Prepare the data for KMeans clustering
# We'll use only the relevant audio features for clustering
audio_features = df[['acousticness', 'danceability', 'energy', 'instrumentalness', 'key',
                     'liveness', 'loudness', 'mode', 'speechiness', 'tempo', 'time_signature', 'valence']]

# Scale the data to have mean=0 and variance=1
scaler = StandardScaler()
scaled_audio_features = scaler.fit_transform(audio_features)

def generate_recommendations(selected_song, kmeans_model):
    cluster_labels = kmeans_model.fit_predict(scaled_audio_features)

    selected_song_choice = f"{selected_song['track_name']} - {selected_song['artist']}"
    selected_song_index = [result['track_name'] + " - " + result['artist'] for result in st.session_state.search_results].index(selected_song_choice)
    selected_song_cluster = cluster_labels[selected_song_index]

    hot_or_not = df[df['track_id'] == selected_song['track_id']]['hot_or_not'].values

    if len(hot_or_not) == 0:
        hot_or_not = 'not_hot'
    else:
        hot_or_not = hot_or_not[0]

    # Filter the DataFrame to get songs from the same cluster as the selected song and the same hot_or_not category
    recommended_songs = df[(cluster_labels == selected_song_cluster) & (df['hot_or_not'] == hot_or_not)].sample(5)
    return recommended_songs

def main():
    st.title("Song Recommender App")
    st.write("Enter a song title and artist to get started!")

    if 'search_results' not in st.session_state:
        st.session_state.search_results = []
        st.session_state.recommended_songs = []
        st.session_state.selected_song = None
        st.session_state.selected_kmeans = None

    song_title = st.text_input("Enter the song title:")
    artist_name = st.text_input("Enter the artist name:")

    if st.button("Search"):
        # Call the function to search for the song in the Spotify API
        search_results = search_song_api(song_title, artist_name)
        st.session_state.search_results = search_results

    if st.session_state.search_results:
        st.write("Select a song from the following list:")
        options_col1, options_col2 = st.columns(2)

        for idx, result in enumerate(st.session_state.search_results):
            track_info = f"{result['track_name']} - {result['artist']}"
            options_col = options_col1 if idx % 2 == 0 else options_col2
            with options_col:
                st.write(f"**{track_info}**")
                st.image(result['album_image'], use_column_width=True)
                st.write(f"**Album:** {result['album_name']}")
                st.write(f"**Release Date:** {result['album_release_year']}")
                st.write(f"**Duration:** {result['track_duration']}")  # Use 'track_duration' instead of 'track_duration_ms'
                st.write(f"**Spotify Link:** [Listen on Spotify]({result['track_link']})")

        selected_song_choice = st.selectbox("Choose a song:", [f"{result['track_name']} - {result['artist']}" for result in st.session_state.search_results])
        selected_song_index = [result['track_name'] + " - " + result['artist'] for result in st.session_state.search_results].index(selected_song_choice)
        st.session_state.selected_song = st.session_state.search_results[selected_song_index]

    if st.button("Generate Recommendations") and st.session_state.selected_song:
        selected_song = st.session_state.selected_song
        st.write("You selected:", selected_song['track_name'], "-", selected_song['artist'])

        # Ask the user to choose a KMeans model
        selected_kmeans = st.radio("Choose a KMeans model:", ['k=10', 'k=20'], key='kmeans_model')
        st.session_state.selected_kmeans = selected_kmeans

        if selected_kmeans == 'k=10':
            kmeans_model = KMeans(n_clusters=10, random_state=42)
        else:
            kmeans_model = KMeans(n_clusters=20, random_state=42)

        st.session_state.recommended_songs = generate_recommendations(selected_song, kmeans_model)

    if len(st.session_state.recommended_songs) > 0:
        st.write("Recommended Songs:")
        rec_col1, rec_col2 = st.columns(2)

        for idx, song in st.session_state.recommended_songs.iterrows():
            rec_col = rec_col1 if idx % 2 == 0 else rec_col2
            with rec_col:
                st.write(f"**{song['track_name']} - {song['artist']}**")
                st.image(song['album_image'], use_column_width=True)
                st.write(f"**Album:** {song['album_name']}")
                st.write(f"**Release Date:** {song['album_release_year']}")
                st.write(f"**Duration:** {song['track_duration']}")
                st.write(f"**Spotify Link:** [Listen on Spotify]({song['track_link']})")

    if st.button("Generate More Recommendations") and len(st.session_state.recommended_songs) > 0:
        recommended_songs = st.session_state.recommended_songs.sample(5)
        st.session_state.recommended_songs = recommended_songs

    if st.button("Reset"):
        st.session_state.search_results = []
        st.session_state.recommended_songs = []
        st.session_state.selected_song = None
        st.session_state.selected_kmeans = None

if __name__ == "__main__":
    main()
