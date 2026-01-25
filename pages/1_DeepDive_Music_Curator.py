import streamlit as st
import google.generativeai as genai
import json
import pandas as pd
import sys
import os

# spotify_auth.pyをインポート
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from spotify_auth import get_auth_manager
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
# ユーザーご指定のアーティスト要素（Camera Obscura, Death Cab, CoBなど）を追加反映
genre_prompts = {
    # --- 既存のカテゴリ ---
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
        "description": "歌モノのハウスミュージックや、メロディアスなダンスミュージック。",
        "mood": "Dance, Melodic House, Groovy"
    },

    # --- アップデートおよび新規追加したカテゴリ ---
    "DeepDive_JanglePop": {
        "description": "Belle and SebastianやCamera Obscuraのように、ストリングスや管楽器を取り入れた室内楽的（Chamber Pop）な上品さと、Sunwichのような陽だまりのような温かさを併せ持つギターポップ。Rickenbackerのクリーントーン。",
        "mood": "Sunny, Twee, Orchestral Pop, Nostalgic"
    },
    "DeepDive_IndieRock": {
        "description": "Death Cab for Cutieのように、内省的で文学的な歌詞と、クリーンなギターのアルペジオが美しく絡み合うロック。派手さよりも、楽曲の構成美や感情の揺れ動きを重視したサウンド。",
        "mood": "Introspective, Storytelling, Clean Guitars, Melancholic"
    },
    "DeepDive_MelodicDeathMetal": {
        "description": "Children of Bodomのようなネオクラシカルで煌びやかなキーボードと速弾きギター、またはArch Enemyのような攻撃的だが一度聴いたら耳に残るキャッチーなギターリフを持つメロデス。叙情と暴虐の融合。",
        "mood": "Neoclassical, Technical, Aggressive but Catchy, Shredding"
    },
    "DeepDive_IndiePop": {
        "description": "ロックよりも「歌心」や「かわいらしさ」を重視したインディーサウンド。シンセサイザーやアコースティック楽器を使い、親しみやすくキャッチーなメロディ。",
        "mood": "Sweet, Catchy, Lo-fi"
    },
    "DeepDive_PopPunk": {
        "description": "3コード進行、速いテンポ、そして一度聴いたら忘れないキャッチーなサビ。青春感や疾走感のあるパンクロック。Green DayやBlink-182の系譜。",
        "mood": "High Energy, Youthful, Anthemic"
    },
    "DeepDive_MelodicHardcore (Melocore)": {
        "description": "ハードコア・パンクの疾走感に、泣きのメロディを乗せたスタイル。90年代のスケートパンクや、Hi-STANDARDのような哀愁のある速いパンク。",
        "mood": "Fast, Emotional, Skate Punk"
    },
    "DeepDive_ThrashMetal": {
        "description": "攻撃的なスピード、刻むギターリフ（ザクザク感）、複雑な展開が特徴のメタル。MetallicaやSlayerのルーツを感じさせつつ、鋭利なサウンド。",
        "mood": "Aggressive, Fast, Technical Riffs"
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

# ディープダイブモードのオプション
st.markdown("---")
st.markdown("### 🎛️ Vibe Controller")
st.write("今の気分に合わせて微調整")

col1, col2 = st.columns(2)
with col1:
    is_deep_dive = st.checkbox("🕵️ 定番を除外して、隠れた名バンドを探す", value=False)
with col2:
    temperature = st.slider("創造性レベル", min_value=0.0, max_value=2.0, value=0.9, step=0.1, 
                           help="高いほどバラエティが増えます（0.0=安定、2.0=冒険的）")

# 気分の微調整スライダー
st.markdown("---")
st.write("**気分の微調整**")
col3, col4, col5 = st.columns(3)
with col3:
    melancholy_level = st.slider("😢 哀愁・エモさ", 0, 100, 50, 
                                 help="100%に近いほど、切なく泣けるメロディを重視")
with col4:
    energy_level = st.slider("⚡ 激しさ・エナジー", 0, 100, 50,
                            help="100%に近いほど、攻撃的でアップテンポ")
with col5:
    obscurity_level = st.slider("🔍 マニアック度", 0, 100, 50,
                               help="100%に近いほど、無名で知る人ぞ知るバンドのみを選出")

st.markdown("---")

# セッション状態の初期化（ディグ機能用）
if 'dig_artist' not in st.session_state:
    st.session_state.dig_artist = None
if 'search_results' not in st.session_state:
    st.session_state.search_results = None
if 'current_genre' not in st.session_state:
    st.session_state.current_genre = None
if 'conversation_history' not in st.session_state:
    st.session_state.conversation_history = []
if 'last_search_params' not in st.session_state:
    st.session_state.last_search_params = None   

# 会話履歴の表示とフィードバック（サイドバー）
with st.sidebar:
    st.markdown("---")
    
    # デバッグ用：セッション状態の確認
    if st.session_state.search_results is not None:
        st.success(f"✅ 検索結果: {len(st.session_state.search_results)}件のアーティスト")
    else:
        st.info("💡 検索を実行すると、フィードバック機能が使えます")
    
    if st.session_state.search_results is not None:
        with st.expander("💬 検索結果へのフィードバック", expanded=True):
            st.write("**前回の検索結果はどうでしたか？**")
            
            feedback_rating = st.slider(
                "満足度",
                min_value=1,
                max_value=5,
                value=3,
                help="1=全然ダメ、3=普通、5=完璧！",
                key="feedback_rating_slider"
            )
            
            feedback_comment = st.text_area(
                "コメント（任意）",
                placeholder="例: もっと激しい曲が良い、2番目のアーティストは最高だった、など",
                height=80,
                key="feedback_comment_area"
            )
            
            if st.button("📝 フィードバックを保存", use_container_width=True, key="save_feedback_btn"):
                # フィードバックを履歴に追加
                feedback_entry = {
                    "search_params": st.session_state.get('last_search_params', {}),
                    "results": [a['artist_name'] for a in st.session_state.search_results],
                    "rating": feedback_rating,
                    "comment": feedback_comment,
                    "timestamp": st.session_state.get('search_timestamp', pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S"))
                }
                st.session_state.conversation_history.append(feedback_entry)
                st.success("✅ フィードバックを保存しました！次の検索に活かします。")
                st.rerun()
    
    # 履歴表示とクリアボタン
    if len(st.session_state.conversation_history) > 0:
        st.markdown("---")
        st.write(f"📚 **保存済みフィードバック:** {len(st.session_state.conversation_history)}件")
        if st.button("🗑️ 会話履歴をクリア", use_container_width=True, key="clear_history_btn"):
            st.session_state.conversation_history = []
            st.success("履歴をクリアしました")
            st.rerun()


# ディグモードの表示と自動検索
if st.session_state.dig_artist:
    st.info(f"🔍 **ディグモード:** 『{st.session_state.dig_artist}』に似たアーティストを探しています...")
    if st.button("🔙 ジャンル検索に戻る"):
        st.session_state.dig_artist = None
        st.rerun()
    # ディグモードの場合は自動的に検索を実行
    should_search = True
else:
    # 通常モードの場合は検索ボタンを表示
    should_search = st.button("おすすめを検索 (Generate)", type="primary")

if should_search:
    if not api_key:
        st.error("APIキーを設定してください。")
        st.stop()

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.5-flash')

    # 気分の微調整指示を生成
    vibe_instruction = f"""
    
    **【今の気分の微調整】**
    - 哀愁・エモさレベル: {melancholy_level}% (100%に近いほど、切なく泣けるメロディを重視。0%なら明るく前向き)
    - 激しさ・エナジーレベル: {energy_level}% (100%に近いほど、攻撃的でアップテンポ。0%なら穏やかでスロー)
    - マニアック度: {obscurity_level}% (100%に近いほど、無名で知る人ぞ知るバンドのみを選出。0%なら定番も可)
    """
    
    # 会話履歴をプロンプトに追加
    history_context = ""
    if len(st.session_state.conversation_history) > 0:
        history_context = "\n\n**【重要: 過去の検索履歴とユーザーフィードバック】**\n"
        history_context += "以下は、このセッションでの過去の検索結果とユーザーの評価です。この情報を活用して、ユーザーの好みをより正確に理解してください。\n\n"
        
        for idx, entry in enumerate(st.session_state.conversation_history[-3:], 1):  # 直近3件のみ
            history_context += f"**検索 #{idx}:**\n"
            history_context += f"- 推薦したアーティスト: {', '.join(entry['results'])}\n"
            history_context += f"- ユーザー評価: {entry['rating']}/5\n"
            if entry['comment']:
                history_context += f"- ユーザーコメント: 『{entry['comment']}』\n"
            history_context += "\n"
        
        history_context += "**指示:** 上記のフィードバックを参考に、ユーザーが高評価したアーティストの特徴を強化し、低評価だった要素は避けてください。\n"
        history_context += "ユーザーのコメントに具体的な要望（例: 「もっと激しい」「メロディアスに」）がある場合は、必ずそれを反映してください。\n"
    
    # ディープダイブモード用の追加指示
    additional_instruction = ""
    if is_deep_dive or obscurity_level > 70:
        additional_instruction = """
    
    **【重要: 選定基準】**
    - メジャーすぎるアーティスト（例: Weezer, Fountains of Wayne, Oasis, The Strokes, Death Cab for Cutieなど）は**絶対に除外**してください。
    - まだあまり知られていない「隠れた名曲」を持つバンドや、2020年以降に活動している新しいアーティストを優先してください。
    - "Underrated"（過小評価されている）アーティストを選んでください。
    - インディーズレーベルや、Spotifyの再生数がまだ少ない良質なアーティストを選んでください。
    - 日本のインディーバンドも積極的に含めてください。
        """

    # ディグモード用のプロンプト修正
    if st.session_state.dig_artist:
        # アーティストベースの検索
        prompt = f"""
    あなたは熟練の音楽キュレーターです。
    以下の条件に基づき、おすすめのアーティストを5組紹介してください。
    
    **基準アーティスト:**
    『{st.session_state.dig_artist}』に音楽性が似ているアーティストを探してください。
    
    **類似性の基準:**
    - サウンドの質感（ギターの音色、ボーカルスタイル、リズムセクション）
    - 楽曲の構成や展開の仕方
    - 歌詞のテーマや雰囲気
    - 同じシーンやムーブメントに属するバンド
    {vibe_instruction}{history_context}{additional_instruction}
    
    **重要:** {st.session_state.dig_artist} 自身は除外してください。
    - 出力形式: JSONフォーマットのみ
    
    **JSONの構造:**
    [
        {{
            "artist_name": "アーティスト名",
            "reason": "なぜ{st.session_state.dig_artist}に似ているのかの具体的な解説（日本語、音楽的な共通点を明確に）",
            "representative_track": "代表曲またはおすすめの1曲",
            "representative_album": "おすすめのアルバム"
        }},
        ...
    ]
    """
    else:
        # 通常のジャンルベース検索
        prompt = f"""
    あなたは熟練の音楽キュレーターです。
    以下の条件に基づき、おすすめのアーティストを5組紹介してください。
    
    **基本ジャンル:**
    {selected_genre_info['description']}
    
    **除外ジャンル:** HipHop, Classical
    {vibe_instruction}{history_context}{additional_instruction}
    - 出力形式: JSONフォーマットのみ
    
    **JSONの構造:**
    [
        {{
            "artist_name": "アーティスト名",
            "reason": "なぜこのジャンルに合うのかの簡潔な解説（日本語、気分の微調整レベルを考慮した選定理由も含める。例: '哀愁度80%のため、この泣きのメロディを持つバンドを選出'）",
            "representative_track": "代表曲またはおすすめの1曲",
            "representative_album": "おすすめのアルバム"
        }},
        ...
    ]
    """

    # 創造性パラメータの設定
    generation_config = {
        "temperature": temperature,  # ユーザーが選択した創造性レベル
    }
    
    spinner_text = "ディープな選曲中..." if is_deep_dive else f"'{selected_genre_key}' に合うアーティストを探しています..."
    
    with st.spinner(spinner_text):
        try:
            # temperatureを設定してリクエスト
            response = model.generate_content(
                prompt,
                generation_config=generation_config
            )
            
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
            
            # 検索結果とパラメータをセッション状態に保存
            st.session_state.search_results = artists
            st.session_state.current_genre = selected_genre_key
            st.session_state.last_search_params = {
                "genre": selected_genre_key,
                "melancholy": melancholy_level,
                "energy": energy_level,
                "obscurity": obscurity_level,
                "deep_dive": is_deep_dive,
                "dig_artist": st.session_state.dig_artist
            }
            st.session_state.search_timestamp = pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # データを保存したら即座に画面を更新する
            st.rerun()

        except json.JSONDecodeError as e:
            st.error(f"JSON解析エラー: {e}")
            st.write("**AIのレスポンス:**")
            st.code(response.text)
        except Exception as e:
            st.error(f"エラーが発生しました: {e}")
            if 'response' in locals():
                st.write("**デバッグ情報:**")
                st.code(response.text)


# 検索結果の表示（セッション状態から取得）
if st.session_state.search_results is not None:
    artists = st.session_state.search_results
    selected_genre_key = st.session_state.current_genre
    
    # Spotify APIでアルバム情報を取得（まだ取得していない場合）
    if not artists[0].get('album_image'):
        auth_manager = get_auth_manager()
        sp = auth_manager.get_spotify_client()
        
        # 各アーティストのSpotify情報を取得
        for artist in artists:
            if sp:
                try:
                    # アーティストとアルバムで検索
                    query = f"artist:{artist['artist_name']} album:{artist['representative_album']}"
                    results = sp.search(q=query, type='album', limit=1)
                    
                    if results['albums']['items']:
                        album = results['albums']['items'][0]
                        artist['album_image'] = album['images'][0]['url'] if album['images'] else None
                        artist['album_url'] = album['external_urls']['spotify']
                        
                        # トラック情報を取得（プレビューURL用）
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
    st.success("検索完了！")
    # プレイリストエクスポート機能
    st.markdown("---")
    st.markdown("### 🎵 Spotifyプレイリストにエクスポート")
    
    # プレイリスト作成モードの選択
    col_mode, col_name = st.columns([1, 2])
    with col_mode:
        playlist_mode = st.radio(
            "エクスポート方法",
            ["新規プレイリスト作成", "既存プレイリストに追加"],
            horizontal=True
        )
    
    # トラック選択モード
    track_mode = st.radio(
        "追加する曲",
        ["代表曲のみ (5曲)", "アーティストTOP10 (各アーティストの人気曲10曲)", "アルバム全体 (各アーティストのアルバム全曲)"],
        horizontal=False,
        help="代表曲のみ: 各アーティストの代表曲1曲ずつ / TOP10: 各アーティストの人気曲トップ10 / アルバム全体: 推薦されたアルバムの全トラック"
    )
    
    # Spotify認証チェック（プレイリスト一覧取得用）
    auth_manager = get_auth_manager()
    sp = auth_manager.get_spotify_client()
    
    if playlist_mode == "新規プレイリスト作成":
        with col_name:
            playlist_name = st.text_input(
                "プレイリスト名", 
                value=f"DeepDive - {selected_genre_key} ({st.session_state.get('dig_artist', 'Genre')})",
                help="Spotifyに作成するプレイリストの名前"
            )
        export_button = st.button("🎵 新規プレイリストを作成", type="primary", use_container_width=True)
    else:
        # 既存プレイリストの一覧を取得
        if sp:
            try:
                user_playlists = sp.current_user_playlists(limit=50)
                playlist_options = {f"{pl['name']} ({pl['tracks']['total']}曲)": pl['id'] 
                                  for pl in user_playlists['items'] if pl['owner']['id'] == sp.current_user()['id']}
                
                if playlist_options:
                    with col_name:
                        selected_playlist_display = st.selectbox(
                            "プレイリストを選択",
                            options=list(playlist_options.keys()),
                            help="追加先のプレイリストを選択してください"
                        )
                    selected_playlist_id = playlist_options[selected_playlist_display]
                    export_button = st.button("🎵 選択したプレイリストに追加", type="primary", use_container_width=True)
                else:
                    st.warning("⚠️ プレイリストが見つかりません。新規作成モードを選択してください。")
                    export_button = False
            except Exception as e:
                st.error(f"プレイリスト一覧の取得に失敗しました: {e}")
                export_button = False
        else:
            st.error("❌ Spotify認証が必要です。Dashboardページで認証を完了してください。")
            export_button = False
    
    if export_button:
        if not sp:
            st.error("❌ Spotify認証が必要です。Dashboardページで認証を完了してください。")
            st.info("💡 Dashboardページ → 'Spotifyと連携' ボタンをクリックしてください")
        else:
            with st.spinner("プレイリストを作成中..." if playlist_mode == "新規プレイリスト作成" else "トラックを追加中..."):
                try:
                    # ユーザー情報を取得
                    user_info = sp.current_user()
                    user_id = user_info['id']
                    st.info(f"👤 ユーザー: {user_info.get('display_name', user_id)}")
                    
                    # プレイリストIDを取得または作成
                    if playlist_mode == "新規プレイリスト作成":
                        # 新規プレイリストを作成
                        playlist = sp.user_playlist_create(
                            user=user_id,
                            name=playlist_name,
                            public=False,
                            description=f"AI-curated playlist by DeepDive Music Curator"
                        )
                        playlist_id = playlist['id']
                        playlist_url = playlist['external_urls']['spotify']
                        st.success(f"✅ プレイリスト「{playlist_name}」を作成しました")
                    else:
                        # 既存プレイリストを使用
                        playlist_id = selected_playlist_id
                        playlist_info = sp.playlist(playlist_id)
                        playlist_url = playlist_info['external_urls']['spotify']
                        st.success(f"✅ プレイリスト「{selected_playlist_display}」に追加します")
                    
                    # トラックURIを収集
                    track_uris = []
                    progress_container = st.container()
                    
                    if track_mode == "代表曲のみ (5曲)":
                        # 代表曲のみを追加
                        for idx, artist in enumerate(artists, 1):
                            try:
                                # アーティスト名とトラック名で検索
                                query = f"artist:{artist['artist_name']} track:{artist['representative_track']}"
                                results = sp.search(q=query, type='track', limit=1)
                                
                                if results['tracks']['items']:
                                    track_uri = results['tracks']['items'][0]['uri']
                                    track_uris.append(track_uri)
                                    progress_container.success(f"✓ {idx}/5: {artist['artist_name']} - {artist['representative_track']}")
                                else:
                                    progress_container.warning(f"⚠️ {idx}/5: {artist['artist_name']} - {artist['representative_track']} が見つかりませんでした")
                            except Exception as e:
                                progress_container.error(f"❌ {idx}/5: {artist['artist_name']} - エラー: {str(e)}")
                    
                    elif track_mode == "アーティストTOP10 (各アーティストの人気曲10曲)":
                        # アーティストのTOP10を追加
                        for idx, artist in enumerate(artists, 1):
                            try:
                                # アーティストを検索
                                query = f"artist:{artist['artist_name']}"
                                results = sp.search(q=query, type='artist', limit=1)
                                
                                if results['artists']['items']:
                                    artist_id = results['artists']['items'][0]['id']
                                    artist_name = results['artists']['items'][0]['name']
                                    
                                    # アーティストのトップトラックを取得（最大10曲）
                                    top_tracks = sp.artist_top_tracks(artist_id, country='JP')
                                    top_track_uris = [track['uri'] for track in top_tracks['tracks'][:10]]
                                    track_uris.extend(top_track_uris)
                                    
                                    progress_container.success(f"✓ {idx}/5: {artist_name} - TOP {len(top_track_uris)}曲")
                                else:
                                    progress_container.warning(f"⚠️ {idx}/5: {artist['artist_name']} が見つかりませんでした")
                            except Exception as e:
                                progress_container.error(f"❌ {idx}/5: {artist['artist_name']} - エラー: {str(e)}")
                    
                    else:
                        # アルバム全体を追加
                        for idx, artist in enumerate(artists, 1):
                            try:
                                # アーティストとアルバムで検索
                                query = f"artist:{artist['artist_name']} album:{artist['representative_album']}"
                                results = sp.search(q=query, type='album', limit=1)
                                
                                if results['albums']['items']:
                                    album = results['albums']['items'][0]
                                    album_id = album['id']
                                    album_name = album['name']
                                    
                                    # アルバムの全トラックを取得
                                    album_tracks = sp.album_tracks(album_id)
                                    album_track_uris = [track['uri'] for track in album_tracks['items']]
                                    track_uris.extend(album_track_uris)
                                    
                                    progress_container.success(f"✓ {idx}/5: {artist['artist_name']} - {album_name} ({len(album_track_uris)}曲)")
                                else:
                                    progress_container.warning(f"⚠️ {idx}/5: {artist['artist_name']} - {artist['representative_album']} が見つかりませんでした")
                            except Exception as e:
                                progress_container.error(f"❌ {idx}/5: {artist['artist_name']} - エラー: {str(e)}")
                    
                    # プレイリストにトラックを追加
                    if track_uris:
                        sp.playlist_add_items(playlist_id, track_uris)
                        st.success(f"🎉 {len(track_uris)}曲をプレイリストに追加しました！")
                        st.markdown(f"### [🎵 Spotifyで開く]({playlist_url})")
                        st.balloons()
                    else:
                        st.error("❌ トラックが見つかりませんでした。アーティスト名やトラック名を確認してください。")
                
                except Exception as e:
                    st.error(f"❌ プレイリスト作成エラー: {str(e)}")
                    st.info("💡 トラブルシューティング:")
                    st.write("1. Spotify認証が有効か確認してください")
                    st.write("2. Dashboardページで再認証を試してください")
                    st.write("3. ブラウザをリフレッシュしてください")
    
    st.markdown("---")
    
    for i, artist in enumerate(artists):
        with st.expander(f"🎵 {artist['artist_name']}", expanded=True):
            # アルバム画像と情報を表示
            col_image, col_info, col_dig = st.columns([1, 3, 1])
            
            with col_image:
                # アルバムアートワーク
                if artist.get('album_image'):
                    st.image(artist['album_image'], use_container_width=True)
                else:
                    st.info("🎵 No Image")
            
            with col_info:
                st.markdown(f"**おすすめ理由:** {artist['reason']}")
                st.markdown(f"**必聴トラック:** `{artist['representative_track']}`")
                st.markdown(f"**必聴アルバム:** `{artist['representative_album']}`")
                
                # プレビュー再生
                if artist.get('preview_url'):
                    st.audio(artist['preview_url'], format='audio/mp3')
                
                # Spotifyリンク
                if artist.get('album_url'):
                    st.markdown(f"[🎵 Spotifyで開く]({artist['album_url']})")
                else:
                    # フォールバック: 検索リンク
                    album_search_query = f"{artist['artist_name']} {artist['representative_album']}".replace(' ', '%20')
                    album_url = f"https://open.spotify.com/search/{album_search_query}"
                    st.markdown(f"[Spotifyでアルバムを検索する]({album_url})")
            
            with col_dig:
                # ディグボタン - on_clickコールバックを使用
                def set_dig_artist(artist_name):
                    st.session_state.dig_artist = artist_name
                
                st.button(
                    f"🔍 ディグ", 
                    key=f"dig_btn_{i}",
                    help="このアーティストに似たバンドをさらに探す",
                    on_click=set_dig_artist,
                    args=(artist['artist_name'],)
                )
