import streamlit as st
from PIL import Image
from streamlit_autorefresh import st_autorefresh
from SpreadSheetAPI import GspreadCtrl
from pylastCtrl import pylastCtrl

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

        artistInfo = spotify.artist(st.session_state.trackInfo["artistID"])
        relatedArtists = spotify.artist_related_artists(st.session_state.trackInfo["artistID"])
        st.session_state.trackInfo["genre"] = artistInfo["genres"]

        related = []
        for artist in relatedArtists["artists"]:
            appendList = [artist["name"], artist["external_urls"]["spotify"]]
            related.append(appendList)
        st.session_state.trackInfo["related"] = related
        st.session_state.trackInfo["artistImg"] = artist["images"][0]["url"]
        st.session_state.trackInfo["artistPopularity"] = artist["popularity"]

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
            st.session_state.trackInfo["trackURL"],
            str(1),
        ])
        #print("Added!")
        ws.append_rows(appendList)
        sp.addLikedTrackToPlaylist(spotify, st.session_state.trackInfo["trackURI"])
        st.write(f'Successfully Added')
    else:
        #impression = int(LikedInfo[st.session_state.trackInfo["Impression"]])
        #impression = impression + 1
        
        cell = ws.find(st.session_state.trackInfo["trackName"])
        #print(cell)
        #print(cell.row)
        #print(ws.cell(cell.row, 9))
        row = int(cell.row)
        #print(ws.cell(row, 9).value)
        if (ws.cell(row, 9).value == None):
            ws.update_cell(cell.row, 9, "1")
        else:
            impression = int(ws.cell(row, 9).value)
            impression = impression + 1
            ws.update_cell(cell.row, 9, impression)
        #ws.update_cell()
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
        0,
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
#    print(f'Successfully Saved!')

def onclickNext():
    print("-----------------------------------------")
    device = spotify.devices()
    print(device)
    spotify.next()
#   # sp.skipTrack(spotify)
    #print("skipped")

############### Main #######################################
st.write(f'#### Now Playing')
initSessionState(st)

currentTrack = spotify.current_user_playing_track()

#print(currentTrack)
if currentTrack != None:
    updateSessionState(st)
    now_playing = pc.getNowPlaying(lastfm_user)
    artistPlayCount = pc.getArtistPlayCount(lastfm_user, now_playing)
    albumPlayCount = pc.getAlbumPlayCount(lastfm_user, now_playing)
    track_play_count = pc.getTrackPlayCount(lastfm_user, now_playing)
    playCountToday = pc.getPlayCountToday(lastfm_user)
    OverallPlayCount = pc.getOverallPlayCount(lastfm_user)
    totalArtists = pc.getOverallArtist(lastfm_user)
    totalAlbums = pc.getOverallAlbum(lastfm_user)
    totalTracks = pc.getOverallTracks(lastfm_user)
    
    col1, col2, col3 = st.columns([2, 2, 6])
    with col1:
        st.image(st.session_state.trackInfo["albumImg"], width=100)
        
    with col2:
        st.button('♥️', on_click=onclickLiked)
        st.button('✅', on_click=onclickSaved)
    
    col1, col2, col3 = st.columns([2, 2, 6])
    with col1:
        st.write(st.session_state.trackInfo["trackName"])
    
    with col2:
        st.write(st.session_state.trackInfo["artistName"])
    
    st.write(st.session_state.trackInfo["releaseDate"])
    
    st.markdown('##### Genre')
    if st.session_state.trackInfo["genre"] != []:
        st.write(f'{", ".join(st.session_state.trackInfo["genre"])}')
    else:
        st.write(f'-')

    st.markdown('##### Related Artists')
    
    for artist in st.session_state.trackInfo["related"]:
        link = artist[1]
        linkLabel = artist[0]
        #st.page_link(link, label=linkLabel)
        st.write(artist[0])
    
    st.sidebar.markdown("## Scrobbles")
    st.sidebar.write(f'artist {artistPlayCount}')
    st.sidebar.write(f'album {albumPlayCount}')
    st.sidebar.write(f'track {track_play_count}')
    
    st.sidebar.write(f'today  {playCountToday}')
    st.sidebar.write(f'total scrobbles {OverallPlayCount}')
    st.sidebar.write(f'total artists   {totalArtists}')
    st.sidebar.write(f'total albums    {totalAlbums}')
    st.sidebar.write(f'total tracks    {totalTracks}')
                
else:
    st.text(f'Track is not playing')
    
# update every 5sec
st_autorefresh(interval=15000, key="dataframerefresh")
