import streamlit as st
import spotipy
import spotipy.util as util
from spotipy.oauth2 import SpotifyClientCredentials
from spotipy.oauth2 import SpotifyOAuth

class SpotifyCtrl:
    def create_spotify():
        """
        Spotifyクライアントを初期化して認証情報を取得
        
        Returns:
            tuple: (auth_manager, spotify) - 認証マネージャーとSpotifyクライアント
        """
        SCOPE = 'user-library-read user-read-playback-state user-modify-playback-state playlist-read-private user-read-recently-played playlist-read-collaborative playlist-modify-public playlist-modify-private'
        
        auth_manager = SpotifyOAuth(
        scope=SCOPE,
        username=st.secrets.SPOTIFY_AUTH.my_user_name,
        redirect_uri=st.secrets.SPOTIFY_AUTH.redirect_url,
        client_id=st.secrets.SPOTIFY_AUTH.my_id,
        client_secret=st.secrets.SPOTIFY_AUTH.my_secret)
        
        spotify = spotipy.Spotify(auth_manager=auth_manager)

        return auth_manager, spotify
    
    def get_albumInfo(spotify, albumID):
        """
        アルバム情報を取得
        
        Args:
            spotify: Spotifyクライアント
            albumID (str): アルバムID
            
        Returns:
            dict: アルバム情報
        """
        albumInfo = spotify.album(albumID)
        return albumInfo

    def get_artistInfo(spotify, artistID):
        """
        アーティスト情報を取得
        
        Args:
            spotify: Spotifyクライアント
            artistID (str): アーティストID
            
        Returns:
            dict: アーティスト情報
        """
        artistInfo = spotify.artist(artistID)
        return artistInfo

    def get_related_artistInfo(spotify, artistID):
        """
        関連アーティスト情報を取得
        
        Args:
            spotify: Spotifyクライアント
            artistID (str): アーティストID
            
        Returns:
            dict: 関連アーティスト情報（取得失敗時は空文字列）
        """
        try:
            relatedArtistInfo = spotify.artist_related_artists(artistID)
        except:
            relatedArtistInfo = ""
        return relatedArtistInfo
    
    def addLikedTrackToPlaylist(spotify, trackUri):
        """
        曲をお気に入りプレイリストに追加
        
        Args:
            spotify: Spotifyクライアント
            trackUri (str): トラックURI
        """
        playlist_url = "https://open.spotify.com/playlist/2301nL49ZNwH1ntcUrfDf1?si=7a0eae278a3c44a6"
        trackList = []
        trackList.append(trackUri)
        spotify.user_playlist_add_tracks(st.secrets.SPOTIFY_AUTH.my_user_name, playlist_url, trackList)

    def play(spotify):
        """
        現在の再生を再開
        
        Args:
            spotify: Spotifyクライアント
            
        Returns:
            bool: 成功時True、失敗時False
        """
        try:
            spotify.start_playback()
            return True
        except Exception as e:
            st.error(f"再生に失敗しました: {str(e)}")
            return False

    def pause(spotify):
        """
        現在の再生を一時停止
        
        Args:
            spotify: Spotifyクライアント
            
        Returns:
            bool: 成功時True、失敗時False
        """
        try:
            spotify.pause_playback()
            return True
        except Exception as e:
            st.error(f"一時停止に失敗しました: {str(e)}")
            return False

    def next_track(spotify):
        """
        次の曲をスキップ
        
        Args:
            spotify: Spotifyクライアント
            
        Returns:
            bool: 成功時True、失敗時False
        """
        try:
            spotify.next_track()
            return True
        except Exception as e:
            st.error(f"スキップに失敗しました: {str(e)}")
            return False

    def previous_track(spotify):
        """
        前の曲に戻す
        
        Args:
            spotify: Spotifyクライアント
            
        Returns:
            bool: 成功時True、失敗時False
        """
        try:
            spotify.previous_track()
            return True
        except Exception as e:
            st.error(f"前の曲への切り替えに失敗しました: {str(e)}")
            return False
    
    def getRecentPlayedTracs(spotify):
        """
        最近再生した曲を取得（最大50件）
        
        Args:
            spotify: Spotifyクライアント
            
        Returns:
            dict: 最近再生した曲の情報
        """
        return spotify.current_user_recently_played(limit=50)

    def getAudioFeature(spotify, trackId):
        """
        トラックのオーディオ機能情報を取得
        
        Args:
            spotify: Spotifyクライアント
            trackId (str): トラックID
            
        Returns:
            dict: オーディオ機能情報
        """
        return spotify.audio_features(trackId)
    
    def add_track_to_queue(spotify, trackUri):
        """
        トラックをSpotifyのキューに追加
        
        Args:
            spotify: Spotifyクライアント
            trackUri (str): トラックURI
            
        Returns:
            bool: 成功時True、失敗時False
        """
        try:
            spotify.add_to_queue(trackUri)
            return True
        except Exception as e:
            st.error(f"キューへの追加に失敗しました: {str(e)}")
            return False
        