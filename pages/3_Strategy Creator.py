import streamlit as st
from libraries.plots import *
import pandas as pd
import plotly.graph_objects as go
from libraries.data import *
import json

st.set_page_config(
    initial_sidebar_state= "expanded"
)

dataset = getData()

st.title("Strategy Creator (Work in Progress)")

# should be in sidebar but moved due to bug in mobile where sidebar closes whenever date is adjusted
# Date range selection
st.header("Date Range Selection")
date_range = st.date_input("Select Date Range",
                           [dataset['timestamp'].min().date(), dataset['timestamp'].max().date()],
                           min_value=dataset['timestamp'].min().date(),
                           max_value=dataset['timestamp'].max().date())

if len(date_range) == 2:
    start_date, end_date = pd.to_datetime(date_range)
    dataset = dataset[(dataset['timestamp'] >= start_date) & (dataset['timestamp'] <= end_date)]

# Features selection
st.sidebar.header("Strategy Configuration")

# Load configuration from file (if uploaded)
uploaded_file = st.sidebar.file_uploader(
    label="Upload Strategy Configuration",
    type="json",
    help="Upload a previously saved configuration file.",
)

# Define default configuration
default_config = {
    'moving_avg_enabled': False,
    'short_term_ma_period': 10,
    'long_term_ma_period': 50,
    'fear_greed_enabled': False,
    'fear_greed_buy_threshold': 25,
    'fear_greed_sell_threshold': 76,
    'rsi_enabled': False,
    'rsi_period': 14,
    'rsi_buy_threshold': 30,
    'rsi_sell_threshold': 70,
    'bollinger_enabled': False,
    'bollinger_std_dev_multiplier': 2.0,
    'momentum_enabled': False,
    'momentum_period': 14,
    'stop_loss_enabled': False,
    'stop_loss_percentage': 5.0,
    'take_profit_enabled': False,
    'take_profit_percentage': 10.0,
    'dollar_cost_avg_enabled': False,
    'dollar_cost_avg_period': 'Daily',
    'initial_balance': 1000,
    'trade_amount': 10
}

# Load configuration from file if uploaded
if uploaded_file is not None:
    try:
        config = json.load(uploaded_file)
        st.success("Configuration loaded successfully!")
    except json.JSONDecodeError:
        st.error("Invalid JSON file. Please upload a valid configuration file.")
        config = default_config
    except KeyError as e:
        st.error(f"Missing key in configuration file: {str(e)}")
        config = default_config
else:
    config = default_config

# Fear Greed Index
st.sidebar.markdown("**Fear Greed Index**", help="Measures overall market sentiment. The index helps identify when the market is too fearful or too greedy. Buy when the index is below the threshold; sell when it's above.")
fear_greed_enabled = st.sidebar.checkbox('Enable Fear Greed Index Strategy', value=config['fear_greed_enabled'])
fear_greed_buy_threshold = st.sidebar.number_input('Buy Below Index', min_value=0, max_value=100, value=config['fear_greed_buy_threshold'], disabled=not fear_greed_enabled)
fear_greed_sell_threshold = st.sidebar.number_input('Sell Above Index', min_value=0, max_value=100, value=config['fear_greed_sell_threshold'], disabled=not fear_greed_enabled)

# Moving Average
st.sidebar.markdown("**Moving Average Crossover**", help="Uses two averages to spot trends. The short-term average reacts quickly to price changes, while the long-term average is slower. Buy when the short-term average crosses above the long-term average; sell when it crosses below.")
moving_avg_enabled = st.sidebar.checkbox('Enable Moving Average Crossover Strategy', value=config['moving_avg_enabled'])
short_term_ma_period = st.sidebar.number_input('Short-term Moving Average (SMA) Period (days)', min_value=1, max_value=None, value=config['short_term_ma_period'], disabled=not moving_avg_enabled)
long_term_ma_period = st.sidebar.number_input('Long-term Moving Average (LMA) Period', min_value=1, max_value=None, value=config['long_term_ma_period'], disabled=not moving_avg_enabled)

# RSI
st.sidebar.markdown("**Relative Strength Index (RSI)**", help="Shows how fast prices are moving up or down. RSI values above 70 suggest the asset is overbought (possibly a sell signal), while values below 30 suggest it is oversold (possibly a buy signal).")
rsi_enabled = st.sidebar.checkbox('Enable Relative Strength Index (RSI) Strategy', value=config['rsi_enabled'])
rsi_period = st.sidebar.number_input('RSI Period (days)', min_value=1, max_value=None, value=config['rsi_period'], disabled=not rsi_enabled)
rsi_buy_threshold = st.sidebar.number_input('Buy Below Signal', min_value=0, max_value=100, value=config['rsi_buy_threshold'], disabled=not rsi_enabled)
rsi_sell_threshold = st.sidebar.number_input('Sell Above Signal', min_value=0, max_value=100, value=config['rsi_sell_threshold'], disabled=not rsi_enabled)

# Bollinger Bands
st.sidebar.markdown("**Bollinger Bands**", help="Creates a middle band (average price) and two outer bands (standard deviations away from the average). A price below the lower band might indicate a buying opportunity, while a price above the upper band might suggest selling.")
bollinger_enabled = st.sidebar.checkbox('Enable Bollinger Bands Strategy', value=config['bollinger_enabled'])
bollinger_std_dev_multiplier = st.sidebar.number_input('Bollinger Band Standard Deviation Multiplier', min_value=1.0, max_value=5.0, value=config['bollinger_std_dev_multiplier'], step=0.1, disabled=not bollinger_enabled)

# Momentum
st.sidebar.markdown("**Simple Momentum**", help="Measures how much the price has changed over a set period. Buy when the momentum (price change over a set period) is positive; sell when it's negative.")
momentum_enabled = st.sidebar.checkbox('Enable Simple Momentum Strategy', value=config['momentum_enabled'])
momentum_period = st.sidebar.number_input('Momentum Period (days)', min_value=1, max_value=None, value=config['momentum_period'], disabled=not momentum_enabled)

# Stop-Loss and Take-Profit Rules
st.sidebar.header("Stop-Loss and Take-Profit Rules")
st.sidebar.markdown("**Stop-Loss**", help="Automatically sell if the price falls below the set percentage of the purchase price.")
stop_loss_enabled = st.sidebar.checkbox('Enable Stop-Loss', value=config['stop_loss_enabled'])
stop_loss_percentage = st.sidebar.number_input('Stop-Loss Percentage', min_value=0.0, max_value=100.0, value=config['stop_loss_percentage'], step=1.0, disabled=not stop_loss_enabled)

st.sidebar.markdown("**Take-Profit**", help="Automatically sell if the price rises above the set percentage of the purchase price.")
take_profit_enabled = st.sidebar.checkbox('Enable Take-Profit', value=config['take_profit_enabled'])
take_profit_percentage = st.sidebar.number_input('Take-Profit Percentage', min_value=0.0, max_value=100.0, value=config['take_profit_percentage'], step=1.0, disabled=not take_profit_enabled)

# Time-Based Rules
st.sidebar.header("Time-Based Rules (not implemented yet)")
st.sidebar.markdown("**Dollar-Cost Averaging**", help="Invest a fixed amount at regular intervals, regardless of price.")
dollar_cost_avg_enabled = st.sidebar.checkbox('Enable Dollar-Cost Averaging', value=config['dollar_cost_avg_enabled'])
dollar_cost_avg_period = st.sidebar.selectbox('Select Period', ['Daily', 'Weekly', 'Monthly'], index=['Daily', 'Weekly', 'Monthly'].index(config['dollar_cost_avg_period']), disabled=not dollar_cost_avg_enabled)

initial_balance = st.sidebar.number_input('Start Balance (USD)', min_value=0, value=config['initial_balance'], step=1000)
trade_amount = st.sidebar.number_input('Trade Amount (USD)', min_value=0, value=config['trade_amount'], step=50)

# Update config with current UI values
config = {
    'moving_avg_enabled': moving_avg_enabled,
    'short_term_ma_period': short_term_ma_period,
    'long_term_ma_period': long_term_ma_period,
    'fear_greed_enabled': fear_greed_enabled,
    'fear_greed_buy_threshold': fear_greed_buy_threshold,
    'fear_greed_sell_threshold': fear_greed_sell_threshold,
    'rsi_enabled': rsi_enabled,
    'rsi_period': rsi_period,
    'rsi_buy_threshold': rsi_buy_threshold,
    'rsi_sell_threshold': rsi_sell_threshold,
    'bollinger_enabled': bollinger_enabled,
    'bollinger_std_dev_multiplier': bollinger_std_dev_multiplier,
    'momentum_enabled': momentum_enabled,
    'momentum_period': momentum_period,
    'stop_loss_enabled': stop_loss_enabled,
    'stop_loss_percentage': stop_loss_percentage,
    'take_profit_enabled': take_profit_enabled,
    'take_profit_percentage': take_profit_percentage,
    'dollar_cost_avg_enabled': dollar_cost_avg_enabled,
    'dollar_cost_avg_period': dollar_cost_avg_period,
    'initial_balance': initial_balance,
    'trade_amount': trade_amount
}

config_json = json.dumps(config)

# Add a streamlit button to download the config as a JSON file
st.sidebar.download_button(
    label="Download Strategy Configuration",
    file_name="config.json",
    mime="application/json",
    data=config_json,
    help="Save your settings as a file for easy reuse later.",
)

addFeatures(dataset)
addSignals(dataset, config)

balances, btc_values, total_values, buy_signals, sell_signals = implement_strategy(dataset, config)
    
# Create a DataFrame with the portfolio composition
portfolio_df = pd.DataFrame({
    'Date': dataset['timestamp'],
    'USD Balance': balances,
    'BTC Value': btc_values,
    'Total Value': total_values
})

# Plot portfolio balance
plot_portfolio(portfolio_df)
plot_signals(dataset, buy_signals, sell_signals)
plot_strategy_signals(dataset)