import streamlit as st

import data as data_loader
from plots import *

data = data_loader.getData()

num_days = st.slider('Select Number of Past Days for Analysis', 1, len(data), 365)
data = data.tail(num_days).reset_index(drop=True)

st.pyplot(plot_btc_against_fgi(data))

data_loader.addFeatures(data)

st.pyplot(plot_btc_against_fgi_classification(data))
st.pyplot(lag_plot_btc_against_fgi(data))
st.pyplot(lag_plot_btc_against_fgi_classification(data))
