import streamlit as st
from PIL import Image
from streamlit_autorefresh import st_autorefresh
from SpreadSheetAPI import GspreadCtrl
from pylastCtrl import pylastCtrl
import pytz

import spotipy
import spotipy.util as util
from spotipy.oauth2 import SpotifyClientCredentials
from spotipy.oauth2 import SpotifyOAuth

from SpotifyAPI import SpotifyCtrl

import datetime

st.set_page_config(layout="wide")

sp = SpotifyCtrl
auth_manager, spotify = sp.create_spotify()

pc = pylastCtrl
lastfm_network = pc.getNetwork()
lastfm_user = pc.getUser(lastfm_network)

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
        st.session_state.trackInfo["artistImg"] = ""
        st.session_state.trackInfo["artistPopularity"] = ""
        st.session_state.trackInfo["type"] = ""
        st.session_state.trackInfo["total_tracks"] = ""
    
    if 'playCount' not in st.session_state:
        #st.session_state.playCount["nowPlaying"] = ""
        st.session_state.playCount = {}
        st.session_state.playCount["artistPlayCount"] = ""
        st.session_state.playCount["albumPlayCount"] = ""
        st.session_state.playCount["track_play_count"] = ""
        st.session_state.playCount["playCountToday"] = ""
        st.session_state.playCount["OverallPlayCount"] = ""
    
    if 'gs' not in st.session_state:
        st.session_state.gs = None
    
    if 'ws' not in st.session_state:
        st.session_state.ws = None
    
    if 'wb' not in st.session_state:
        st.session_state.wb = None
    
    if 'LikedInfo' not in st.session_state:
        st.session_state.LikedInfo = {}
    
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
        st.session_state.trackInfo["type"] = currentTrack["item"]["album"]["type"]
        st.session_state.trackInfo["total_tracks"] = currentTrack["item"]["album"]["total_tracks"]

#        artistInfo = sp.get_related_artistInfo(st.session_state.trackInfo["artistID"])
        artistInfo = spotify.artist(st.session_state.trackInfo["artistID"])
#        relatedArtists = spotify.artist_related_artists(spotify, st.session_state.trackInfo["artistID"])
        st.session_state.trackInfo["genre"] = artistInfo["genres"]

        # related = []
        # if relatedArtists != "":
        #     for artist in relatedArtists["artists"]:
        #         appendList = [artist["name"], artist["external_urls"]["spotify"]]
        #         related.append(appendList)
        #     st.session_state.trackInfo["related"] = related
        # else: 
        st.session_state.trackInfo["related"] = ""
        st.session_state.trackInfo["artistImg"] = artistInfo["images"][0]["url"]
        st.session_state.trackInfo["artistPopularity"] = artistInfo["popularity"]
        
        now_playing = pc.getNowPlaying(lastfm_user)
        st.session_state.playCount["artistPlayCount"] = pc.getArtistPlayCount(lastfm_user, now_playing)
        st.session_state.playCount["albumPlayCount"] = pc.getAlbumPlayCount(lastfm_user, now_playing)
        st.session_state.playCount["track_play_count"] = pc.getTrackPlayCount(lastfm_user, now_playing)
        st.session_state.playCount["playCountToday"] = pc.getPlayCountToday(lastfm_user)
        st.session_state.playCount["OverallPlayCount"] = pc.getOverallPlayCount(lastfm_user)

def onclickLiked():
    gs = GspreadCtrl
    SP_SHEET_KEY = st.secrets.SP_SHEET_KEY.Key_LikedSongs
    ws, wb, LikedInfo = gs.connect_gspread(SP_SHEET_KEY)
    trackIdList = ws.col_values(6)
    
    if st.session_state.trackInfo["trackID"] not in trackIdList: 
        dt_now = dt_now = datetime.datetime.now(tz=pytz.timezone("Asia/Tokyo"))
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
            st.session_state.trackInfo["trackURL"],
            str(1),
        ])
        ws.append_rows(appendList)
        sp.addLikedTrackToPlaylist(spotify, st.session_state.trackInfo["trackURI"])
        st.write(f'Successfully Added')
    else:
        cell = ws.find(st.session_state.trackInfo["trackName"])
        row = int(cell.row)
        if (ws.cell(row, 9).value == None):
            ws.update_cell(cell.row, 9, "1")
        else:
            impression = int(ws.cell(row, 9).value)
            impression = impression + 1
            ws.update_cell(cell.row, 9, impression)
        st.write(f'Already Added')

def onclickSaved():        
    gs = GspreadCtrl
    SP_SHEET_KEY = st.secrets.SP_SHEET_KEY.key_SpotifySavedAlbums
    ws, wb, SpreadInfo = gs.connect_gspread(SP_SHEET_KEY)
    dt_now = dt_now = datetime.datetime.now(tz=pytz.timezone("Asia/Tokyo"))
    today = str(dt_now.year) + "-" + str(dt_now.month) + "-" + str(dt_now.day)
    appendList = []
    appendList.append([
        today,
        "",
        st.session_state.trackInfo["albumName"],
        st.session_state.trackInfo["artistName"],
        st.session_state.trackInfo["albumImg"],
        st.session_state.trackInfo["artistImg"],
        st.session_state.trackInfo["albumID"],
        st.session_state.trackInfo["albumURL"],
        st.session_state.trackInfo["artistID"],
        st.session_state.trackInfo["artistURL"],
        st.session_state.trackInfo["total_tracks"],
        0,
        0,
        "",
        "",
        st.session_state.trackInfo["artistPopularity"],
        "",
        st.session_state.trackInfo["type"],
        st.session_state.trackInfo["releaseDate"],
        ", ".join(st.session_state.trackInfo["genre"]),
        ""
    ])
    print(appendList)
    ws.append_rows(appendList)
    st.write(f'Successfully Saved!')

# def onChangeStar():
#     gs = GspreadCtrl
#     SP_SHEET_KEY = st.secrets.SP_SHEET_KEY.Key_LikedSongs
#     ws, wb, LikedInfo = gs.connect_gspread(SP_SHEET_KEY)
#     trackIdList = ws.col_values(6)
    
#     if st.session_state.trackInfo["trackID"] not in trackIdList: 
#         dt_now = dt_now = datetime.datetime.now(tz=pytz.timezone("Asia/Tokyo"))
#         today = str(dt_now.year) + "-" + str(dt_now.month) + "-" + str(dt_now.day)
#         appendList = []
#         appendList.append([
#             today,
#             st.session_state.trackInfo["trackName"],
#             st.session_state.trackInfo["albumName"],
#             st.session_state.trackInfo["artistName"],
#             st.session_state.trackInfo["albumImg"],
#             st.session_state.trackInfo["trackID"],
#             "",
#             st.session_state.trackInfo["trackURL"],
#             str(1),
#         ])
#         ws.append_rows(appendList)
#         sp.addLikedTrackToPlaylist(spotify, st.session_state.trackInfo["trackURI"])
#         st.write(f'Successfully Added')
#     else:
#         cell = ws.find(st.session_state.trackInfo["trackName"])
#         row = int(cell.row)
#         if (ws.cell(row, 9).value == None):
#             ws.update_cell(cell.row, 9, "1")
#         else:
#             impression = int(ws.cell(row, 9).value)
#             impression = impression + 1
#             ws.update_cell(cell.row, 9, impression)
#         st.write(f'Already Added')

def readSpreadSheet(st):
    if st.session_state.gs == None:
        st.write("read spread sheet")
        st.session_state.gs = GspreadCtrl
        st.session_state.ws, st.session_state.wb, st.session_state.LikedInfo = st.session_state.gs.connect_gspread(st.secrets.SP_SHEET_KEY.Key_LikedSongs)

############### Main #######################################
#st.write(f'#### Now Playing')
initSessionState(st)
readSpreadSheet(st)

currentTrack = spotify.current_user_playing_track()

#print(currentTrack)
if currentTrack != None:
    updateSessionState(st)
    
    st.image(st.session_state.trackInfo["albumImg"], width=70)    
#    st.button('♥️', on_click=onclickLiked)
    st.button('✅', on_click=onclickSaved)
    
    st.write(f'__{st.session_state.trackInfo["trackName"]}__ by __{st.session_state.trackInfo["artistName"]}__ ({st.session_state.trackInfo["releaseDate"]})')
    st.markdown(f'🎤 {st.session_state.playCount["artistPlayCount"]} &nbsp; &nbsp; 💿 {st.session_state.playCount["albumPlayCount"]}  &nbsp; &nbsp; 🎵 {st.session_state.playCount["track_play_count"]}  \n ⏭️ {st.session_state.playCount["playCountToday"]} &nbsp; &nbsp; &nbsp; ▶️ {st.session_state.playCount["OverallPlayCount"]}')    
    star_options = {
        "★": 1,
        "★★" : 2, 
        "★★★" : 3, 
        "★★★★" : 4, 
        "★★★★★" : 5
    }
    trackIdList = st.session_state.ws.col_values(6)
    if st.session_state.trackInfo["trackID"] in trackIdList:
        cell = st.session_state.ws.find(st.session_state.trackInfo["trackName"])
        row = int(cell.row)
        current_rate = int(st.session_state.ws.cell(row, 9).value)
        
        rate = st.radio("Rate", 
             ["★", "★★", "★★★", "★★★★", "★★★★★"],
             index=(current_rate-1)
             )
        rate = star_options[rate]
    else:
        rate = st.radio("rate this track", 
             ["★", "★★", "★★★", "★★★★", "★★★★★"],
             index=None
             ) 
        rate = 0
    
    if (current_rate != rate):    
        st.write("rating changed")
        st.session_state.ws.update_cell(cell.row, 9, rate)
    
#    st.markdown('##### Genre')
    if st.session_state.trackInfo["genre"] != []:
        st.write(f'{", ".join(st.session_state.trackInfo["genre"])}')
    else:
        st.write(f'-')

    # st.write(f'artist {st.session_state.playCount["artistPlayCount"]}')
    # st.write(f'album {st.session_state.playCount["albumPlayCount"]}')
    # st.write(f'track {st.session_state.playCount["track_play_count"]}')
    # st.write(f'today  {st.session_state.playCount["playCountToday"]}')
    # st.write(f'total scrobbles {st.session_state.playCount["OverallPlayCount"]}')

    # st.markdown('##### Related Artists')
    
    # if st.session_state.trackInfo["related"] != "":
    #     for artist in st.session_state.trackInfo["related"]:
    #         link = artist[1]
    #         linkLabel = artist[0]
    #         st.write(artist[0])
                
else:
    st.text(f'Track is not playing')
    
# update every 5sec
st_autorefresh(interval=15000, key="dataframerefresh")
