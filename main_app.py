import streamlit as st
from PIL import Image

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



st.title('Get Twitter')

with st.form(key='prifile_form'):
    albumID = st.text_input('Album ID')
    submit_btn = st.form_submit_button('submit')
    
    if (submit_btn == True):
#        st.text(f'ID={albumID}')
        albumInfo = spotify.album(albumID)
        
        st.text(f'Album Name : {albumInfo["name"]}')
        st.text(f'Artist Name : {albumInfo["artists"][0]["name"]}')
        #st.text(f'Total tracks : {albumInfo["total_tracks"]}')
        st.text(f'Release Date : {albumInfo["release_date"]}')
        
#        st.text(f'Artist ID = {albumInfo["artists"][0]["id"]}')      
        artistInfo = spotify.artist(albumInfo["artists"][0]["id"])
        
        if artistInfo["genres"] != []:
            st.text(f'Genre : {", ".join(artistInfo["genres"])}')
        else:
            st.text(f'Genre : -')
        
        
        
        dt_now = dt_now = datetime.datetime.now()
        year = str(dt_now.year)
        st.text(f'')
        st.text(f'#NewAlbum_{year}')
        st.text(f'#WeeklyFeaturedAlbum')
        st.text(f'#今週良さそう')
        st.text(f'#新譜')
        st.text(f'{albumInfo["external_urls"]["spotify"]}')
        
        
        
        
        
        
        
