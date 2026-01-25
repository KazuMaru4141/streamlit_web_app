import streamlit as st
import google.generativeai as genai
import json
import sys
import os

# ページディレクトリから実行される場合、親ディレクトリをパスに追加
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from spotify_auth import get_auth_manager

# ページ設定
st.set_page_config(page_title="DeepDive Music Curator", page_icon="🎧", layout="wide")

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

# 1. APIキーの読み込み (secrets.toml または 入力欄から)
api_key = None

try:
    # 直接アクセス
    api_key = st.secrets["GOOGLE_API_KEY"]
except KeyError:
    try:
        # get()メソッドを使用
        api_key = st.secrets.get("GOOGLE_API_KEY")
        if not api_key:
            raise KeyError("GOOGLE_API_KEY not found")
    except Exception as e:
        # secretsがない場合のフォールバック（サイドバーで入力）
        st.sidebar.warning("⚠️ API Key not found in secrets.toml")
        st.sidebar.info("Please enter your API key below")
        api_key = st.sidebar.text_input("Gemini API Key", type="password")

# 2. ジャンルと「裏側の定義（プロンプト）」の辞書
# ここを書き換えるだけで、ユーザーさん好みの定義にチューニングできます
genre_prompts = {
    "DeepDive_PowerPop": {
        "description": "Fountains of WayneやWeezerのような、歪んだギターとキャッチーなメロディ、切ないハーモニーを持つパワーポップ。",
        "mood": "Energetic, Catchy, Melodic"
    },
    "DeepDive_MellowPop": {
        "description": "夜に聴きたくなるような、落ち着いたテンポで美しいメロディを持つポップス。アコースティックとエレクトロニカの融合。",
        "mood": "Chill, Emotional, Night drive"
    },
    "DeepDive_BeautifulEmo": {
        "description": "美しい旋律と感情的なボーカルが特徴のエモ・ロック。激しさよりも美しさを重視。",
        "mood": "Emotional, Beautiful, Rock"
    },
    "DeepDive_Dance": {
        "description": "Le YouthやLane 8のような、歌モノのハウスミュージックや、メロディアスなダンスミュージック。",
        "mood": "Dance, Melodic House, Groovy"
    }
}

# UI構築
st.title("🎧 DeepDive Music Curator")
st.write("今の気分に合ったカテゴリを選んでください。AIが厳選します。")

# サイドバーでジャンル選択
selected_genre_key = st.selectbox(
    "カテゴリーを選択",
    options=list(genre_prompts.keys())
)

# 選択されたジャンルの情報を取得
selected_genre_info = genre_prompts[selected_genre_key]
st.info(f"💡 **Definition:** {selected_genre_info['description']}")

# 検索ボタン
if st.button("おすすめを検索 (Generate)", type="primary"):
    if not api_key:
        st.error("APIキーを設定してください。")
        st.stop()

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.5-flash')

    # プロンプトの作成（JSON出力を強制）
    prompt = f"""
    あなたは熟練の音楽キュレーターです。
    以下の条件に基づき、おすすめのアーティストを5組紹介してください。
    
    **条件:**
    - ジャンル定義: {selected_genre_info['description']}
    - 除外ジャンル: HipHop, Classical
    - 出力形式: JSONフォーマットのみ
    
    **JSONの構造:**
    [
        {{
            "artist_name": "アーティスト名",
            "reason": "なぜこのジャンルに合うのかの簡潔な解説（日本語）",
            "representative_track": "代表曲またはおすすめの1曲"
        }},
        ...
    ]
    """

    with st.spinner(f"'{selected_genre_key}' に合うアーティストを探しています..."):
        try:
            # JSONモードなしでリクエスト（gemini-proはJSONモードをサポートしていない可能性がある）
            response = model.generate_content(prompt)
            
            # レスポンステキストからJSONを抽出
            response_text = response.text.strip()
            
            # JSONブロックを抽出（```json ... ``` の形式の場合）
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                response_text = response_text[json_start:json_end].strip()
            elif "```" in response_text:
                json_start = response_text.find("```") + 3
                json_end = response_text.find("```", json_start)
                response_text = response_text[json_start:json_end].strip()
            
            # JSON文字列をPythonリストに変換
            artists = json.loads(response_text)

            # 結果の表示
            st.success("検索完了！")
            
            for artist in artists:
                with st.expander(f"🎵 {artist['artist_name']}", expanded=True):
                    st.markdown(f"**おすすめ理由:** {artist['reason']}")
                    st.markdown(f"**必聴トラック:** `{artist['representative_track']}`")
                    
                    # 簡易的なSpotify検索リンク（クリックでSpotifyアプリが開くかWeb検索）
                    search_url = f"https://open.spotify.com/search/{artist['artist_name'].replace(' ', '%20')}"
                    st.markdown(f"[Spotifyで検索する]({search_url})")

        except json.JSONDecodeError as e:
            st.error(f"JSON解析エラー: {e}")
            st.write("**AIのレスポンス:**")
            st.code(response.text)
        except Exception as e:
            st.error(f"エラーが発生しました: {e}")
            if 'response' in locals():
                st.write("**デバッグ情報:**")
                st.code(response.text)
