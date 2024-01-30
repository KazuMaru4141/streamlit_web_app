import streamlit as st
from PIL import Image
from streamlit_autorefresh import st_autorefresh

import spotipy
import spotipy.util as util
from spotipy.oauth2 import SpotifyClientCredentials
from spotipy.oauth2 import SpotifyOAuth

import datetime


#Spotify Authorization
MY_USER_NAME = "kazmaru"
MY_ID = '38537f7c27b84471b27a018c58a582b5'
MY_SECRET = '8aea8e2036ab4e78a8d10f6cab425a18'
REDIRECT_URI = 'http://localhost:8888/callback'

def create_spotify():
    SCOPE = 'user-library-read user-read-playback-state playlist-read-private user-read-recently-played playlist-read-collaborative playlist-modify-public playlist-modify-private'
    
    auth_manager = SpotifyOAuth(
    scope=SCOPE,
    username=MY_USER_NAME,
    redirect_uri=REDIRECT_URI,
    client_id=MY_ID,
    client_secret=MY_SECRET)

    spotify = spotipy.Spotify(auth_manager=auth_manager)

    return auth_manager, spotify

auth_manager, spotify = create_spotify()

st.title('Currently Playing Track')
col1, col2 = st.columns(2)

currentTrack = spotify.current_user_playing_track()

if currentTrack != None:
    trackName = currentTrack["item"]["name"]



    artistName = currentTrack["item"]["artists"][0]["name"]
    artistID = currentTrack["item"]["artists"][0]["id"]
    albumName = currentTrack["item"]["album"]["name"]
    albumID = currentTrack["item"]["album"]["id"]
    albumURL = currentTrack["item"]["album"]["external_urls"]["spotify"]
    releaseDate = currentTrack["item"]["album"]["release_date"]
    albumImg = currentTrack["item"]["album"]["images"][0]["url"]

    artistInfo = spotify.artist(artistID)
    relatedArtists = spotify.artist_related_artists(artistID)

    related = []
    for artist in relatedArtists["artists"]:
        related.append(artist["name"])
    
    with col1:
        st.image(albumImg, width=200)
    
    with col2:
        st.text(f'■ Album Name : {albumName}')
        st.text(f'■ Artist Name : {artistName}')
        st.text(f'■ Track Name : {trackName}')
        st.text(f'■ Release Date : {releaseDate}')
    
    st.text(f'{albumURL}')
    albumURL
    if artistInfo["genres"] != []:
        st.text(f'■ Genre : {", ".join(artistInfo["genres"])}')
    else:
        st.text(f'■ Genre : -')
    st.text(f'■ Related Artists')
    count = 0
    output = []
    for at in related:
        if count <= 3:
            output.append(at)
            count = count + 1
                            
        if count >= 3:
            st.text(f'{", ".join(output)}')
            output = []
            count = 0        
        
    
else:
    st.text(f'Track is not playing')

# update every 5sec
st_autorefresh(interval=15000, key="dataframerefresh")



##with st.form(key='prifile_form'):
#    like_btn = st.form_submit_button('Like')
#    dislike_btn = st.form_submit_button('Dislike')

#    if like_btn == True:
#        print("like!")
        
#    if dislike_btn == True:
#        print("Dislike!")
#"""
