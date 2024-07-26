import streamlit as st

from libraries.data import *
from libraries.plots import *

dataset = getData()

num_days = st.slider('Select Number of Past Days to Analyze', 1, len(dataset), 365)
dataset = dataset.tail(num_days).reset_index(drop=True)

st.dataframe(dataset, use_container_width=True)

if st.button("Add Features to Dataset"):
    addFeatures(dataset)
    st.dataframe(dataset, use_container_width=True)