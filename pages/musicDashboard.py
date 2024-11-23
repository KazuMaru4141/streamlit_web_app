import streamlit as st
from operator import itemgetter
from SpreadSheetAPI import GspreadCtrl
import pandas as pd
import numpy as np
import datetime
import pytz
from overview import OverviewController
from likedTracks import LovedTracksController

st.set_page_config(layout="wide")
tab1, tab2 = st.tabs(["Overview", "LikedTracs"])
oc = OverviewController()
lt = LovedTracksController()

with tab1:
    oc.overviewCtrl()
    
with tab2:
    lt.likecTracksCtrl()
    
