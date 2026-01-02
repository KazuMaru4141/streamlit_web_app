import streamlit as st
from PIL import Image
from streamlit_autorefresh import st_autorefresh
from SpreadSheetAPI import GspreadCtrl
from pylastCtrl import pylastCtrl
import pytz
import pandas as pd

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
        st.session_state.trackInfo["albumTracks"] = {} 
        st.session_state.trackInfo["albumURL"] = ""
        st.session_state.trackInfo["releaseDate"] = ""
        st.session_state.trackInfo["albumImg"] = ""
        st.session_state.trackInfo["genre"] = ""
        st.session_state.trackInfo["artistImg"] = ""
        st.session_state.trackInfo["artistPopularity"] = ""
        st.session_state.trackInfo["type"] = ""
        st.session_state.trackInfo["total_tracks"] = ""
        st.session_state.artistInfo = {}
    
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
        st.session_state.LikedInfo = []
    
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
        
        if st.session_state.trackInfo["albumID"] != currentTrack["item"]["album"]["id"]:
            st.session_state.trackInfo["albumID"] = currentTrack["item"]["album"]["id"]
            st.session_state.trackInfo["albumTracks"] = spotify.album_tracks(currentTrack["item"]["album"]["id"])
        st.session_state.trackInfo["albumURL"] = currentTrack["item"]["album"]["external_urls"]["spotify"]
        st.session_state.trackInfo["releaseDate"] = currentTrack["item"]["album"]["release_date"]
        album_images = currentTrack["item"]["album"].get("images", [])
        st.session_state.trackInfo["albumImg"] = album_images[0]["url"] if album_images else ""
        st.session_state.trackInfo["type"] = currentTrack["item"]["album"]["type"]
        st.session_state.trackInfo["total_tracks"] = currentTrack["item"]["album"]["total_tracks"]
        artistInfo = spotify.artist(st.session_state.trackInfo["artistID"])
        st.session_state.artistInfo = artistInfo
        st.session_state.trackInfo["genre"] = artistInfo.get("genres", [])
        #        print(st.session_state.artistInfo)
        artist_images = artistInfo.get("images", [])
        st.session_state.trackInfo["artistImg"] = artist_images[0]["url"] if artist_images else ""
        st.session_state.trackInfo["artistPopularity"] = artistInfo["popularity"]
        
        try:
            now_playing = pc.getNowPlaying(lastfm_user)
            if now_playing is not None:
                st.session_state.playCount["artistPlayCount"] = pc.getArtistPlayCount(lastfm_user, now_playing)
                st.session_state.playCount["albumPlayCount"] = pc.getAlbumPlayCount(lastfm_user, now_playing)
                st.session_state.playCount["track_play_count"] = pc.getTrackPlayCount(lastfm_user, now_playing)
                st.session_state.playCount["playCountToday"] = pc.getPlayCountToday(lastfm_user)
                st.session_state.playCount["OverallPlayCount"] = pc.getOverallPlayCount(lastfm_user)
            else:
                st.session_state.playCount["artistPlayCount"] = 0
                st.session_state.playCount["albumPlayCount"] = 0
                st.session_state.playCount["track_play_count"] = 0
                st.session_state.playCount["playCountToday"] = 0
                st.session_state.playCount["OverallPlayCount"] = 0
        except:
            st.session_state.playCount["artistPlayCount"] = 0
            st.session_state.playCount["albumPlayCount"] = 0
            st.session_state.playCount["track_play_count"] = 0
            st.session_state.playCount["playCountToday"] = 0
            st.session_state.playCount["OverallPlayCount"] = 0

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
        cell = ws.find(st.session_state.trackInfo["trackID"])
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
    ws.append_rows(appendList)
    st.write(f'Successfully Saved!')

def readSpreadSheet(st):
    if st.session_state.gs == None:
        with st.spinner("Loading..."):
            st.session_state.gs = GspreadCtrl
            st.session_state.ws, st.session_state.wb, st.session_state.LikedInfo = st.session_state.gs.connect_gspread(st.secrets.SP_SHEET_KEY.Key_LikedSongs)

############### Main #######################################
#st.write(f'#### Now Playing')
initSessionState(st)
readSpreadSheet(st)

currentTrack = spotify.current_user_playing_track()

if currentTrack != None:
    updateSessionState(st)
    
    
    
    with st.container(border=True):
        st.markdown("### Track")
        st.image(st.session_state.trackInfo["albumImg"], width=70)    
    #    st.button('♥️', on_click=onclickLiked)
        st.button('✅', on_click=onclickSaved)
        st.write(f'__{st.session_state.trackInfo["trackName"]}__ by __{st.session_state.trackInfo["artistName"]}__ ({st.session_state.trackInfo["releaseDate"]})')
        st.markdown(f'🎤 {st.session_state.playCount["artistPlayCount"]} &nbsp; &nbsp; 💿 {st.session_state.playCount["albumPlayCount"]}  &nbsp; &nbsp; 🎵 {st.session_state.playCount["track_play_count"]}  \n ⏭️ {st.session_state.playCount["playCountToday"]} &nbsp; &nbsp; &nbsp; ▶️ {st.session_state.playCount["OverallPlayCount"]}')    
        # if st.session_state.trackInfo["genre"] != []:
        #     st.write(f'{", ".join(st.session_state.trackInfo["genre"])}')
        # else:
        #     st.write(f'-')
    
    
        star_options = {
            "★": 1,
            "★★" : 2, 
            "★★★" : 3, 
            "★★★★" : 4, 
            "★★★★★" : 5
        }
        trackIdList = st.session_state.ws.col_values(6)
        if st.session_state.trackInfo["trackID"] in trackIdList:
            cell = st.session_state.ws.find(st.session_state.trackInfo["trackID"])
            row = int(cell.row)
            current_rate = int(st.session_state.ws.cell(row, 9).value)
            
            rate = st.radio("Rate", 
                ["★", "★★", "★★★", "★★★★", "★★★★★"],
                index=(current_rate-1)
                )
            rate = star_options[rate]
            
            flg = False
            for likedSong in st.session_state.LikedInfo:
                if st.session_state.trackInfo["trackID"] == likedSong["TrackID"]:
                    likedSong["Rating"] = rate
                    flg = True
            
            if flg == False:
                dt_now = dt_now = datetime.datetime.now(tz=pytz.timezone("Asia/Tokyo"))
                today = str(dt_now.year) + "-" + str(dt_now.month) + "-" + str(dt_now.day)
                appendDict = {}
                appendDict["SavedAt"] = today
                appendDict["trackName"] = st.session_state.trackInfo["trackName"]
                appendDict["AlbumName"] = st.session_state.trackInfo["albumName"]
                appendDict["ArtistName"] = st.session_state.trackInfo["artistName"]
                appendDict["AlbumImage"] = st.session_state.trackInfo["albumImg"]
                appendDict["TrackID"] = st.session_state.trackInfo["trackID"]
                appendDict["TrackSrc"] = ""
                appendDict["TrackURL"] = st.session_state.trackInfo["trackURL"]
                appendDict["Rating"] = rate
                st.session_state.LikedInfo.append(appendDict)

        else:
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
                str(2),
            ])
            st.session_state.ws.append_rows(appendList)
            current_rate = 0
            rate = st.radio("rate this track", 
                ["★", "★★", "★★★", "★★★★", "★★★★★"],
                index=1
                ) 
            rate = star_options[rate]
            print(rate, current_rate)
        
        if (current_rate != rate):    
            st.success("rating updated")
            st.session_state.ws.update_cell(cell.row, 9, rate)
    
    with st.container(border=True):
        st.markdown("### Album")
        track_point = {
            1: 0,
            2: 20, 
            3: 60, 
            4 : 80, 
            5 : 100
        }
        if st.session_state.trackInfo["albumTracks"] is not None:
            totalTrackNum = st.session_state.trackInfo["albumTracks"]["total"]
            
            disp_rate = {
                0: "☆☆☆☆☆",
                1 : "★☆☆☆☆", 
                2 : "★★☆☆☆", 
                3 : "★★★☆☆", 
                4 : "★★★★☆",
                5 : "★★★★★"
            }
            cnt = 1
            album_rate = 0.0
            album_table = []
            for track in st.session_state.trackInfo["albumTracks"]["items"]:
                trackname = track["name"]
                trackid = track["id"]
                
                current_rate = 0
                for likedSong in st.session_state.LikedInfo:
                    if trackid == likedSong["TrackID"]:
                        current_rate = likedSong["Rating"]
                        album_rate += track_point[current_rate]
                disp = disp_rate[current_rate]
                album_table.append([trackname, disp])
    #            st.write(f'{cnt}. {trackname} {disp}')
                cnt+=1
            
            average = album_rate / totalTrackNum
            
            dispAlbum = []
            st.markdown(f'[link]({st.session_state.trackInfo["albumURL"]})')
            
            dispAlbum.append(["Name", str(st.session_state.trackInfo["albumName"])])
            dispAlbum.append(["Score", str(average)])
            dispAlbum.append(["Release Date", str(st.session_state.trackInfo["releaseDate"])])
            dispAlbum.append(["Genre", ", ".join(st.session_state.trackInfo["genre"])])
            dataframe = pd.DataFrame(dispAlbum)
            st.table(dataframe)
            
            df = pd.DataFrame(album_table, columns=["Track Name", "Rate"])
            df.index = df.index + 1
            st.table(df)
            st.write(f'total point {album_rate}')
        
    with st.container(border=True):
        st.markdown("#### Artist")
        artist = st.session_state.artistInfo
        dispArtist = []
        dispArtist.append(
            ["name", str(artist["name"])]
        )
        dispArtist.append(
            ["popularity", str(artist["popularity"])]
        )
        dispArtist.append(
            ["followers", str(artist["followers"]["total"])]
        )            
        artist_images = artist.get("images", [])
        if artist_images:
            st.image(artist_images[0]["url"], width=100)
        st.markdown(f'[link]({artist["external_urls"]["spotify"]})')
        
        dataframe = pd.DataFrame(dispArtist)
        st.table(dataframe)
else:
    st.text(f'Track is not playing')
    
# update every 5sec
st_autorefresh(interval=15000, key="dataframerefresh")
