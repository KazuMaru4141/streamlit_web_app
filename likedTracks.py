import streamlit as st
from SpreadSheetAPI import GspreadCtrl

class LovedTracksController:
    def __init__(self):
        self.gc = GspreadCtrl
    
    def likecTracksCtrl(self):
        self.wsLiked, self.wbLiked, self.LikedInfo = self.gc.connect_gspread(st.secrets.SP_SHEET_KEY.Key_LikedSongs)
        
        for track in reversed(self.LikedInfo[-100:]):
            with st.container(border=True):
                col1, col2, col3 = st.columns([1, 4, 7], vertical_alignment="center")
                
                with col1:
                    st.image({track["AlbumImage"]}, width=70)
                
                with col2:
                    st.write(f'{track["TrackName"]}  \n {track["ArtistName"]}  \n {track["SavedAt"]}')
                
                with col3:
                    pass
