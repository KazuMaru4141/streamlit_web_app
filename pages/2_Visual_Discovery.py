import streamlit as st
import google.generativeai as genai
import json
from PIL import Image
import sys
import os

# spotify_auth.pyをインポート
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from spotify_auth import get_auth_manager

st.set_page_config(page_title="Visual Discovery", page_icon="🖼️", layout="wide")

# APIキーの読み込み
api_key = None
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
except (FileNotFoundError, KeyError) as e:
    st.sidebar.warning("⚠️ API Key not found in secrets.toml")
    st.sidebar.info("Please enter your API key below")
    api_key = st.sidebar.text_input("Gemini API Key", type="password")

# UI構築
st.title("🖼️ Visual Discovery (ジャケ買いモード)")
st.write("好きなアルバムジャケットや、雰囲気の好きな画像をアップロードしてください。")
st.write("その画像の美的感覚から連想される音楽をAIが提案します。")

# 画像アップロード
uploaded_file = st.file_uploader(
    "画像をアップロード (JPG, PNG)", 
    type=["jpg", "png", "jpeg"],
    help="アルバムアートや、好きな風景、抽象画など、音楽的なインスピレーションを得たい画像を選んでください"
)

if uploaded_file is not None:
    # 画像を表示
    image = Image.open(uploaded_file)
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.image(image, caption='アップロードされた画像', use_container_width=True)
    
    with col2:
        st.write("### 画像の分析設定")
        
        # 分析の深さを調整
        analysis_depth = st.slider(
            "分析の深さ",
            min_value=0.0,
            max_value=2.0,
            value=1.0,
            step=0.1,
            help="高いほど、より抽象的で実験的な音楽を提案します"
        )
        
        # 検索ボタン
        if st.button("🎨 画像から音楽を探す", type="primary"):
            if not api_key:
                st.error("APIキーを設定してください。")
                st.stop()
            
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-2.5-flash')
            
            # 画像用のプロンプト
            vision_prompt = """
            あなたは、視覚情報を音楽に翻訳する「共感覚」を持つ音楽キュレーターです。
            提供された画像を見て、その「色彩」「構図」「雰囲気」「テクスチャ」から連想される音楽ジャンルやサウンドを分析してください。
            
            分析の観点:
            - 色彩: 暖色系/寒色系、明度、彩度から感じる感情
            - 構図: 静的/動的、シンメトリー/アシンメトリー
            - テクスチャ: 滑らか/粗い、有機的/幾何学的
            - 全体の雰囲気: 穏やか/激しい、明るい/暗い、ノスタルジック/未来的
            
            そして、そのイメージにぴったり合うアーティストを5組紹介してください。
            
            出力は以下のJSON形式のみでお願いします:
            [
                {
                    "artist_name": "アーティスト名",
                    "reason": "画像から受けたインスピレーションと選曲理由（例: 『青く冷たい色使いから、北欧のポストロックを連想しました』など、具体的に）",
                    "representative_track": "代表曲またはおすすめの1曲",
                    "representative_album": "おすすめのアルバム"
                },
                ...
            ]
            """
            
            with st.spinner("画像を音楽に翻訳中..."):
                try:
                    # 画像とテキストをリストで渡す
                    response = model.generate_content(
                        [vision_prompt, image],
                        generation_config={"temperature": analysis_depth}
                    )
                    
                    # レスポンステキストからJSONを抽出
                    response_text = response.text.strip()
                    
                    # JSONブロックを抽出
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
                    
                    # Spotify APIでアルバム情報を取得
                    auth_manager = get_auth_manager()
                    sp = auth_manager.get_spotify_client()
                    
                    # 各アーティストのSpotify情報を取得
                    for artist in artists:
                        if sp:
                            try:
                                query = f"artist:{artist['artist_name']} album:{artist['representative_album']}"
                                results = sp.search(q=query, type='album', limit=1)
                                
                                if results['albums']['items']:
                                    album = results['albums']['items'][0]
                                    artist['album_image'] = album['images'][0]['url'] if album['images'] else None
                                    artist['album_url'] = album['external_urls']['spotify']
                                    
                                    album_id = album['id']
                                    tracks = sp.album_tracks(album_id, limit=5)
                                    for track in tracks['items']:
                                        if track.get('preview_url'):
                                            artist['preview_url'] = track['preview_url']
                                            break
                                else:
                                    artist['album_image'] = None
                                    artist['album_url'] = None
                                    artist['preview_url'] = None
                            except Exception as e:
                                artist['album_image'] = None
                                artist['album_url'] = None
                                artist['preview_url'] = None
                        else:
                            artist['album_image'] = None
                            artist['album_url'] = None
                            artist['preview_url'] = None
                    
                    # 結果の表示
                    st.success("✨ 画像から音楽を発見しました！")
                    
                    for i, artist in enumerate(artists):
                        with st.expander(f"🎵 {artist['artist_name']}", expanded=True):
                            col_image, col_info = st.columns([1, 3])
                            
                            with col_image:
                                if artist.get('album_image'):
                                    st.image(artist['album_image'], use_container_width=True)
                                else:
                                    st.info("🎵 No Image")
                            
                            with col_info:
                                st.markdown(f"**画像からのインスピレーション:** {artist['reason']}")
                                st.markdown(f"**必聴トラック:** `{artist['representative_track']}`")
                                st.markdown(f"**必聴アルバム:** `{artist['representative_album']}`")
                                
                                # プレビュー再生
                                if artist.get('preview_url'):
                                    st.audio(artist['preview_url'], format='audio/mp3')
                                
                                # Spotifyリンク
                                if artist.get('album_url'):
                                    st.markdown(f"[🎵 Spotifyで開く]({artist['album_url']})")
                                else:
                                    album_search_query = f"{artist['artist_name']} {artist['representative_album']}".replace(' ', '%20')
                                    album_url = f"https://open.spotify.com/search/{album_search_query}"
                                    st.markdown(f"[Spotifyでアルバムを検索する]({album_url})")
                
                except json.JSONDecodeError as e:
                    st.error(f"JSON解析エラー: {e}")
                    st.write("**AIのレスポンス:**")
                    st.code(response.text)
                except Exception as e:
                    st.error(f"エラーが発生しました: {e}")
                    if 'response' in locals():
                        st.write("**デバッグ情報:**")
                        st.code(response.text)
else:
    st.info("👆 画像をアップロードして、ビジュアルから音楽を発見しましょう！")
    
    # 使い方の例
    with st.expander("💡 使い方のヒント"):
        st.write("""
        **こんな画像がおすすめ:**
        - 🎨 好きなアルバムジャケット
        - 🌆 印象的な風景写真
        - 🎭 抽象画やアート作品
        - 📸 雰囲気のある写真
        
        **例:**
        - 雨の降る街の写真 → Jangle Pop, Mellow Pop
        - 激しい赤色の抽象画 → Thrash Metal, Aggressive Rock
        - 穏やかな海の風景 → Ambient, Post-Rock
        - ネオンの夜景 → Synthwave, Electronic
        """)
