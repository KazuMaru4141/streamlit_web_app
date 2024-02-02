import streamlit as st
from SpreadSheetAPI import GspreadCtrl
import datetime

st.title('Get New Release')

with st.form(key='prifile_form'):    
    date = st.text_input('Date')
    dt_now = dt_now = datetime.datetime.now()
    today = str(dt_now.year) + str(dt_now.month) + str(dt_now.day)
    st.text(today)
    update_btn = st.form_submit_button('update')
    
    if update_btn == True:
        gs = GspreadCtrl
        SP_SHEET_KEY = st.secrets.SP_SHEET_KEY.key_NewRelease
        ws, wb, SpreadInfo = gs.connect_gspread(SP_SHEET_KEY)
        
        for album in SpreadInfo:
            if str(date) in str(album["SavedAt"]):
                img = album["AlbumImage"].replace('=IMAGE("', "")
                img = img.replace('",1)', "")
                
                #print("fdsfdsfdfsdfdsfdsfdsfdsfd")
                #print(img)
                st.image(img, width=200)
                st.text(f'Album Name : {album["AlbumName"]} ({album["Type"]})')
                st.text(f'Artist Name : {album["ArtistName"]}')
                album["AlbumURL"]
                st.text(f'Genre : {album["Genre"]}')
                st.text(f'Release Date : {album["ReleaseDate"]}')
        
    
    