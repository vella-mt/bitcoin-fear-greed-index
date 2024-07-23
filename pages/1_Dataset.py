import streamlit as st

import data as data_loader
from plots import *

data = data_loader.getData()

num_days = st.slider('Select Number of Past Days for Analysis', 1, len(data), 365, key="tail_slider")
data = data.tail(num_days).reset_index(drop=True)

st.dataframe(data, use_container_width=True)

if st.button("Add Features to Dataset"):
    data_loader.addFeatures(data)
    st.dataframe(data, use_container_width=True)