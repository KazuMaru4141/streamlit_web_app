import streamlit as st
from PIL import Image
from streamlit_autorefresh import st_autorefresh
from SpreadSheetAPI import GspreadCtrl

import spotipy
import spotipy.util as util
from spotipy.oauth2 import SpotifyClientCredentials
from spotipy.oauth2 import SpotifyOAuth

from SpotifyAPI import SpotifyCtrl

import datetime

def initSessionState(st):
    if 'trackInfo' not in st.session_state:
        st.session_state.trackInfo = {}
        st.session_state.trackInfo["trackName"] = ""
        st.session_state.trackInfo["trackID"] = ""
        st.session_state.trackInfo["trackURL"] = ""
        st.session_state.trackInfo["trackURI"] = ""
        st.session_state.trackInfo["artistName"] = ""
        st.session_state.trackInfo["artistID"] = ""
        st.session_state.trackInfo["artistURL"] = ""
        st.session_state.trackInfo["albumName"] = ""
        st.session_state.trackInfo["albumID"] = ""
        st.session_state.trackInfo["albumURL"] = ""
        st.session_state.trackInfo["releaseDate"] = ""
        st.session_state.trackInfo["albumImg"] = ""
        st.session_state.trackInfo["genre"] = ""
        st.session_state.trackInfo["related"] = []

def updateSessionState(st):
    if st.session_state.trackInfo["trackName"] != currentTrack["item"]["name"]:        
        st.session_state.trackInfo["trackName"] = currentTrack["item"]["name"]
        st.session_state.trackInfo["trackID"] = currentTrack["item"]["id"]
        st.session_state.trackInfo["trackURI"] = currentTrack["item"]["uri"]
        st.session_state.trackInfo["trackURL"] = currentTrack["item"]["external_urls"]["spotify"]
        st.session_state.trackInfo["artistName"] = currentTrack["item"]["artists"][0]["name"]
        st.session_state.trackInfo["artistID"] = currentTrack["item"]["artists"][0]["id"]
        st.session_state.trackInfo["artistURL"] = currentTrack["item"]["artists"][0]["external_urls"]["spotify"]
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

def onclickLiked():
    gs = GspreadCtrl
    SP_SHEET_KEY = st.secrets.SP_SHEET_KEY.Key_LikedSongs
    ws, wb, LikedInfo = gs.connect_gspread(SP_SHEET_KEY)
    list_of_list = ws.col_values(2)
    
    if st.session_state.trackInfo["trackName"] not in list_of_list: 
        dt_now = dt_now = datetime.datetime.now()
        today = str(dt_now.year) + "-" + str(dt_now.month) + "-" + str(dt_now.day)
        appendList = []
        appendList.append([
            today,
            st.session_state.trackInfo["trackName"],
            st.session_state.trackInfo["albumName"],
            st.session_state.trackInfo["artistName"],
            st.session_state.trackInfo["albumImg"],
            st.session_state.trackInfo["trackID"],
            "",
            st.session_state.trackInfo["trackURL"]
        ])
        #print("Added!")
        ws.append_rows(appendList)
        sp.addLikedTrackToPlaylist(spotify, st.session_state.trackInfo["trackURI"])
        st.write(f'Successfully Added')
    else:
        st.write(f'Already Added')

def onclickSaved():        
    gs = GspreadCtrl
    SP_SHEET_KEY = st.secrets.SP_SHEET_KEY.key_SpotifySavedAlbums
    ws, wb, SpreadInfo = gs.connect_gspread(SP_SHEET_KEY)
    dt_now = dt_now = datetime.datetime.now()
    today = str(dt_now.year) + "-" + str(dt_now.month) + "-" + str(dt_now.day)
    appendList = []
    appendList.append([
        today,
        "",
        st.session_state.trackInfo["albumName"],
        st.session_state.trackInfo["artistName"],
        st.session_state.trackInfo["albumImg"],
        "",
        st.session_state.trackInfo["albumID"],
        st.session_state.trackInfo["albumURL"],
        st.session_state.trackInfo["artistID"],
        st.session_state.trackInfo["artistURL"],
        "",
        0,
        0,
        "",
        "",
        "",
        "",
        "",
        st.session_state.trackInfo["releaseDate"],
        ", ".join(st.session_state.trackInfo["genre"]),
        ""
    ])
    print(appendList)
    ws.append_rows(appendList)
    print(f'Successfully Saved!')

############### Main #######################################
st.write(f'#### Now Playing')
initSessionState(st)

sp = SpotifyCtrl
auth_manager, spotify = sp.create_spotify()
currentTrack = spotify.current_user_playing_track()
cols = st.columns(2)

if currentTrack != None:
    updateSessionState(st)
    st.image(st.session_state.trackInfo["albumImg"], width=100)
    st.button('♥️', on_click=onclickLiked)
    st.button('✅', on_click=onclickSaved)

    st.page_link(st.session_state.trackInfo["albumURL"], label=st.session_state.trackInfo["trackName"])
    st.page_link(st.session_state.trackInfo["artistURL"], label=st.session_state.trackInfo["artistName"])
        
    st.markdown('##### Genre')
    if st.session_state.trackInfo["genre"] != []:
        st.write(f'{", ".join(st.session_state.trackInfo["genre"])}')
    else:
        st.write(f'-')

    st.markdown('##### Related Artists')

    for artist in st.session_state.trackInfo["related"]:
        link = artist[1]
        linkLabel = artist[0]
        st.page_link(link, label=linkLabel)
                
else:
    st.text(f'Track is not playing')
    
# update every 5sec
st_autorefresh(interval=15000, key="dataframerefresh")
