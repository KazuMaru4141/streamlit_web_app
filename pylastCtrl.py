import pylast
import streamlit as st
import os
import datetime
from tzlocal import get_localzone

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
        ja = get_localzone()
        current_time = datetime.datetime.now(tz=ja)
        start_time = datetime.datetime(current_time.year, current_time.month, current_time.day, 0, 0, 0, 0)

        current_unix_time = int(current_time.timestamp())
        start_unix_time = int(start_time.timestamp())
        play_count = user.get_recent_tracks(limit=400,time_from=start_unix_time, time_to=current_unix_time)

        return len(play_count)