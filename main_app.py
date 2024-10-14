import streamlit as st
from PIL import Image
import datetime
from SpotifyAPI import SpotifyCtrl
from SpreadSheetAPI import GspreadCtrl
import pandas as pd
import numpy as np

sp = SpotifyCtrl
gs = GspreadCtrl
auth_manager, spotify = sp.create_spotify()

st.title('crate tweet')

with st.form(key='prifile_form'):
    albumID = st.text_input('Album ID')
    submit_btn = st.form_submit_button('submit')
    
    if (submit_btn == True):
        albumInfo = sp.get_albumInfo(spotify, albumID)
        
        st.write(f'{albumInfo["name"]} by {albumInfo["artists"][0]["name"]}')
        st.write(f'{albumInfo["release_date"]}')
        # st.text(f'アルバム名 : {albumInfo["name"]}')
        # st.text(f'アーティスト名 : {albumInfo["artists"][0]["name"]}')
        
        
        artistInfo = sp.get_artistInfo(spotify, albumInfo["artists"][0]["id"])
        if artistInfo["genres"] != []:
            st.text(f'ジャンル {", ".join(artistInfo["genres"])}')
        else:
            st.text(f'ジャンル -')
            
        relatedArtistInfo = sp.get_related_artistInfo(spotify, albumInfo["artists"][0]["id"])
        count = 0
        outRelatedArtist = []
        for artist in relatedArtistInfo["artists"]:
            outRelatedArtist.append(artist["name"])
            count = count + 1
            if count >= 3:
                break
        
        if outRelatedArtist != []:
            st.text(f'関連アーティスト {", ".join(outRelatedArtist)}')
        else:
            st.text(f'関連アーティスト -')
        
        dt_now = dt_now = datetime.datetime.now()
        year = str(dt_now.year)
        st.text(f'')
        st.text(f'#NewAlbum_{year}')
        st.text(f'#WeeklyFeaturedAlbum')
#        st.text(f'#今週良さそう')
        st.text(f'#新譜')
        st.write(f'{albumInfo["external_urls"]["spotify"]}')
        
with st.form(key='prifile_form2'):
    dt_now = dt_now = datetime.datetime.now()
    today = str(dt_now.year) + "-" + str(dt_now.month) + "-" + str(dt_now.day)
    date = st.text_input('Date', value=today)
    update_btn = st.form_submit_button('update')
    
    if (update_btn == True):
        
        SP_SHEET_KEY = st.secrets.SP_SHEET_KEY.key_SpotifySavedAlbums
        ws, wb, SpreadInfo = gs.connect_gspread(SP_SHEET_KEY)
        
        featuredAlbum = []
        for album in SpreadInfo:
            if date in album["SavedAt"]:
                featuredAlbum.append([
                    album["AlbumID"],
                    album["AlbumName"],
                    album["ArtistName"],
                    album["ReleaseDate"]
                    
                ])
        
        if featuredAlbum != None:   
            df = pd.DataFrame(featuredAlbum, columns=["ID", "AlbumName", "ArtistName", "Release"])
            #st.write(df)
            st.dataframe(df)
                #st.text(f'{album["AlbumName"]} by {album["ArtistName"]}, {album["AlbumID"]}')
    
        
        
