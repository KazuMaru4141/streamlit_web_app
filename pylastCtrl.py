import pylast
import streamlit as st
import os
import datetime
import pytz
import pandas as pd

class pylastCtrl:
    def getNetwork():
        api_key = st.secrets.LASTFM_AUTH.API_KEY
        api_securet = st.secrets.LASTFM_AUTH.API_SECRET
        network = pylast.LastFMNetwork(api_key, api_securet)
        network.session_key = st.secrets.LASTFM_AUTH.SESSION_KEY
        
        return network

    def getUser(network):
        username = st.secrets.LASTFM_AUTH.USERNAME
        lastFmUser = network.get_user(username)
        
        return lastFmUser

    def getNowPlaying(user):
        now_playing = user.get_now_playing()

        return now_playing

    def getArtistPlayCount(user, nowPlaying):
        artist = nowPlaying.artist
        artist.username = user
        artistPlayCount = artist.get_userplaycount()
        
        return artistPlayCount
        
    def getAlbumPlayCount(user, nowPlaying):
        album = nowPlaying.get_album()
        album.username = user
        albumPlayCount = album.get_userplaycount()
        
        return albumPlayCount
    
    def getTrackPlayCount(user, nowPlaying):
        TrackPlayCount = nowPlaying.get_userplaycount()
        
        return TrackPlayCount
        
    def getPlayCountToday(user):
        current_time = datetime.datetime.now(tz=pytz.timezone("Asia/Tokyo"))
        start_time = datetime.datetime(current_time.year, current_time.month, current_time.day, 0, 0, 0, 0, tzinfo=pytz.timezone("Asia/Tokyo"))
        
        current_unix_time = int(current_time.timestamp())
        start_unix_time = int(start_time.timestamp())
        play_count = user.get_recent_tracks(limit=400,time_from=start_unix_time, time_to=current_unix_time)

        return len(play_count)

    def getPlayCountThisMonth(user):
        current_time = datetime.datetime.now(tz=pytz.timezone("Asia/Tokyo"))
        start_time = datetime.datetime(current_time.year, current_time.month, 1, 0, 0, 0, 0, tzinfo=pytz.timezone("Asia/Tokyo"))
        
        current_unix_time = int(current_time.timestamp())
        start_unix_time = int(start_time.timestamp())
        play_count = user.get_recent_tracks(limit=None,time_from=start_unix_time, time_to=current_unix_time)

        return len(play_count)
    
    def getAveragePlayCountThisMonth(user):
        current_time = datetime.datetime.now(tz=pytz.timezone("Asia/Tokyo"))
        start_time = datetime.datetime(current_time.year, current_time.month, 1, 0, 0, 0, 0, tzinfo=pytz.timezone("Asia/Tokyo"))
        
        current_unix_time = int(current_time.timestamp())
        start_unix_time = int(start_time.timestamp())
        play_count = user.get_recent_tracks(limit=None,time_from=start_unix_time, time_to=current_unix_time)
        
        # 月の1日から今日までの日数を計算
        days_elapsed = current_time.day
        
        if days_elapsed == 0:
            return 0
        
        average = len(play_count) / days_elapsed
        return round(average, 1)
    
    def getPlayCountThisYear(user):
        current_time = datetime.datetime.now(tz=pytz.timezone("Asia/Tokyo"))
        start_time = datetime.datetime(current_time.year, 1, 1, 0, 0, 0, 0, tzinfo=pytz.timezone("Asia/Tokyo"))
        
        current_unix_time = int(current_time.timestamp())
        start_unix_time = int(start_time.timestamp())
        play_count = user.get_recent_tracks(limit=None,time_from=start_unix_time, time_to=current_unix_time)

        return len(play_count)

    def getOverallPlayCount(user):
        total_scrobbles = user.get_playcount()
        
        return total_scrobbles
    
    def getOverallArtist(user):
        artists = user.get_top_artists(period=pylast.PERIOD_OVERALL, limit=None)
        total_artists = len(artists)
        
        return total_artists

    def getOverallAlbum(user):
        albums = user.get_top_albums(period=pylast.PERIOD_OVERALL, limit=None)
        total_albums = len(albums)
        
        return total_albums

    def getOverallTracks(user):
        tracks = user.get_recent_tracks(limit=None)
        total_tracks = len(tracks)
        
        return total_tracks
    
    def getMonthlyPlayCounts(user):
        current_time = datetime.datetime.now(tz=pytz.timezone("Asia/Tokyo"))
        
        monthly_counts = {}
        month_order = []
        
        # 過去12ヶ月分のデータを取得
        for i in range(11, -1, -1):
            # i ヶ月前の月の開始日と終了日を計算
            if i == 0:
                # 現在の月
                month_start = datetime.datetime(current_time.year, current_time.month, 1, 0, 0, 0, 0, tzinfo=pytz.timezone("Asia/Tokyo"))
                month_end = current_time
            else:
                # i ヶ月前
                month_num = current_time.month - i
                year = current_time.year
                
                if month_num <= 0:
                    month_num += 12
                    year -= 1
                
                month_start = datetime.datetime(year, month_num, 1, 0, 0, 0, 0, tzinfo=pytz.timezone("Asia/Tokyo"))
                
                if month_num == 12:
                    month_end = datetime.datetime(year + 1, 1, 1, 0, 0, 0, 0, tzinfo=pytz.timezone("Asia/Tokyo"))
                else:
                    month_end = datetime.datetime(year, month_num + 1, 1, 0, 0, 0, 0, tzinfo=pytz.timezone("Asia/Tokyo"))
            
            start_unix_time = int(month_start.timestamp())
            end_unix_time = int(month_end.timestamp())
            
            play_count = user.get_recent_tracks(limit=None, time_from=start_unix_time, time_to=end_unix_time)
            month_label = f"{month_start.month}月"
            month_order.append(month_label)
            monthly_counts[month_label] = len(play_count)
        
        # pandasのSeriesで順序を保持して返す
        return pd.Series(monthly_counts, index=month_order)