import streamlit as st

with st.form(key='prifile_form'):
    # text box
    name = st.text_input('名前')
    address = st.text_input('住所')
    print(name)

    # select box
    age_category = st.radio(
        '年齢層',
        ('こども(18才未満)', '大人(18才以上)')
    )
    
    hobby = st.multiselect(
        '趣味',
        ('スポーツ', '読書', 'プログラミング', 'アニメ・映画', '釣り', '料理')
    )

    # ボタン
    submit_btn = st.form_submit_button('送信')
    cancel_btn = st.form_submit_button('キャンセル')

    print(f'submit_btn: {submit_btn}')
    print(f'cancel_btn: {cancel_btn}')

    if (submit_btn == True):
        st.text(f'ようこそ！{name}さん!{address}に書籍を送りました!')
        st.text(f'{age_category}')
        st.text(f'{", ".join(hobby)}')