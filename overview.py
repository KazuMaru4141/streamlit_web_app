import streamlit as st
from SpotifyAPI import SpotifyCtrl

class OverviewController:
    def __init__(self):
        self.sp = SpotifyCtrl
        self.auth_manager, self.spotify = self.sp.create_spotify()
    
    def overviewCtrl(self):
        recentTracks = self.sp.getRecentPlayedTracs(self.spotify)
#        st.write(f'total{recentTracks["items"]}')
        for track in recentTracks["items"]:
            with st.container(border=True):
                col1, col2, col3, col4 = st.columns([1, 4, 1, 6], vertical_alignment="center")
                with col1:
                    st.image({track["track"]["album"]["images"][0]["url"]}, width=70)
                
                with col2:
                    st.markdown(f'{track["track"]["name"]}  \n {track["track"]["artists"][0]["name"]}  \n {track["played_at"]}')
                
                with col3:
                    st.markdown('♥️')
                    
                with col4:
                    pass

