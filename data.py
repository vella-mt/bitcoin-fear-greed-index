import requests
import pandas as pd
import yfinance as yf
from trading import *

def getData(tailDays=0):
    # Fetch Fear and Greed Index data
    r = requests.get('https://api.alternative.me/fng/?limit=0')
    df = pd.DataFrame(r.json()['data'])
    df['value'] = df['value'].astype(int)
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s')
    df.set_index('timestamp', inplace=True)
    df.rename(columns={'value': 'fear_greed'}, inplace=True)
    df.drop(['time_until_update'], axis=1, inplace=True)

    # Fetch Bitcoin data history
    df1 = yf.download('BTC-USD', interval='1d')[['Close']]
    df1.rename(columns={'Close': 'close'}, inplace=True)
    df1.index.name = 'timestamp'
    df1['timestamp'] = df1.index
    df1.reset_index(drop=True, inplace=True)
    df1['timestamp'] = pd.to_datetime(df1['timestamp']).dt.tz_localize(None)
    df1.set_index('timestamp', inplace=True)

    # Merge the two dataframes
    data = df.merge(df1, on='timestamp')
    data.sort_index(inplace=True)
    data.reset_index(inplace=True)

    if tailDays > 0:
        data = data.tail(tailDays).reset_index(drop=True)

    return data

def addFeatures(data):
    data['timestamp'] = pd.to_datetime(data['timestamp'])

    # Define color map for value classification
    classification_colors = {
        'Extreme Fear': 'red',
        'Fear': 'orange',
        'Neutral': 'gray',
        'Greed': 'lightblue',
        'Extreme Greed': 'blue'
    }

    # Map the classification to colors
    data['color'] = data['value_classification'].map(classification_colors)

    data['close_tomorrow'] = data['close'].shift(-1)
    data['close_change'] = data['close'].pct_change()
    data['fear_greed_tomorrow'] = data['fear_greed'].shift(-1)
    data['fear_greed_change'] = data['fear_greed'].pct_change()
    data['ma_close_10'] = data['close'].rolling(window=10).mean()
    data['ma_close_50'] = data['close'].rolling(window=50).mean()
    data['ma_fear_greed_10'] = data['fear_greed'].rolling(window=10).mean()
    data['ma_fear_greed_50'] = data['fear_greed'].rolling(window=50).mean()
    data['roc_close'] = data['close'].pct_change(periods=10)
    data['roc_fear_greed'] = data['fear_greed'].pct_change(periods=10)
    data['next_day_close_change'] = data['close'].pct_change().shift(-1)

    data['rsi_14'] = calculate_rsi(data, 14)
    data['bollinger_mid'], data['bollinger_upper'], data['bollinger_lower'] = calculate_bollinger_bands(data, 20, 2)