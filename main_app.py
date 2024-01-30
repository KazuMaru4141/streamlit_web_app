import streamlit as st
from PIL import Image

st.title('かずちゃんアプリ')
st.title('test application')

image = Image.open('./data/WFA_Artist(20240119).png')
st.image(image, width=200)
