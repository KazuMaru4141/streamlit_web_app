import streamlit as st
from PIL import Image
import datetime
import sys
import os

# ページディレクトリから実行される場合、親ディレクトリをパスに追加
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from SpotifyAPI import SpotifyCtrl
from SpreadSheetAPI import GspreadCtrl
from spotify_auth import get_auth_manager
import pandas as pd
import numpy as np
import pytz

# ===== 認証フロー処理 =====
auth_manager = get_auth_manager()

# URLパラメータから認証コードを取得
query_params = st.query_params
if 'code' in query_params:
    # 認証コールバックを処理
    code = query_params['code']
    if auth_manager.handle_callback(code):
        st.success("✅ Spotify認証に成功しました！")
        # URLパラメータをクリア
        st.query_params.clear()
        st.rerun()
    else:
        st.error("❌ 認証に失敗しました。もう一度お試しください。")

# 認証状態をチェック
if not auth_manager.is_authenticated():
    st.title("🎵 Spotify Music Manager")
    st.markdown("---")
    st.markdown("### Spotifyアカウントで認証してください")
    st.markdown("このアプリを使用するには、Spotifyアカウントでの認証が必要です。")
    
    # 認証URLを生成
    auth_url = auth_manager.get_auth_url()
    
    # 認証ボタンを表示
    st.markdown(f"[🔐 Spotifyで認証する]({auth_url})")
    st.info("💡 認証後、このページに自動的に戻ります。")
    st.stop()

# ===== 認証済み - 通常のアプリケーション処理 =====

# サイドバーにナビゲーションを追加
st.sidebar.title("📍 Navigation")
st.sidebar.markdown("---")
st.sidebar.markdown("🏠 [main app](/)")
st.sidebar.markdown("📊 [Dashboard](/0_Dashboard)")
st.sidebar.markdown("🎵 [page1](/page1)")
st.sidebar.markdown("🎧 [DeepDive Music Curator](/1_DeepDive_Music_Curator)")
st.sidebar.markdown("---")

sp = SpotifyCtrl
gs = GspreadCtrl
auth_manager, spotify = sp.create_spotify()

# Spotifyクライアントが取得できない場合（トークン期限切れなど）
if spotify is None:
    st.error("❌ Spotify接続エラー。再認証が必要です。")
    if st.button("🔄 再認証"):
        auth_manager.logout()
        st.rerun()
    st.stop()

#st.title('create tweet')

with st.form(key='prifile_form'):
    albumID = st.text_input('Album ID')
    submit_btn = st.form_submit_button('submit')
    
    if (submit_btn == True):
        albumInfo = sp.get_albumInfo(spotify, albumID)
        
        st.text(f'{albumInfo["name"]} by {albumInfo["artists"][0]["name"]}')
        st.text(f'{albumInfo["release_date"]}')
        # st.text(f'アルバム名 : {albumInfo["name"]}')
        # st.text(f'アーティスト名 : {albumInfo["artists"][0]["name"]}')
        
        
        artistInfo = sp.get_artistInfo(spotify, albumInfo["artists"][0]["id"])
        if artistInfo["genres"] != []:
            st.text(f'ジャンル:{", ".join(artistInfo["genres"])}')
        else:
            st.text(f'ジャンル:-')
            
        # relatedArtistInfo = sp.get_related_artistInfo(spotify, albumInfo["artists"][0]["id"])
        # count = 0
        # outRelatedArtist = []
        # for artist in relatedArtistInfo["artists"]:
        #     outRelatedArtist.append(artist["name"])
        #     count = count + 1
        #     if count >= 3:
        #         break
        
        # if outRelatedArtist != []:
        #     st.text(f'関連アーティスト:{", ".join(outRelatedArtist)}')
        # else:
        #     st.text(f'関連アーティスト:-')
        
        dt_now = dt_now = datetime.datetime.now(tz=pytz.timezone("Asia/Tokyo"))
        year = str(dt_now.year)
        #st.write(f'')
        st.text(f'#NewAlbum_{year}')
        st.text(f'#WeeklyFeaturedAlbum')
#        st.text(f'#今週良さそう')
        st.text(f'#新譜')
        st.write(f'{albumInfo["external_urls"]["spotify"]}')
        
with st.form(key='prifile_form2'):
    dt_now = dt_now = datetime.datetime.now(tz=pytz.timezone("Asia/Tokyo"))
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
    
        
        
