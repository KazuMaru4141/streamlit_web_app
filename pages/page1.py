import streamlit as st
from PIL import Image
from streamlit_autorefresh import st_autorefresh

import spotipy
import spotipy.util as util
from spotipy.oauth2 import SpotifyClientCredentials
from spotipy.oauth2 import SpotifyOAuth

from SpotifyAPI import SpotifyCtrl

import datetime

st.title('Currently Playing Track')
col1, col2 = st.columns(2)

if 'trackInfo' not in st.session_state:
    st.session_state.trackInfo = {}
    st.session_state.trackInfo["trackName"] = ""
    st.session_state.trackInfo["artistName"] = ""
    st.session_state.trackInfo["artistID"] = ""
    st.session_state.trackInfo["albumName"] = ""
    st.session_state.trackInfo["albumID"] = ""
    st.session_state.trackInfo["albumURL"] = ""
    st.session_state.trackInfo["releaseDate"] = ""
    st.session_state.trackInfo["albumImg"] = ""
    st.session_state.trackInfo["genre"] = ""
    st.session_state.trackInfo["related"] = []

sp = SpotifyCtrl
auth_manager, spotify = sp.create_spotify()
currentTrack = spotify.current_user_playing_track()

if currentTrack != None:
    if st.session_state.trackInfo["trackName"] != currentTrack["item"]["name"]:        
        st.session_state.trackInfo["trackName"] = currentTrack["item"]["name"]
        st.session_state.trackInfo["artistName"] = currentTrack["item"]["artists"][0]["name"]
        st.session_state.trackInfo["artistID"] = currentTrack["item"]["artists"][0]["id"]
        st.session_state.trackInfo["albumName"] = currentTrack["item"]["album"]["name"]
        st.session_state.trackInfo["albumID"] = currentTrack["item"]["album"]["id"]
        st.session_state.trackInfo["albumURL"] = currentTrack["item"]["album"]["external_urls"]["spotify"]
        st.session_state.trackInfo["releaseDate"] = currentTrack["item"]["album"]["release_date"]
        st.session_state.trackInfo["albumImg"] = currentTrack["item"]["album"]["images"][0]["url"]

        artistInfo = spotify.artist(st.session_state.trackInfo["artistID"])
        relatedArtists = spotify.artist_related_artists(st.session_state.trackInfo["artistID"])
        st.session_state.trackInfo["genre"] = artistInfo["genres"]

        related = []
        for artist in relatedArtists["artists"]:
            appendList = [artist["name"], artist["external_urls"]["spotify"]]
            related.append(appendList)
        st.session_state.trackInfo["related"] = related
        
    with col1:
        st.image(st.session_state.trackInfo["albumImg"], width=200)
        
    with col2:
        st.write(f'■ Album Name : {st.session_state.trackInfo["albumName"]}')
        st.write(f'■ Artist Name : {st.session_state.trackInfo["artistName"]}')
        st.write(f'■ Track Name : {st.session_state.trackInfo["trackName"]}')
        st.write(f'■ Release Date : {st.session_state.trackInfo["releaseDate"]}')
        
    st.session_state.trackInfo["albumURL"]
    if st.session_state.trackInfo["genre"] != []:
        st.write(f'■ Genre : {", ".join(st.session_state.trackInfo["genre"])}')
    else:
        st.write(f'■ Genre : -')
    st.write(f'■ Related Artists')
    count = 0
    output = []

    info = []
    for artist in st.session_state.trackInfo["related"]:
        link = artist[1]
        #print(link)
        st.write(f'{artist[0]}')
        st.markdown(link, unsafe_allow_html=True) 
        
else:
    st.text(f'Track is not playing')
    
    

# update every 5sec
st_autorefresh(interval=15000, key="dataframerefresh")
