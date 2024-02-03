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

st.title('Currently Playing Track')
col1, col2 = st.columns(2)

if 'trackInfo' not in st.session_state:
    st.session_state.trackInfo = {}
    st.session_state.trackInfo["trackName"] = ""
    st.session_state.trackInfo["trackID"] = ""
    st.session_state.trackInfo["trackURL"] = ""
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

sp = SpotifyCtrl
auth_manager, spotify = sp.create_spotify()
currentTrack = spotify.current_user_playing_track()

if currentTrack != None:
    if st.session_state.trackInfo["trackName"] != currentTrack["item"]["name"]:        
        st.session_state.trackInfo["trackName"] = currentTrack["item"]["name"]
        st.session_state.trackInfo["trackID"] = currentTrack["item"]["id"]
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
        
    with st.form(key='prifile_form'):
        st.image(st.session_state.trackInfo["albumImg"], width=200)
        like_btn = st.form_submit_button('like')
        save_btn = st.form_submit_button('save album')
            
        st.write(f'■ Album Name : {st.session_state.trackInfo["albumName"]}')
        st.write(f'{st.session_state.trackInfo["albumID"]}')
        st.write(f'■ Artist Name : {st.session_state.trackInfo["artistName"]}')
        st.write(f'{st.session_state.trackInfo["artistID"]}')
        st.write(f'■ Track Name : {st.session_state.trackInfo["trackName"]}')
        st.write(f'{st.session_state.trackInfo["trackID"]}')
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
        
        if like_btn == True:
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
            
            
        if save_btn == True:
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
            
            
        
else:
    st.text(f'Track is not playing')
    
    

# update every 5sec
st_autorefresh(interval=15000, key="dataframerefresh")
