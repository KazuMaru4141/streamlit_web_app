import streamlit as st
from operator import itemgetter
from SpreadSheetAPI import GspreadCtrl
import pandas as pd
import numpy as np
import datetime

def CountLikedSongs(AllLikedSongs):
    AlbumLikedCount = {}
    for LikedSongs in AllLikedSongs:
        AlbumName = LikedSongs["AlbumName"]

        if AlbumName in AlbumLikedCount:
            AlbumLikedCount[AlbumName]["LikedCount"] = AlbumLikedCount[AlbumName]["LikedCount"] + 1
        else:
            AlbumLikedCount[AlbumName] = {}
            AlbumLikedCount[AlbumName]["LikedCount"] = 1
            AlbumLikedCount[AlbumName]["ArtistName"] = LikedSongs["ArtistName"]
            AlbumLikedCount[AlbumName]["AlbumImage"] = LikedSongs["AlbumImage"]
            #AlbumLikedCount[AlbumName]["ReleaseDate"] = LikedSongs["ReleaseDate"]
    
    return AlbumLikedCount

# Main
gs = GspreadCtrl

with st.form(key='prifile_form'):
    udpate_btn = st.form_submit_button('update')
    if udpate_btn == True:
        
        SP_SHEET_KEY = st.secrets.SP_SHEET_KEY.Key_LikedSongs
        ws, wb, LikedInfo = gs.connect_gspread(SP_SHEET_KEY)
        
        SP_SHEET_KEY = st.secrets.SP_SHEET_KEY.key_SpotifySavedAlbumOld
        ws, wb, AlbumInfo = gs.connect_gspread(SP_SHEET_KEY)
        #print(AlbumInfo)
        CountedAlbum = CountLikedSongs(LikedInfo)
        
        list = []
        for album in CountedAlbum.items():
            #print(album)
            append = {}
            append["AlbumName"] = album[0]
            append["ArtistName"] = album[1]["ArtistName"]
            append["AlbumImage"] = album[1]["AlbumImage"]
            #append["ReleaseDate"] = album[1]["ReleaseDate"]
            append["LikedCount"] = album[1]["LikedCount"]
            
            append["ReleaseDate"] = ""
            append["TrackNumber"] = 0
            for info in AlbumInfo:
                if album[0] == info["AlbumName"]:
                    append["ReleaseDate"] = info["ReleaseDate"]
                    append["TrackNumber"] = int(info["TrackNumber"])
                    #print(info["TrackNumber"])
            
            list.append(append)
            #print(append)
        
        sortedList = sorted(list, key=itemgetter('LikedCount'), reverse=True)
        
        ranking = []
        for album in sortedList:
            #print(album["AlbumName"])
            if int(album["TrackNumber"]) > 0:
                rate = int(album["LikedCount"]) / int(album["TrackNumber"]) * 100
            else:
                rate = 0.0
            ranking.append([
                album["AlbumName"],
                album["ArtistName"],
                album["ReleaseDate"],
                album["TrackNumber"],
                album["LikedCount"],
                rate
            ])
        
        dt_now = datetime.datetime.now()
        rankingThisYear = []
        for album in sortedList:
            if str(dt_now.year) in str(album["ReleaseDate"]):
                if int(album["TrackNumber"]) > 0:
                    rate = int(album["LikedCount"]) / int(album["TrackNumber"]) * 100
                else:
                    rate = 0.0
                
                rankingThisYear.append([
                    album["AlbumName"],
                    album["ArtistName"],
                    album["TrackNumber"],
                    album["LikedCount"],
                    rate
                ])
        
        
        #sortedList = sorted(list, key="LikedCount")
        #print(sorted)
        df = pd.DataFrame(ranking, columns=["AlbumName", "ArtistName", "ReleaseDate", "TrackNumber", "LikedCount", "Rate"])
        dfThisYear = pd.DataFrame(rankingThisYear, columns=["AlbumName", "ArtistName", "TrackNumber", "LikedCount", "Rate"])

        st.text(f'2024ランキング')
        st.write(dfThisYear)
        
        st.text(f'総合ランキング')
        st.write(df)
        
        
        #for album in sortedList:
        #    st.text(f'{album["AlbumName"]} by {album["ArtistName"]}, {album["LikedCount"]}')