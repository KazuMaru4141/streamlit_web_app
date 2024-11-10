import dataclasses
import threading
import time

import streamlit as st
from streamlit_autorefresh import st_autorefresh
from streamlit_gsheets import GSheetsConnection
from pylastCtrl import pylastCtrl
import pylast

class Worker(threading.Thread):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.pc = pylastCtrl
        self.lastfm_network = self.pc.getNetwork()
        self.lastfm_user = self.pc.getUser(self.lastfm_network)
        self.playCountToday = self.pc.getPlayCountToday(self.lastfm_user)
        self.overallPlayCount = self.pc.getOverallPlayCount(self.lastfm_user)        
        self.now_playing = self.pc.getNowPlaying(self.lastfm_user)
        
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

#@st.experimental_singleton
@st.cache_resource
@dataclasses.dataclass
class ThreadManager:
    worker = None
    
    def get_worker(self):
        return self.worker
    
    def is_running(self):
        return self.worker is not None and self.worker.is_alive()
    
    def start_worker(self):
        if self.worker is not None:
            self.stop_worker()
        self.worker = Worker(daemon=True)
        self.worker.start()
        return self.worker
    
    def stop_worker(self):
        self.worker.stop_req.set()
        self.worker.join()
        self.worker = None

def main():
    conn = st.connection("gsheets", type=GSheetsConnection)
    df = conn.read()
    for row in df.itertuples():
        st.write(f"{row.TrackName}")
    
    thread_manager = ThreadManager()

    with st.sidebar:
        if st.button('Start worker', disabled=thread_manager.is_running()):
            worker = thread_manager.start_worker()
#            st.experimental_rerun()
            
        if st.button('Stop worker', disabled=not thread_manager.is_running()):
            thread_manager.stop_worker()
#            st.experimental_rerun()
    
    if not thread_manager.is_running():
        st.markdown('No worker running.')
    else:
        worker = thread_manager.get_worker()
        
        if worker.now_playing != None:
            st.image(worker.album_cover_image, width=100)  
            st.markdown(f'{worker.track_title} by {worker.artist_name} ({worker.release_date})')
            st.markdown(f'todays play count {worker.playCountToday}')
            st.markdown(f'overall play count {worker.overallPlayCount}')
            st.markdown(f'artist play count {worker.artistPlayCount}')
            st.markdown(f'album play count {worker.albumPlayCount}')
            st.markdown(f'track play count {worker.trackPlayCount}')
        else:
            st.markdown(f'Nothing playing')

    st_autorefresh(interval=1000, key="dataframerefresh")


if __name__ == '__main__':
    main()