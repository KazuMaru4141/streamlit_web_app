import dataclasses
import threading
import time
import pytz
import datetime
import pylast
import plotly.express as px
import plotly.graph_objects as go

import streamlit as st
from streamlit_autorefresh import st_autorefresh

from pylastCtrl import pylastCtrl
from SpreadSheetAPI import GspreadCtrl
from SpotifyAPI import SpotifyCtrl


class Worker(threading.Thread):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
#        print("init Worker")
        self.pc = pylastCtrl
        self.sp = SpotifyCtrl
        self.spotify = None
        self.auth_manager = None
        self.lastfm_network = self.pc.getNetwork()
        self.lastfm_user = self.pc.getUser(self.lastfm_network)
        self.stop_req = threading.Event()
        
        self.init_parameter()
#        self.i = 0
        
    def run(self):
        while not self.stop_req.wait(0):
#            if self.spotify is None:
#                self.auth_manager, self.spotify = self.sp.create_spotify()
            self.now_playing = self.pc.getNowPlaying(self.lastfm_user)
#            self.i = self.i + 1

            if self.now_playing is not None:
                trackName = self.now_playing.get_name()
                if trackName != self.track_title:
                    self.track_title = trackName
                    self.artist_name = self.now_playing.artist.get_name()
                    
                    currentAlbum = self.now_playing.get_album()
                    self.album_name = currentAlbum.title
                    self.album_cover_image = currentAlbum.get_cover_image(pylast.SIZE_EXTRA_LARGE)
                    self.artistPlayCount = self.pc.getArtistPlayCount(self.lastfm_user, self.now_playing)
                    self.albumPlayCount = self.pc.getAlbumPlayCount(self.lastfm_user, self.now_playing)
                    self.trackPlayCount = self.pc.getTrackPlayCount(self.lastfm_user, self.now_playing)
                    self.playCountToday = self.pc.getPlayCountToday(self.lastfm_user)
                    self.overallPlayCount = self.pc.getOverallPlayCount(self.lastfm_user)
                    
                    self.auth_manager, self.spotify = self.sp.create_spotify()
                    currentTrack = self.spotify.current_user_playing_track()
                    self.release_date = currentTrack["item"]["album"]["release_date"]
                    artistInfo = self.spotify.artist(currentTrack["item"]["artists"][0]["id"])
                    self.genres = artistInfo["genres"]
                    
                    relatedArtists = self.spotify.artist_related_artists(currentTrack["item"]["artists"][0]["id"])
                    related = []
                    for artist in relatedArtists["artists"]:
                        appendList = [artist["name"], artist["external_urls"]["spotify"]]
                        related.append(appendList)
                    self.related = related
                    
                    self.audioFeature = self.sp.getAudioFeature(self.spotify, currentTrack["item"]["id"])
            else:
                self.init_parameter()
            
            time.sleep(10)

    def init_parameter(self):
        self.artist_name = ""
        self.album_name = ""
        self.album_cover_image = ""
        self.release_date = ""
        self.genres = ""
        self.track_title = ""
        self.related = ""
        self.playCountToday = 0
        self.overallPlayCount = 0
        self.artistPlayCount = 0
        self.albumPlayCount = 0
        self.trackPlayCount = 0
        self.audioFeature = None

class SpreadSheetUpdater(threading.Thread):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.onLiked = threading.Event()
        self.onSaved = threading.Event()
        
#        print("init SpreadSheetUpdater")
        self.gs = GspreadCtrl
        self.wsLiked = None
        self.wbLiked = None
        self.LikedInfo = None
        self.wsSaved = None
        self.wbSaved = None
        self.SavedInfo = None
        self.sp = SpotifyCtrl
        self.spotify = None
        self.auth_manager = None
        self.stop_event = threading.Event()
        self.isLikedInit = False
        self.isLSavedInit = False
    
    def run(self):
        while not self.stop_event.is_set():
            self.setup_connections()

            if self.onLiked.wait(0) == True:
                self.handle_liked_event()
            
            if self.onSaved.wait(0) == True:
                self.handle_saved_event()
            
            time.sleep(1)
        
    def setup_connections(self):
        if self.wsLiked is None:
            self.wsLiked, self.wbLiked, self.LikedInfo = self.gs.connect_gspread(st.secrets.SP_SHEET_KEY.Key_LikedSongs)
            self.isLikedInit = True
#            print("spread sheet liked read")
        
        if self.wsSaved is None:
            self.wsSaved, self.wbSaved, self.SavedInfo = self.gs.connect_gspread(st.secrets.SP_SHEET_KEY.key_SpotifySavedAlbums)
            self.isLSavedInit = True
#            print("spread sheet saved read")
        
        if self.spotify is None:
            self.auth_manager, self.spotify = self.sp.create_spotify()
#            print("spotify object created")

    def handle_liked_event(self):
#        print("Likedボタン押されたよ")
        self.onLiked.clear()
        currentTrack = self.spotify.current_user_playing_track()
        trackIdList = self.wsLiked.col_values(6)

        if currentTrack["item"]["id"] not in trackIdList: 
            today = self.getToday()
            appendList = [[
                today,
                currentTrack["item"]["name"],
                currentTrack["item"]["album"]["name"],
                currentTrack["item"]["artists"][0]["name"],
                currentTrack["item"]["album"]["images"][0]["url"],
                currentTrack["item"]["id"],
                "",
                currentTrack["item"]["external_urls"]["spotify"],
                str(1),
            ]]
            self.wsLiked.append_rows(appendList)
#            st.write(f'Successfully Added')
        else:
            cell = self.wsLiked.find(currentTrack["item"]["id"])
            row = int(cell.row)
            if (self.wsLiked.cell(row, 9).value == None):
                self.wsLiked.update_cell(cell.row, 9, "1")
            else:
                impression = int(self.wsLiked.cell(row, 9).value)
                impression = impression + 1
                self.wsLiked.update_cell(cell.row, 9, impression)
#                st.write(f'Already Added')
    
    def handle_saved_event(self):
#        print("Savedボタン押されたよ")
        self.onSaved.clear()
        today = self.getToday()
        currentTrack = self.spotify.current_user_playing_track()
        artistInfo = self.spotify.artist(currentTrack["item"]["artists"][0]["id"])
        appendList = [[
            today,
            "",
            currentTrack["item"]["album"]["name"],
            currentTrack["item"]["artists"][0]["name"],
            currentTrack["item"]["album"]["images"][0]["url"],
            artistInfo["images"][0]["url"],
            currentTrack["item"]["album"]["id"],
            currentTrack["item"]["album"]["external_urls"]["spotify"],
            currentTrack["item"]["artists"][0]["id"],
            currentTrack["item"]["artists"][0]["external_urls"]["spotify"],
            currentTrack["item"]["album"]["total_tracks"],
            0,
            0,
            "",
            "",
            artistInfo["popularity"],
            "",
            currentTrack["item"]["album"]["type"],
            currentTrack["item"]["album"]["release_date"],
            ", ".join(artistInfo["genres"]),
            ""
        ]]

#        print(appendList)
        self.wsSaved.append_rows(appendList)
#        st.write(f'Successfully Saved!')

    def getToday(self):
        dt_now = datetime.datetime.now(tz=pytz.timezone("Asia/Tokyo"))
        today = f"{dt_now.year}-{dt_now.month}-{dt_now.day}"

        return today
        
    def stop(self):
        self.stop_event.set()
    
@st.cache_resource
@dataclasses.dataclass
class ThreadManager:
    worker = None
    worker2 = None
    
    def get_worker(self):
        return self.worker, self.worker2
    
    def is_running(self):
        return self.worker is not None and self.worker.is_alive()
    
    def start_worker(self):
        if self.worker is not None:
            self.stop_worker()
        self.worker = Worker(daemon=True)
        self.worker.start()
        
        self.worker2 = SpreadSheetUpdater(daemon=True)
        self.worker2.start()
        
        return self.worker
    
    def stop_worker(self):
        self.worker.stop_req.set()
        self.worker.join()
        self.worker = None
    
    def onLiked(self):
#        print("onLiked")
        self.worker2.onLiked.set()
    
    def onSaved(self):
#        print("onSaved")
        self.worker2.onSaved.set()
    
def main():    
    thread_manager = ThreadManager()    
    if not thread_manager.is_running():
#        print("start thread manager")
        worker = thread_manager.start_worker()
    else:
        worker, worker2 = thread_manager.get_worker()
        
        if worker.now_playing != None:
#            st.markdown(f'{worker.i}')
            if worker.album_cover_image is not None:
                st.image(worker.album_cover_image, width=100)
                
            if worker2.isLikedInit == True:
                st.button('♥️', on_click=thread_manager.onLiked)
            
            if worker2.isLSavedInit == True:
                st.button('✅', on_click=thread_manager.onSaved)
            
            st.markdown(f'__{worker.track_title}__ by __{worker.artist_name}__ ({worker.release_date})')
            st.markdown(f'🎤 {worker.artistPlayCount} &nbsp; &nbsp; 💿 {worker.albumPlayCount}  &nbsp; &nbsp; 🎵 {worker.trackPlayCount}')
            st.markdown(f'⏭️ {worker.playCountToday} &nbsp; &nbsp; &nbsp; ▶️ {worker.overallPlayCount}')
            if worker.genres != []:
                st.write(f'{", ".join(worker.genres)}')
            else:
                st.write(f'-')
            
            # データをリスト形式に変換
            if worker.audioFeature is not None:
                audio_features = worker.audioFeature[0]
                labels = ['danceability', 'energy', 'speechiness', 'acousticness', 'instrumentalness', 'liveness','loudness', 'valence']
                values = [audio_features[label] for label in labels]
                
                # レーダーチャートを作成
                fig = go.Figure()
                fig.add_trace(go.Scatterpolar( r=values, theta=labels, fill='toself' ))
                fig.update_layout(width=400, height=400, polar=dict(radialaxis=dict( visible=True, range=[0, 1] ) ), showlegend=False)
                st.plotly_chart(fig)
            
            st.markdown(":violet[__Related artists__]")
            for artist in worker.related:
                st.write(artist[0])
            
        else:
            st.markdown(f'Nothing playing')

    st_autorefresh(interval=1000, key="dataframerefresh") 

if __name__ == '__main__':
    main()