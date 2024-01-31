import spotipy
import spotipy.util as util
from spotipy.oauth2 import SpotifyClientCredentials
from spotipy.oauth2 import SpotifyOAuth

#Spotify Authorization
MY_USER_NAME = "kazmaru"
MY_ID = '38537f7c27b84471b27a018c58a582b5'
MY_SECRET = '8aea8e2036ab4e78a8d10f6cab425a18'
REDIRECT_URI = 'http://localhost:8888/callback'

class SpotifyCtrl:
    def create_spotify():
        SCOPE = 'user-library-read user-read-playback-state playlist-read-private user-read-recently-played playlist-read-collaborative playlist-modify-public playlist-modify-private'
        
        auth_manager = SpotifyOAuth(
        scope=SCOPE,
        username=MY_USER_NAME,
        redirect_uri=REDIRECT_URI,
        client_id=MY_ID,
        client_secret=MY_SECRET)

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
