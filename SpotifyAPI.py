import streamlit as st
import spotipy
import spotipy.util as util
from spotipy.oauth2 import SpotifyClientCredentials
from spotipy.oauth2 import SpotifyOAuth



class SpotifyCtrl:
    def create_spotify():
        SCOPE = 'user-library-read user-read-playback-state playlist-read-private user-read-recently-played playlist-read-collaborative playlist-modify-public playlist-modify-private'
        
        auth_manager = SpotifyOAuth(
        scope=SCOPE,
        username=st.secrets.SPOTIFY_AUTH.my_user_name,
        redirect_uri=st.secrets.SPOTIFY_AUTH.redirect_url,
        client_id=st.secrets.SPOTIFY_AUTH.my_id,
        client_secret=st.secrets.SPOTIFY_AUTH.my_secret)
        
        spotify = spotipy.Spotify(auth_manager=auth_manager)

        return auth_manager, spotify
    
    def get_albumInfo(spotify, albumID):
        albumInfo = spotify.album(albumID)
        return albumInfo

    def get_artistInfo(spotify, artistID):
        artistInfo = spotify.artist(artistID)
        return artistInfo

    def get_related_artistInfo(spotify, artistID):
        relatedArtistInfo = spotify.artist_related_artists(artistID)
        return relatedArtistInfo
    
    def addLikedTrackToPlaylist(spotify, trackUri):
        playlist_url = "https://open.spotify.com/playlist/2301nL49ZNwH1ntcUrfDf1?si=7a0eae278a3c44a6"
        trackList = []
        trackList.append(trackUri)
        spotify.user_playlist_add_tracks(st.secrets.SPOTIFY_AUTH.my_user_name, playlist_url, trackList)
