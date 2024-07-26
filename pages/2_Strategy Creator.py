import streamlit as st

from libraries.data import *
from libraries.plots import *

dataset = getData()

st.title("Fear Greed Index Strategy Creator")

num_days = st.slider('Select Number of Past Days to Analyze', 30, len(dataset), 825)
dataset = dataset.tail(num_days).reset_index(drop=True)

buy_threshold = st.slider('Buy Below Index', 0, 100, 25)
sell_threshold = st.slider('Sell Above Index', 0, 100, 76)
initial_balance = st.number_input('Start Balance (USD)', value=1000, step=1000)
trade_amount = st.number_input('Trade Amount (USD)', value=10, step=50)

if st.button('Run Simulation'):
    balances, btc_values, total_values, buy_signals, sell_signals = implement_strategy(
        dataset, buy_threshold, sell_threshold, initial_balance, trade_amount)
    fig1 = plot_buy_and_hold_comparison(dataset, balances, btc_values, total_values, buy_signals, sell_signals)
    fig2 = plot_strategy(dataset, balances, btc_values, total_values, buy_signals, sell_signals)
    
    st.pyplot(fig1)
    st.pyplot(fig2)
