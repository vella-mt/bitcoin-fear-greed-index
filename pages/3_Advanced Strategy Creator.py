import streamlit as st

# Title
st.title("Advanced Strategy Creator")

num_days = st.slider('Select Number of Past Days to Analyze', min_value=1, max_value=365, value=30)

# Features selection
st.header("Strategy Configuration")

# Fear Greed Index
st.write("**Fear Greed Index:** Measures overall market sentiment. The index helps identify when the market is too fearful or too greedy. Buy when the index is below the threshold; sell when it's above.")
fear_greed_enabled = st.checkbox('Enable Fear Greed Index Strategy')
fear_greed_metric1 = st.number_input('Buy Below Index', min_value=0, max_value=100, value=25, disabled=not fear_greed_enabled)
fear_greed_metric2 = st.number_input('Sell Above Index', min_value=0, max_value=100, value=76, disabled=not fear_greed_enabled)

# Moving Average
st.write("**Moving Average Crossover:** Uses two averages to spot trends. The short-term average reacts quickly to price changes, while the long-term average is slower. Buy when the short-term average crosses above the long-term average; sell when it crosses below.")
moving_avg_enabled = st.checkbox('Enable Moving Average Crossover Strategy')
moving_avg_metric1 = st.number_input('Short-term Moving Average (SMA) Period (days)', min_value=1, max_value=None, value=10, disabled=not moving_avg_enabled)
moving_avg_metric2 = st.number_input('Long-term Moving Average (LMA) Period', min_value=1, max_value=None, value=50, disabled=not moving_avg_enabled)

# RSI
st.write("**Relative Strength Index (RSI):** Shows how fast prices are moving up or down. RSI values above 70 suggest the asset is overbought (possibly a sell signal), while values below 30 suggest it is oversold (possibly a buy signal).")
rsi_enabled = st.checkbox('Enable Relative Strength Index (RSI) Strategy')
vwap_metric1 = st.number_input('RSI Period (days)', min_value=1, max_value=None, value=14, disabled=not rsi_enabled)
rsi_metric1 = st.number_input('Buy Below Signal', min_value=0, max_value=100, value=30, disabled=not rsi_enabled)
rsi_metric2 = st.number_input('Sell Above Signal', min_value=0, max_value=100, value=70, disabled=not rsi_enabled)

# Bollinger Bands
st.write("**Bollinger Bands:** Creates a middle band (average price) and two outer bands (standard deviations away from the average). A price below the lower band might indicate a buying opportunity, while a price above the upper band might suggest selling.")
bollinger_enabled = st.checkbox('Enable Bollinger Bands Strategy')
bollinger_metric1 = st.number_input('Bollinger Band Standard Deviation Multiplier', min_value=1.0, max_value=5.0, value=2.0, step=0.1, disabled=not bollinger_enabled)

# Momentum
st.write("**Simple Momentum:** Measures how much the price has changed over a set period. Buy when the momentum (price change over a set period) is positive; sell when it's negative.")
momentum_enabled = st.checkbox('Enable Simple Momentum Strategy')
momentum_metric1 = st.number_input('Momentum Period (days)', min_value=1, max_value=None, value=14, disabled=not momentum_enabled)

st.write("**Volume-Weighted Average Price (VWAP):** Calculates the average price of an asset, weighted by the volume traded. Buy when the price is below the VWAP (average price weighted by volume); sell when it's above.")
vwap_enabled = st.checkbox('Enable Volume-Weighted Average Price (VWAP) Strategy')
vwap_metric1 = st.number_input('VWAP Period (days)', min_value=1, max_value=None, value=30, disabled=not vwap_enabled)

st.header("Stop-Loss and Take-Profit Rules")
st.write("**Stop-Loss:** Automatically sell if the price falls below the set percentage of the purchase price.")
st.write("**Take-Profit:** Automatically sell if the price rises above the set percentage of the purchase price.")
stop_loss_enabled = st.checkbox('Enable Stop-Loss')
stop_loss_percentage = st.number_input('Stop-Loss Percentage', min_value=0.0, max_value=100.0, value=5.0, step=0.1, disabled=not stop_loss_enabled)

take_profit_enabled = st.checkbox('Enable Take-Profit')
take_profit_percentage = st.number_input('Take-Profit Percentage', min_value=0.0, max_value=100.0, value=10.0, step=0.1, disabled=not take_profit_enabled)

# Time-Based Rules
st.header("Time-Based Rules")
st.write("**Dollar-Cost Averaging:** Invest a fixed amount at regular intervals, regardless of price.")
dollar_cost_avg_enabled = st.checkbox('Enable Dollar-Cost Averaging')
dollar_cost_avg_period = st.selectbox('Select Period', ['Daily', 'Weekly', 'Monthly'], disabled=not dollar_cost_avg_enabled)