"""
Spotify OAuth認証モジュール

Authorization Code Flowを使用したSpotify認証を管理します。
トークンの取得、保存、更新を自動的に処理します。
"""

import streamlit as st
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import time
from typing import Optional, Tuple


class SpotifyAuthManager:
    """Spotify OAuth認証を管理するクラス"""
    
    def __init__(self, client_id: str, client_secret: str, redirect_uri: str, scope: str):
        """
        認証マネージャーを初期化
        
        Args:
            client_id: Spotify Client ID
            client_secret: Spotify Client Secret
            redirect_uri: OAuth リダイレクトURI
            scope: 必要な権限のスコープ
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.scope = scope
        
        # SpotifyOAuthオブジェクトを作成（キャッシュなし）
        self.sp_oauth = SpotifyOAuth(
            client_id=client_id,
            client_secret=client_secret,
            redirect_uri=redirect_uri,
            scope=scope,
            cache_path=None,  # ファイルキャッシュを無効化
            show_dialog=False
        )
    
    def get_auth_url(self) -> str:
        """
        Spotify認証URLを生成
        
        Returns:
            str: 認証URL
        """
        return self.sp_oauth.get_authorize_url()
    
    def handle_callback(self, code: str) -> bool:
        """
        認証コールバックを処理してトークンを取得
        
        Args:
            code: Spotifyから返された認証コード
            
        Returns:
            bool: トークン取得成功時True
        """
        try:
            # 認証コードをトークンに交換
            token_info = self.sp_oauth.get_access_token(code, as_dict=True, check_cache=False)
            
            if token_info:
                # セッション状態にトークン情報を保存
                st.session_state['spotify_token_info'] = token_info
                st.session_state['spotify_authenticated'] = True
                return True
            return False
        except Exception as e:
            st.error(f"認証エラー: {str(e)}")
            return False
    
    def get_cached_token(self) -> Optional[dict]:
        """
        セッション状態からトークン情報を取得
        
        Returns:
            dict: トークン情報、存在しない場合はNone
        """
        return st.session_state.get('spotify_token_info')
    
    def is_token_expired(self, token_info: dict) -> bool:
        """
        トークンの有効期限をチェック
        
        Args:
            token_info: トークン情報
            
        Returns:
            bool: 期限切れの場合True
        """
        if not token_info:
            return True
        
        # 現在時刻と有効期限を比較（60秒のバッファを持たせる）
        now = int(time.time())
        expires_at = token_info.get('expires_at', 0)
        return now >= (expires_at - 60)
    
    def refresh_access_token(self, token_info: dict) -> Optional[dict]:
        """
        リフレッシュトークンを使用してアクセストークンを更新
        
        Args:
            token_info: 現在のトークン情報
            
        Returns:
            dict: 新しいトークン情報、失敗時はNone
        """
        try:
            refresh_token = token_info.get('refresh_token')
            if not refresh_token:
                return None
            
            # トークンをリフレッシュ
            new_token_info = self.sp_oauth.refresh_access_token(refresh_token)
            
            # セッション状態を更新
            st.session_state['spotify_token_info'] = new_token_info
            return new_token_info
        except Exception as e:
            st.error(f"トークン更新エラー: {str(e)}")
            return None
    
    def get_valid_token(self) -> Optional[str]:
        """
        有効なアクセストークンを取得（必要に応じて自動更新）
        
        Returns:
            str: 有効なアクセストークン、取得失敗時はNone
        """
        token_info = self.get_cached_token()
        
        if not token_info:
            return None
        
        # トークンが期限切れの場合は更新
        if self.is_token_expired(token_info):
            token_info = self.refresh_access_token(token_info)
            if not token_info:
                return None
        
        return token_info.get('access_token')
    
    def get_spotify_client(self) -> Optional[spotipy.Spotify]:
        """
        認証済みSpotifyクライアントを取得
        
        Returns:
            Spotify: 認証済みクライアント、認証失敗時はNone
        """
        access_token = self.get_valid_token()
        
        if not access_token:
            return None
        
        return spotipy.Spotify(auth=access_token)
    
    def is_authenticated(self) -> bool:
        """
        認証状態をチェック
        
        Returns:
            bool: 認証済みの場合True
        """
        return st.session_state.get('spotify_authenticated', False) and self.get_cached_token() is not None
    
    def logout(self):
        """認証情報をクリア"""
        if 'spotify_token_info' in st.session_state:
            del st.session_state['spotify_token_info']
        if 'spotify_authenticated' in st.session_state:
            del st.session_state['spotify_authenticated']


def get_auth_manager() -> SpotifyAuthManager:
    """
    認証マネージャーのシングルトンインスタンスを取得
    
    Returns:
        SpotifyAuthManager: 認証マネージャー
    """
    if 'auth_manager' not in st.session_state:
        # secrets.tomlから認証情報を取得
        scope = 'user-library-read user-read-playback-state user-modify-playback-state playlist-read-private user-read-recently-played playlist-read-collaborative playlist-modify-public playlist-modify-private'
        
        st.session_state['auth_manager'] = SpotifyAuthManager(
            client_id=st.secrets.SPOTIFY_AUTH.my_id,
            client_secret=st.secrets.SPOTIFY_AUTH.my_secret,
            redirect_uri=st.secrets.SPOTIFY_AUTH.redirect_url,
            scope=scope
        )
    
    return st.session_state['auth_manager']
