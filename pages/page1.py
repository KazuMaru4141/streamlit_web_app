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

def getCurrentDateTime():
    """
    現在の日時を取得
    
    Returns:
        str: "YYYY-MM-DD HH:MM:SS" 形式の日時文字列
    """
    dt_now = datetime.datetime.now(tz=pytz.timezone("Asia/Tokyo"))
    return f"{dt_now.year}-{dt_now.month}-{dt_now.day} {dt_now.hour:02d}:{dt_now.minute:02d}:{dt_now.second:02d}"

def initSessionState(st):
    """
    Streamlitセッション状態を初期化
    
    曲情報、再生カウント、Googleスプレッドシート接続情報などの
    セッション変数を初期化
    
    Args:
        st: Streamlitモジュール
    """
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
    
    if 'OldAlbumInfo' not in st.session_state:
        st.session_state.OldAlbumInfo = []
    
    if 'ws_old' not in st.session_state:
        st.session_state.ws_old = None
    
    if 'wb_old' not in st.session_state:
        st.session_state.wb_old = None
    
def updateSessionState(st):
    """
    セッション状態を現在再生中の曲情報で更新
    
    Spotifyから現在再生中の曲情報を取得し、セッション状態に保存
    Last.fmから再生回数などの統計情報も取得
    
    Args:
        st: Streamlitモジュール
    """
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
    """
    現在再生中の曲をお気に入り曲として保存
    
    Googleスプレッドシート「LikedSongs」に曲情報を追加または更新
    スポティファイのお気に入りプレイリストにも追加
    
    初回追加時：新規行として追加
    既に存在する場合：再生回数をインクリメント
    """
    gs = GspreadCtrl
    SP_SHEET_KEY = st.secrets.SP_SHEET_KEY.Key_LikedSongs
    ws, wb, LikedInfo = gs.connect_gspread(SP_SHEET_KEY)
    trackIdList = ws.col_values(6)
    
    if st.session_state.trackInfo["trackID"] not in trackIdList: 
        today = getCurrentDateTime()
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
    """
    現在再生中のアルバムを保存済みアルバムとして記録
    
    Googleスプレッドシート「OldAlbums」にアルバム情報を追加
    アルバム画像、アーティスト情報、リリース日などを記録
    Featured列にTRUEを設定
    
    既に存在する場合は追加しないが、FeaturedがTRUEでない場合はTRUEに更新
    
    Args:
        なし
    """        
    # アルバムIDのリストを取得（G列 = 7列目）
    albumIdList = st.session_state.ws_old.col_values(7)
    
    # アルバムが既に存在するかチェック
    if st.session_state.trackInfo["albumID"] not in albumIdList:
        today = getCurrentDateTime()
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
            "",
            "",
            "TRUE"  # W列: Featured Key
        ])
        st.session_state.ws_old.append_rows(appendList)
        st.write(f'Successfully Saved!')
        # セッション状態を更新
        st.session_state.OldAlbumInfo = st.session_state.ws_old.get_all_records()
    else:
        # アルバムが既に存在する場合、Featured列をチェック
        cell = st.session_state.ws_old.find(st.session_state.trackInfo["albumID"])
        row = int(cell.row)
        
        # W列（23列目）のFeatured値を取得
        featured_value = st.session_state.ws_old.cell(row, 23).value
        
        # FeaturedがTRUEでない場合、TRUEに更新
        if featured_value != "TRUE":
            st.session_state.ws_old.update_cell(row, 23, "TRUE")
            st.write(f'Featured Updated to TRUE!')
            # セッション状態を更新
            st.session_state.OldAlbumInfo = st.session_state.ws_old.get_all_records()
        else:
            st.write(f'Already Saved!')

def onclickAddToQueue(trackUri, trackName):
    """
    トラックをSpotifyのキューに追加
    
    Args:
        trackUri (str): トラックURI
        trackName (str): トラック名
    """
    # if sp.add_track_to_queue(spotify, trackUri):
    #     st.toast(f"Queued: {trackName}", icon="➕")

def readSpreadSheet(st):
    """
    Googleスプレッドシートを読み込んでセッション状態に保存
    
    LikedSongsシートから曲情報を読み込み
    初回読み込み時のみ実行（キャッシング）
    
    Args:
        st: Streamlitモジュール
    """
    if st.session_state.gs == None:
        with st.spinner("Loading..."):
            st.session_state.gs = GspreadCtrl
            st.session_state.ws, st.session_state.wb, st.session_state.LikedInfo = st.session_state.gs.connect_gspread(st.secrets.SP_SHEET_KEY.Key_LikedSongs)
            # Load Old Albums data
            st.session_state.ws_old, st.session_state.wb_old, st.session_state.OldAlbumInfo = st.session_state.gs.connect_gspread(st.secrets.SP_SHEET_KEY.key_SpotifySavedAlbumOld)

def display_track_info(st):
    """
    トラック情報と評価を表示・更新
    
    現在再生中の曲の情報を表示し、ユーザーが評価（星）を付けられる
    初回の場合は新規追加、既存の場合は評価を更新
    
    Args:
        st: Streamlitモジュール
    """
    with st.container(border=True):
        st.markdown("### Track")
        st.image(st.session_state.trackInfo["albumImg"], width=70) 
    #    st.button('♥️', on_click=onclickLiked)
        
        # 保存済みかチェック（AlbumIDが一致し、かつFeaturedキーがTRUEのもの）
        is_saved = any(
            st.session_state.trackInfo["albumID"] in album.values() and 
            (album.get("Featured") == "TRUE" or album.get("Featured Key") == "TRUE")
            for album in st.session_state.OldAlbumInfo
        )
        
        if is_saved:
            # 保存済みの場合はアイコン（非ボタン）を表示
            st.markdown("📁 Already Saved")
        else:
            # 未保存の場合は保存ボタンを表示
            st.button('✅', on_click=onclickSaved)
            
        st.write(f'__{st.session_state.trackInfo["trackName"]}__ by __{st.session_state.trackInfo["artistName"]}__ ({st.session_state.trackInfo["releaseDate"]})')
        st.markdown(f'🎤 {st.session_state.playCount["artistPlayCount"]} &nbsp; &nbsp; 💿 {st.session_state.playCount["albumPlayCount"]}  &nbsp; &nbsp; 🎵 {st.session_state.playCount["track_play_count"]}  \n ⏭️ {st.session_state.playCount["playCountToday"]} &nbsp; &nbsp; &nbsp; ▶️ {st.session_state.playCount["OverallPlayCount"]}')    
            
        star_options = {
            "★": 1,
            "★★" : 2,
            "★★★" : 3, 
            "★★★★" : 4, 
            "★★★★★" : 5
        }
        trackIdList = st.session_state.ws.col_values(6)
        
        # トラックIDがスプレッドシートに存在するか確認
        if st.session_state.trackInfo["trackID"] in trackIdList:
            cell = st.session_state.ws.find(st.session_state.trackInfo["trackID"])
            row = int(cell.row)
            
            # A列に再生日付を更新
            today = getCurrentDateTime()
            st.session_state.ws.update_cell(row, 1, today)
            
            current_rate = int(st.session_state.ws.cell(row, 9).value)
        else:
            # 新規トラックの場合、スプレッドシートに追加
            today = getCurrentDateTime()
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
                st.session_state.trackInfo["albumID"],
            ])
            st.session_state.ws.append_rows(appendList)
            
            cell = st.session_state.ws.find(st.session_state.trackInfo["trackID"])
            row = int(cell.row)
            current_rate = 2
        
        # 評価の表示と取得（共通処理）
        rate = st.radio("Rate", 
            ["★", "★★", "★★★", "★★★★", "★★★★★"],
            index=(current_rate-1),
            key=f"rating_{st.session_state.trackInfo['trackID']}"
        )
        rate = star_options[rate]
        
#        print(f'current_rate: {current_rate}, rate: {rate}')
        
        # LikedInfo内の評価を更新
        flg = False
        for likedSong in st.session_state.LikedInfo:
            if st.session_state.trackInfo["trackID"] == likedSong["TrackID"]:
                likedSong["Rating"] = rate
                flg = True
                break
        
        # LikedInfoに存在しない場合は追加
        if not flg:
            today = getCurrentDateTime()
            appendDict = {
                "SavedAt": today,
                "trackName": st.session_state.trackInfo["trackName"],
                "AlbumName": st.session_state.trackInfo["albumName"],
                "ArtistName": st.session_state.trackInfo["artistName"],
                "AlbumImage": st.session_state.trackInfo["albumImg"],
                "TrackID": st.session_state.trackInfo["trackID"],
                "TrackSrc": "",
                "TrackURL": st.session_state.trackInfo["trackURL"],
                "Rating": rate,
                "AlbumId": st.session_state.trackInfo["albumID"]
            }
            st.session_state.LikedInfo.append(appendDict)
        
        # 評価が変更された場合、スプレッドシートを更新
        if (current_rate != rate):    
            st.success("rating updated")
            st.session_state.ws.update_cell(row, 9, rate)

def display_album_info(st):
    """
    アルバム情報を表示
    
    アルバムの詳細情報（名前、スコア、リリース日、ジャンル）と
    各トラックの評価一覧を表示
    
    Args:
        st: Streamlitモジュール
    """
    with st.container(border=True):
        st.markdown("### Album")
        track_point = {
            1: 0,
            2: 10, 
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
            dispAlbum.append(["Score", f"{average:.1f}"])
            dispAlbum.append(["Release Date", str(st.session_state.trackInfo["releaseDate"])])
            dispAlbum.append(["Genre", ", ".join(st.session_state.trackInfo["genre"])])
            dataframe = pd.DataFrame(dispAlbum)
            st.table(dataframe)
            
            # トラックリストをインタラクティブに表示
            st.markdown("#### Tracks")
            
            # ヘッダー
            col1, col2, col3, col4 = st.columns([0.5, 4, 2, 1])
            col1.write("**#**")
            col2.write("**Track Name**")
            col3.write("**Rate**")
            col4.write("**Queue**")
            
            cnt = 1
            for track in st.session_state.trackInfo["albumTracks"]["items"]:
                trackname = track["name"]
                trackid = track["id"]
                trackuri = track["uri"]
                
                current_rate = 0
                for likedSong in st.session_state.LikedInfo:
                    if trackid == likedSong["TrackID"]:
                        current_rate = likedSong["Rating"]
                
                disp = disp_rate[current_rate]
                
                c1, c2, c3, c4 = st.columns([0.5, 4, 2, 1])
                c1.write(str(cnt))
                c2.write(trackname)
                c3.write(disp)
                c4.button("➕", key=f"q_{trackid}", on_click=onclickAddToQueue, args=(trackuri, trackname))
                cnt += 1
            
            st.write(f'total point {album_rate}')

def display_artist_info(st):
    """
    アーティスト情報を表示
    
    アーティストの名前、人気度、フォロワー数、画像、Spotifyリンクを表示
    
    Args:
        st: Streamlitモジュール
    """
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

############### Main #######################################
#st.write(f'#### Now Playing')
initSessionState(st)
readSpreadSheet(st)

auth_manager, spotify = sp.create_spotify()

currentTrack = spotify.current_user_playing_track()

if currentTrack != None:
    updateSessionState(st)
    
    # 各セクションを関数で表示
    display_track_info(st)
    display_album_info(st)
    display_artist_info(st)
else:
    st.text(f'Track is not playing')
    
# update every 15sec
st_autorefresh(interval=15000, key="dataframerefresh")
