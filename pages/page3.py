import dataclasses
import threading
import time
import pytz
import datetime
import pylast

import streamlit as st
from streamlit_autorefresh import st_autorefresh

from pylastCtrl import pylastCtrl
from SpreadSheetAPI import GspreadCtrl
from SpotifyAPI import SpotifyCtrl

class Worker(threading.Thread):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        print("init Worker")
        self.pc = pylastCtrl
        self.lastfm_network = self.pc.getNetwork()
        self.lastfm_user = self.pc.getUser(self.lastfm_network)
        self.playCountToday = self.pc.getPlayCountToday(self.lastfm_user)
        self.overallPlayCount = self.pc.getOverallPlayCount(self.lastfm_user)        
        self.now_playing = self.pc.getNowPlaying(self.lastfm_user)
        
        self.i = 0
        
        if self.now_playing != None:
            self.artist_name = self.now_playing.artist.get_name()
            self.album_name = self.now_playing.get_album().title
            self.album_cover_image = self.now_playing.get_album().get_cover_image(pylast.SIZE_EXTRA_LARGE)
            self.release_date = ""
            self.track_title = self.now_playing.get_name()
            self.artistPlayCount = self.pc.getArtistPlayCount(self.lastfm_user, self.now_playing)
            self.albumPlayCount = self.pc.getAlbumPlayCount(self.lastfm_user, self.now_playing)
            self.trackPlayCount = self.pc.getTrackPlayCount(self.lastfm_user, self.now_playing)
        else:
            self.update_blank()
        self.stop_req = threading.Event()
        
    def run(self):
        while not self.stop_req.wait(0):
            time.sleep(1)
            self.now_playing = self.pc.getNowPlaying(self.lastfm_user)
            self.i = self.i + 1

            if self.now_playing != None:
                trackName = self.now_playing.get_name()
                if trackName != self.track_title:
                    self.track_title = trackName
                    self.artist_name = self.now_playing.artist.get_name()
                    self.album_name = self.now_playing.get_album().title
                    self.album_cover_image = self.now_playing.get_album().get_cover_image(pylast.SIZE_EXTRA_LARGE)
                    self.release_date = ""
                    self.artistPlayCount = self.pc.getArtistPlayCount(self.lastfm_user, self.now_playing)
                    self.albumPlayCount = self.pc.getAlbumPlayCount(self.lastfm_user, self.now_playing)
                    self.trackPlayCount = self.pc.getTrackPlayCount(self.lastfm_user, self.now_playing)
                    self.playCountToday = self.pc.getPlayCountToday(self.lastfm_user)
                    self.overallPlayCount = self.pc.getOverallPlayCount(self.lastfm_user)
            else:
                self.update_blank()

    def update_blank(self):
        self.artist_name = ""
        self.album_name = ""
        self.album_mbid = ""
        self.album_cover_image = ""
        self.release_date = ""
        self.track_title = ""
        self.track_mbid = ""
        self.artistPlayCount = ""
        self.albumPlayCount = ""
        self.trackPlayCount = ""

class SpreadSheetUpdater(threading.Thread):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.onLiked = threading.Event()
        self.onSaved = threading.Event()
        
        print("init SpreadSheetUpdater")
        self.gs = GspreadCtrl
        self.ws = None
        self.wb = None
        self.LikedInfo = None
        
    
    def run(self):
        while (1):
            if self.ws == None:
                self.ws, self.wb, self.LikedInfo = self.gs.connect_gspread(st.secrets.SP_SHEET_KEY.Key_LikedSongs)
                print("spread sheet read")
            
            if self.onLiked.wait(0) == True:
                print("Likedボタン押されたよ")
            
            if self.onSaved.wait(0) == True:
                print("Savedボタン押されたよ")
            
            time.sleep(1)
            

@st.cache_resource
@dataclasses.dataclass
class ThreadManager:
    worker = None
    SpreadSheetUpdater = None
    
    def get_worker(self):
        return self.worker
    
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
        self.worker2.onLiked.set()
    
    def onSaved(self):
        self.worker2.onSaved.set()

#def onclickLiked():
    # gs = GspreadCtrl
    # SP_SHEET_KEY = st.secrets.SP_SHEET_KEY.Key_LikedSongs
    # ws, wb, LikedInfo = gs.connect_gspread(SP_SHEET_KEY)
    # trackIdList = ws.col_values(6)
    
    # if st.session_state.trackInfo["trackID"] not in trackIdList: 
    #     dt_now = dt_now = datetime.datetime.now(tz=pytz.timezone("Asia/Tokyo"))
    #     today = str(dt_now.year) + "-" + str(dt_now.month) + "-" + str(dt_now.day)
    #     appendList = []
    #     appendList.append([
    #         today,
    #         st.session_state.trackInfo["trackName"],
    #         st.session_state.trackInfo["albumName"],
    #         st.session_state.trackInfo["artistName"],
    #         st.session_state.trackInfo["albumImg"],
    #         st.session_state.trackInfo["trackID"],
    #         "",
    #         st.session_state.trackInfo["trackURL"],
    #         str(1),
    #     ])
    #     ws.append_rows(appendList)
    #     sp.addLikedTrackToPlaylist(spotify, st.session_state.trackInfo["trackURI"])
    #     st.write(f'Successfully Added')
    # else:
    #     cell = ws.find(st.session_state.trackInfo["trackName"])
    #     row = int(cell.row)
    #     if (ws.cell(row, 9).value == None):
    #         ws.update_cell(cell.row, 9, "1")
    #     else:
    #         impression = int(ws.cell(row, 9).value)
    #         impression = impression + 1
    #         ws.update_cell(cell.row, 9, impression)
    #     st.write(f'Already Added')

#def onclickSaved():
    # gs = GspreadCtrl
    # SP_SHEET_KEY = st.secrets.SP_SHEET_KEY.key_SpotifySavedAlbums
    # ws, wb, SpreadInfo = gs.connect_gspread(SP_SHEET_KEY)
    # dt_now = dt_now = datetime.datetime.now(tz=pytz.timezone("Asia/Tokyo"))
    # today = str(dt_now.year) + "-" + str(dt_now.month) + "-" + str(dt_now.day)
    # appendList = []
    # appendList.append([
    #     today,
    #     "",
    #     st.session_state.trackInfo["albumName"],
    #     st.session_state.trackInfo["artistName"],
    #     st.session_state.trackInfo["albumImg"],
    #     st.session_state.trackInfo["artistImg"],
    #     st.session_state.trackInfo["albumID"],
    #     st.session_state.trackInfo["albumURL"],
    #     st.session_state.trackInfo["artistID"],
    #     st.session_state.trackInfo["artistURL"],
    #     st.session_state.trackInfo["total_tracks"],
    #     0,
    #     0,
    #     "",
    #     "",
    #     st.session_state.trackInfo["artistPopularity"],
    #     "",
    #     st.session_state.trackInfo["type"],
    #     st.session_state.trackInfo["releaseDate"],
    #     ", ".join(st.session_state.trackInfo["genre"]),
    #     ""
    # ])
    # print(appendList)
    # ws.append_rows(appendList)
    # st.write(f'Successfully Saved!')
    
def main():    
    thread_manager = ThreadManager()    
    if not thread_manager.is_running():
        worker = thread_manager.start_worker()
    else:
        worker = thread_manager.get_worker()
        
        if worker.now_playing != None:
            st.markdown(f'{worker.i}')
            st.image(worker.album_cover_image, width=100)
            st.button('♥️', on_click=thread_manager.onLiked)
            st.button('✅', on_click=thread_manager.onSaved)
            st.markdown(f'{worker.track_title} by {worker.artist_name} ({worker.release_date})')
            st.markdown(f'todays play count {worker.playCountToday}')
            st.markdown(f'overall play count {worker.overallPlayCount}')
            st.markdown(f'artist play count {worker.artistPlayCount}')
            st.markdown(f'album play count {worker.albumPlayCount}')
            st.markdown(f'track play count {worker.trackPlayCount}')
        else:
            st.markdown(f'Nothing playing')
            st.markdown(f'{worker.i}')

    st_autorefresh(interval=1000, key="dataframerefresh")


if __name__ == '__main__':
    main()