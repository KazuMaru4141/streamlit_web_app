import streamlit as st
from SpotifyAPI import SpotifyCtrl
from pylastCtrl import pylastCtrl
from SpreadSheetAPI import GspreadCtrl
import threading
import logging

class OverviewController:
    def __init__(self):
        self.sp = SpotifyCtrl
        self.auth_manager, self.spotify = self.sp.create_spotify()
        self.network = pylastCtrl.getNetwork()
        self.user = pylastCtrl.getUser(self.network)
        # スプレッドシートから LikedInfo を取得
        gc = GspreadCtrl
        self.wsLiked, self.wbLiked, self.LikedInfo = gc.connect_gspread(st.secrets.SP_SHEET_KEY.Key_LikedSongs)
    
    def overviewCtrl(self):
        # リフレッシュボタン
        # col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
        # with col1:
        #     if st.button("🔄 Refresh", use_container_width=True):
        #         st.rerun()
        
        # st.divider()
        
        # rating 表示用の辞書
        disp_rate = {
            0: "☆☆☆☆☆",
            1: "★☆☆☆☆", 
            2: "★★☆☆☆", 
            3: "★★★☆☆", 
            4: "★★★★☆",
            5: "★★★★★",
            "1": "★☆☆☆☆", 
            "2": "★★☆☆☆", 
            "3": "★★★☆☆", 
            "4": "★★★★☆",
            "5": "★★★★★"
        }
        
        # 現在再生中の曲を表示
        current_playback = self.spotify.current_playback()
        if current_playback and current_playback.get("item"):
            track = current_playback["item"]
            # st.markdown("### 🎵 Now Playing")
            with st.container(border=True):
                col1, col2, col3 = st.columns([1, 4, 5], vertical_alignment="center")
                with col1:
                    st.image({track["album"]["images"][0]["url"]}, width=50)
                
                with col2:
                    st.markdown(f'[{track["name"]}]({track["external_urls"]["spotify"]})  \n [{track["artists"][0]["name"]}]({track["artists"][0]["external_urls"]["spotify"]})')
                
                with col3:
                    # スプレッドシートから rating を取得
                    track_id = track["id"]
                    rating = 0
                    row = None
                    for idx, liked_song in enumerate(self.LikedInfo):
                        if liked_song.get("TrackID") == track_id:
                            rating = liked_song.get("Rating", 0)
                            break
                    
                    # track がスプレッドシートにない場合は追加
                    if rating == 0 and track_id not in [s.get("TrackID") for s in self.LikedInfo]:
                        # 新規行として追加
                        import datetime
                        import pytz
                        dt_now = datetime.datetime.now(tz=pytz.timezone("Asia/Tokyo"))
                        today = f"{dt_now.year}-{dt_now.month}-{dt_now.day} {dt_now.hour:02d}:{dt_now.minute:02d}:{dt_now.second:02d}"
                        
                        appendList = [[
                            today,
                            track["name"],
                            track["album"]["name"],
                            track["artists"][0]["name"],
                            track["album"]["images"][0]["url"],
                            track_id,
                            "",
                            track["external_urls"]["spotify"],
                            2,
                            track["album"]["id"]
                        ]]
                        self.wsLiked.append_rows(appendList)
                        rating = 2
                    
                    # rating 更新用の操作
                    star_options = {
                        "★": 1,
                        "★★": 2, 
                        "★★★": 3, 
                        "★★★★": 4, 
                        "★★★★★": 5
                    }
                    
                    selected_rate = st.radio(
                        "Rate",
                        ["★", "★★", "★★★", "★★★★", "★★★★★"],
                        index=(rating - 1) if rating > 0 else 1,
                        key=f"rating_{track_id}"
                    )
                    
                    new_rating = star_options[selected_rate]
                    
                    # スプレッドシートで track を探す
                    trackIdList = self.wsLiked.col_values(6)
                    if track_id in trackIdList:
                        cell = self.wsLiked.find(track_id)
                        # AlbumId は常に更新
                        self.wsLiked.update_cell(cell.row, 10, track["album"]["id"])
                        
                        # rating が変更された場合、rating も更新
                        if rating != new_rating:
                            self.wsLiked.update_cell(cell.row, 9, new_rating)
                            # LikedInfo も更新
                            for liked_song in self.LikedInfo:
                                if liked_song.get("TrackID") == track_id:
                                    liked_song["Rating"] = new_rating
                                    break
                            st.success("Rating updated!")
                            st.rerun()
            
            # アルバム内の全曲を表示（タイムアウト5秒）
            st.markdown(f"### 💿 {track['album']['name']}")
            album_id = track["album"]["id"]
            
            album_tracks_result = {"data": None, "completed": False, "rate_limited": False}
            
            def fetch_album_tracks():
                try:
                    album_tracks_result["data"] = self.spotify.album_tracks(album_id)
                    album_tracks_result["completed"] = True
                except Exception as e:
                    error_msg = str(e).lower()
                    # レート制限エラーをチェック
                    if "rate" in error_msg or "limit" in error_msg or "429" in error_msg:
                        album_tracks_result["rate_limited"] = True
                    album_tracks_result["completed"] = False
            
            # スレッドでアルバムトラック取得
            thread = threading.Thread(target=fetch_album_tracks, daemon=True)
            thread.start()
            thread.join(timeout=5)  # 5秒でタイムアウト
            
            if album_tracks_result["completed"] and album_tracks_result["data"]:
                for album_track in album_tracks_result["data"]["items"]:
                    album_track_id = album_track["id"]
                    album_track_name = album_track["name"]
                    
                    # rating を取得
                    album_rating = 0
                    for liked_song in self.LikedInfo:
                        if liked_song.get("TrackID") == album_track_id:
                            album_rating = liked_song.get("Rating", 0)
                            break
                    
                    rating_str = disp_rate.get(album_rating, "☆☆☆☆☆")
                    st.write(f"{album_track_name} {rating_str}")
            elif album_tracks_result["rate_limited"]:
                st.warning("API rate limit reached - skipping album tracks")
            else:
                st.info("Album tracks loading timed out - please try again later")
                            
            st.divider()
        
        # タブを作成
        tab1, tab2 = st.tabs(["Recently Played", "Statistics"])
        
        with tab1:
            # st.markdown("### 📜 Recently Played")
            recentTracks = self.sp.getRecentPlayedTracs(self.spotify)
            
#        st.write(f'total{recentTracks["items"]}')
            for track in recentTracks["items"]:
                with st.container(border=True):
                    col1, col2, col3, col4 = st.columns([1, 4, 2, 5], vertical_alignment="center")
                    with col1:
                        st.image({track["track"]["album"]["images"][0]["url"]}, width=50)
                    
                    with col2:
                        st.markdown(f'[{track["track"]["name"]}]({track["track"]["external_urls"]["spotify"]})  \n [{track["track"]["artists"][0]["name"]}]({track["track"]["artists"][0]["external_urls"]["spotify"]})  \n {track["played_at"]}')
                    
                    with col3:
                        # スプレッドシートから rating を取得
                        track_id = track["track"]["id"]
                        rating = 0
                        for liked_song in self.LikedInfo:
                            if liked_song.get("TrackID") == track_id:
                                rating = liked_song.get("Rating", 0)
                                break
                        rating_str = disp_rate.get(rating, "☆☆☆☆☆")
                        st.markdown(f'**{rating_str}**')
                    
                    with col4:
                        pass
        
        with tab2:
            st.markdown("### 📊 Play Count Statistics")
            col1, col2, col3, col4, col5 = st.columns(5)
            
            with col1:
                play_count_today = pylastCtrl.getPlayCountToday(self.user)
                st.metric("Today", play_count_today)
            
            with col2:
                play_count_month = pylastCtrl.getPlayCountThisMonth(self.user)
                st.metric("This Month", play_count_month)
            
            with col3:
                avg_play_count_month = pylastCtrl.getAveragePlayCountThisMonth(self.user)
                st.metric("This Month Avg", avg_play_count_month)
            
            with col4:
                play_count_year = pylastCtrl.getPlayCountThisYear(self.user)
                st.metric("This Year", play_count_year)
            
            with col5:
                play_count_overall = pylastCtrl.getOverallPlayCount(self.user)
                st.metric("All Time", play_count_overall)