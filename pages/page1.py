import streamlit as st
from PIL import Image
from streamlit_autorefresh import st_autorefresh

import spotipy
import spotipy.util as util
from spotipy.oauth2 import SpotifyClientCredentials
from spotipy.oauth2 import SpotifyOAuth

from SpotifyAPI import SpotifyCtrl

import datetime

sp = SpotifyCtrl
auth_manager, spotify = sp.create_spotify()

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
        appendList = [artist["name"], artist["external_urls"]["spotify"]]
        related.append(appendList)
    
    with col1:
        st.image(albumImg, width=200)
    
    with col2:
        st.text(f'■ Album Name : {albumName}')
        st.text(f'■ Artist Name : {artistName}')
        st.text(f'■ Track Name : {trackName}')
        st.text(f'■ Release Date : {releaseDate}')
    
    albumURL
    if artistInfo["genres"] != []:
        st.text(f'■ Genre : {", ".join(artistInfo["genres"])}')
    else:
        st.text(f'■ Genre : -')
    st.text(f'■ Related Artists')
    count = 0
    output = []

    for artist in related:
        link = artist[1]
        #print(link)
        st.text(f'{artist[0]}')
        st.markdown(link, unsafe_allow_html=True)        
    
else:
    st.text(f'Track is not playing')

# update every 5sec
st_autorefresh(interval=15000, key="dataframerefresh")
