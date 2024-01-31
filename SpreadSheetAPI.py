import gspread
import json
import os.path
import requests
from oauth2client.service_account import ServiceAccountCredentials

"""
Spread sheet Authorization
"""
JSON_FILENAME = "gspread-sheet-python-409905-42d319678b7f.json"

class GspreadCtrl:
    #Spotify Saved Albums
    SPOTIFY_SAVED_ALBUMS = "1XTFHPaq_8psiZENSUkdfegPJqlwRzlpCmFRtO9aXRXk"
    #Liked Songs
    LIKED_SONGS = "1rNxcX9RHgZ4Qi_3L7LQ88_HtZIo8jVgZOjof377qTBM"
    #Album Of The Year
    ALBUM_OF_THE_YEAR = "1LNVhjlzgU98Jb6cncIm3ftxzOYGivXoNW7rAgRhGGvw"
    #Spotify Saved Albums 旧譜
    SPOTIFY_SAVED_ALBUMS_OLD = "1zNf9n4AusAeeGpDj8ESna8UeDBSCfFF15Yx1xjeUidw"
    
    def connect_gspread(key):
        scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
        jsonf = JSON_FILENAME
        
        credentials = ServiceAccountCredentials.from_json_keyfile_name(jsonf, scope)
        gc = gspread.authorize(credentials)
        
        SPREADSHEET_KEY = key
        workbook = gc.open_by_key(key)
        worksheet = gc.open_by_key(key).sheet1
        
        SpreadInfo = worksheet.get_all_records()
        
        return worksheet, workbook, SpreadInfo

"""
    def import_gspread(SheetKey):
        jsonf = JSON_FILENAME
        spread_sheet_key = SheetKey
        ws, wb = connect_gspread(jsonf,spread_sheet_key)

        SpreadInfo = ws.get_all_records()
        #print(SpreadInfo)
        return ws, wb, SpreadInfo
"""
