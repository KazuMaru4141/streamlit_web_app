import streamlit as st
from operator import itemgetter
from SpreadSheetAPI import GspreadCtrl
import pandas as pd
import numpy as np
import datetime
import pytz
from overview import OverviewController
from pylastCtrl import pylastCtrl

st.set_page_config(layout="wide")

# サイドバーにナビゲーションを追加
st.sidebar.title("📍 Navigation")
st.sidebar.markdown("---")
st.sidebar.markdown("🏠 [main app](/)")
st.sidebar.markdown("📊 [Dashboard](/0_Dashboard)")
st.sidebar.markdown("🎵 [page1](/page1)")
st.sidebar.markdown("---")

oc = OverviewController()
oc.overviewCtrl()
