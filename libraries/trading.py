def calculate_rsi(data, window):
    delta = data['close'].diff(1)
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.rolling(window=window, min_periods=1).mean()
    avg_loss = loss.rolling(window=window, min_periods=1).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def calculate_bollinger_bands(data, window, num_std_dev):
    rolling_mean = data['close'].rolling(window=window).mean()
    rolling_std = data['close'].rolling(window=window).std()
    upper_band = rolling_mean + (rolling_std * num_std_dev)
    lower_band = rolling_mean - (rolling_std * num_std_dev)
    return rolling_mean, upper_band, lower_band

def calculate_momentum(data, period):
    return data['close'].pct_change(periods=period)

def calculate_vwap(data, period):
    data['volume_price'] = data['close'] * data['volume']
    data['cumulative_volume'] = data['volume'].rolling(window=period).sum()
    data['cumulative_volume_price'] = data['volume_price'].rolling(window=period).sum()
    vwap = data['cumulative_volume_price'] / data['cumulative_volume']
    return vwap