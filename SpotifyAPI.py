import streamlit as st
import spotipy
import spotipy.util as util
from spotipy.oauth2 import SpotifyClientCredentials, SpotifyOAuth
from spotify_auth import get_auth_manager

class SpotifyCtrl:
    def create_spotify():
        """
        Spotifyクライアントを初期化して認証情報を取得
        
        新しい認証システムを使用してトークンを管理します。
        
        Returns:
            tuple: (auth_manager, spotify) - 認証マネージャーとSpotifyクライアント
                   認証されていない場合は (auth_manager, None)
        """
        auth_manager = get_auth_manager()
        spotify = auth_manager.get_spotify_client()
        
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
            error_msg = str(e)
            if "404" in error_msg or "Not found" in error_msg:
                st.error("⚠️ アクティブなSpotifyデバイスが見つかりません。\n\n"
                        "キューに追加するには、Spotifyアプリ（PC、スマホ、ブラウザなど）で音楽を再生してください。")
            else:
                st.error(f"キューへの追加に失敗しました: {error_msg}")
            return False
        