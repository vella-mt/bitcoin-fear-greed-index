import requests
import pandas as pd
import yfinance as yf
from libraries.trading import *
import streamlit as st

@st.cache_data(ttl="1d")
def getData(tailDays=0):
    # Fetch Fear and Greed Index data
    r = requests.get('https://api.alternative.me/fng/?limit=0')
    df = pd.DataFrame(r.json()['data'])
    df['value'] = df['value'].astype(int)
    df['timestamp'] = pd.to_datetime(df['timestamp'].astype(int), unit='s')
    df = df.set_index('timestamp')
    df = df.rename(columns={'value': 'fear_greed'})
    df = df.drop(['time_until_update'], axis=1)

    # Fetch Bitcoin data history
    df1 = yf.download('BTC-USD', interval='1d')[['Close']].copy()
    df1 = df1.rename(columns={'Close': 'close'})
    df1.index.name = 'timestamp'
    df1 = df1.reset_index()
    df1['timestamp'] = pd.to_datetime(df1['timestamp']).dt.tz_localize(None)
    df1 = df1.set_index('timestamp')

    # Merge the two dataframes
    data = df.merge(df1, on='timestamp')
    data = data.sort_index()
    data = data.reset_index()

    if tailDays > 0:
        data = data.tail(tailDays).reset_index(drop=True)

    return data

def addFeatures(data):
    data['timestamp'] = pd.to_datetime(data['timestamp'])

    # Existing color mapping
    classification_colors = {
        'Extreme Fear': 'red',
        'Fear': 'orange',
        'Neutral': 'gray',
        'Greed': 'lightblue',
        'Extreme Greed': 'blue'
    }
    data['color'] = data['value_classification'].map(classification_colors)

    # Existing features
    data['close_tomorrow'] = data['close'].shift(-1)
    data['close_change'] = data['close'].pct_change()
    data['fear_greed_tomorrow'] = data['fear_greed'].shift(-1)
    data['fear_greed_change'] = data['fear_greed'].pct_change()

    # Moving Averages (using default periods)
    data['ma_close_short'] = data['close'].rolling(window=10).mean()
    data['ma_close_long'] = data['close'].rolling(window=50).mean()

    # RSI (using default period)
    data['rsi'] = calculate_rsi(data, 14)

    # Bollinger Bands (using default parameters)
    data['bollinger_mid'], data['bollinger_upper'], data['bollinger_lower'] = calculate_bollinger_bands(data, 20, 2.0)

    # Momentum (using default period)
    data['momentum'] = calculate_momentum(data, 14)

    return data

def addSignals(data, config):
    # Moving Averages
    if config['moving_avg_enabled']:
        data['ma_close_short'] = data['close'].rolling(window=config['short_term_ma_period']).mean()
        data['ma_close_long'] = data['close'].rolling(window=config['long_term_ma_period']).mean()
        data['ma_buy_signal'] = data['ma_close_short'] > data['ma_close_long']
        data['ma_sell_signal'] = data['ma_close_short'] < data['ma_close_long']

    # Fear and Greed Index
    if config['fear_greed_enabled']:
        data['fear_greed_buy_signal'] = data['fear_greed'] < config['fear_greed_buy_threshold']
        data['fear_greed_sell_signal'] = data['fear_greed'] > config['fear_greed_sell_threshold']

    # RSI
    if config['rsi_enabled']:
        data['rsi'] = calculate_rsi(data, config['rsi_period'])
        data['rsi_buy_signal'] = data['rsi'] < config['rsi_buy_threshold']
        data['rsi_sell_signal'] = data['rsi'] > config['rsi_sell_threshold']

    # Bollinger Bands
    if config['bollinger_enabled']:
        data['bollinger_mid'], data['bollinger_upper'], data['bollinger_lower'] = calculate_bollinger_bands(data, 20, config['bollinger_std_dev_multiplier'])
        data['bollinger_buy_signal'] = data['close'] < data['bollinger_lower']
        data['bollinger_sell_signal'] = data['close'] > data['bollinger_upper']

    # Momentum
    if config['momentum_enabled']:
        data['momentum'] = calculate_momentum(data, config['momentum_period'])
        data['momentum_buy_signal'] = data['momentum'] > 0
        data['momentum_sell_signal'] = data['momentum'] < 0

    return data
