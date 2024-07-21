import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.dates as mdates
import yfinance as yf
import numpy as np

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

# Streamlit UI
st.title('Bitcoin Trading based on Fear and Greed Index Strategy Simulator')

st.markdown("### Fear and Greed Index Value Classifications:")
st.markdown("- **Extreme Greed**: 76-100")
st.markdown("- **Greed**: 55-75")
st.markdown("- **Neutral**: 47-54")
st.markdown("- **Fear**: 26-46")
st.markdown("- **Extreme Fear**: 1-25")


num_days = st.slider('Number of Days to Analyze', 30, len(data), 825)

buy_threshold = st.slider('Buy Below Index', 0, 100, 25)
sell_threshold = st.slider('Sell Above Index', 0, 100, 76)
initial_balance = st.number_input('Start Balance (USD)', value=1000, step=1000)
trade_amount = st.number_input('Trade Amount (USD)', value=10, step=50)

data = data.tail(num_days).reset_index(drop=True)

# Define the strategy implementation function
def implement_strategy(data, buy_threshold, sell_threshold, initial_balance, trade_amount):
    balance = initial_balance
    btc_held = 0
    balances = [balance]
    btc_values = [0]
    total_values = [balance]
    buy_signals = []
    sell_signals = []

    for i, row in data.iterrows():
        if row['fear_greed'] <= buy_threshold and balance > 0:
            btc_to_buy = min(trade_amount, balance) / row['close']
            btc_held += btc_to_buy
            balance -= min(trade_amount, balance)
            buy_signals.append(i)
        elif row['fear_greed'] >= sell_threshold and btc_held > 0:
            btc_to_sell = min(trade_amount / row['close'], btc_held)
            balance += btc_to_sell * row['close']
            btc_held -= btc_to_sell
            sell_signals.append(i)
        
        btc_value = btc_held * row['close']
        total_value = balance + btc_value
        
        balances.append(balance)
        btc_values.append(btc_value)
        total_values.append(total_value)

    return balances, btc_values, total_values, buy_signals, sell_signals

# Define the plotting function
def plot_strategy(data, balances, btc_values, total_values, buy_signals, sell_signals):
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 16), sharex=True)
    
    ax1.plot(data['timestamp'], data['close'], label='Bitcoin Price', color='black', linewidth=2)
    ax1.scatter(data.loc[buy_signals, 'timestamp'], data.loc[buy_signals, 'close'], marker='^', color='green', s=100, label='Buy Signal')
    ax1.scatter(data.loc[sell_signals, 'timestamp'], data.loc[sell_signals, 'close'], marker='v', color='red', s=100, label='Sell Signal')
    ax1.set_ylabel('Bitcoin Price (USD)')
    ax1.set_title('Bitcoin Price with Buy/Sell Signals')
    ax1.legend(loc='upper left')
    ax1.grid(True, linestyle='--', alpha=0.5)
    ax1.set_yscale('log')

    ax2.fill_between(data['timestamp'], balances[1:], color='green', alpha=0.6, label='Cash Balance')
    ax2.fill_between(data['timestamp'], balances[1:], total_values[1:], color='orange', alpha=0.6, label='BTC Balance')
    ax2.scatter(data.loc[buy_signals, 'timestamp'], [total_values[i+1] for i in buy_signals], marker='o', color='green', s=50, label='Buy')
    ax2.scatter(data.loc[sell_signals, 'timestamp'], [total_values[i+1] for i in sell_signals], marker='o', color='red', s=50, label='Sell')
    ax2.set_ylabel('Balance (USD)')
    ax2.set_title('Portfolio Composition Over Time')
    ax2.legend(loc='upper left')
    ax2.grid(True, linestyle='--', alpha=0.5)

    ax2.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    ax2.xaxis.set_major_locator(mdates.AutoDateLocator())
    fig.autofmt_xdate()

    initial_value = total_values[0]
    final_value = total_values[-1]
    roi = (final_value - initial_value) / initial_value * 100
    buy_hold_final_value = (initial_value / data['close'].iloc[0]) * data['close'].iloc[-1]
    buy_hold_roi = (buy_hold_final_value - initial_value) / initial_value * 100
    
    roi_text = f'Strategy ROI: {roi:.2f}%\nBuy & Hold ROI: {buy_hold_roi:.2f}%'
    plt.figtext(0.01, 0.01, roi_text, fontsize=12, ha='left')

    ax2.annotate(f'Final Portfolio Value: ${final_value:,.2f}', 
                 xy=(data['timestamp'].iloc[-1], final_value),
                 xytext=(30, 30), textcoords='offset points',
                 bbox=dict(boxstyle='round,pad=0.5', fc='yellow', alpha=0.5),
                 arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0'))

    plt.tight_layout()
    plt.subplots_adjust(bottom=0.1)  # Adjust bottom spacing to remove white space

    return fig

def plot_strategy2(data, balances, btc_values, total_values, buy_signals, sell_signals):
    fig, ax = plt.subplots(figsize=(12, 8))

    # Calculate the performance of a buy-and-hold strategy
    initial_btc = total_values[0] / data['close'].iloc[0]
    buy_hold_values = data['close'] * initial_btc

    # Plot Bitcoin price
    ax.plot(data['timestamp'], data['close'], label='Bitcoin Price', color='black', linewidth=2)

    # Plot total portfolio value
    ax.plot(data['timestamp'], total_values[1:], label='Portfolio Value', color='blue', linewidth=2)

    # Plot buy-and-hold strategy
    ax.plot(data['timestamp'], buy_hold_values, label='Buy & Hold Value', color='gray', linestyle='--', linewidth=2)

    # Fill the area between portfolio value and buy-and-hold strategy
    ax.fill_between(data['timestamp'], buy_hold_values, total_values[1:], 
                    where=(np.array(total_values[1:]) > buy_hold_values), 
                    color='green', alpha=0.3, label='Outperforming Buy & Hold')
    ax.fill_between(data['timestamp'], buy_hold_values, total_values[1:], 
                    where=(np.array(total_values[1:]) <= buy_hold_values), 
                    color='red', alpha=0.3, label='Underperforming Buy & Hold')

    # Mark buy signals
    ax.scatter(data.iloc[buy_signals]['timestamp'], data.iloc[buy_signals]['close'], marker='^', color='green', s=100, 
               label='Buy Signal', edgecolor='black', zorder=5)

    # Mark sell signals
    ax.scatter(data.iloc[sell_signals]['timestamp'], data.iloc[sell_signals]['close'], marker='v', color='red', s=100, 
               label='Sell Signal', edgecolor='black', zorder=5)

    # Customize the y-axis
    ax.set_ylabel('Value (USD)', fontsize=12)
    ax.tick_params(axis='y', labelsize=10)
    ax.set_yscale('log')  # Use log scale for better visibility of relative changes

    # Customize x-axis
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    ax.xaxis.set_major_locator(mdates.AutoDateLocator())
    fig.autofmt_xdate()

    # Add a legend
    ax.legend(loc='upper left', bbox_to_anchor=(1, 1), fontsize=10)

    # Add grid lines
    ax.grid(True, linestyle='--', alpha=0.5)

    # Set the title
    plt.title('Trading Strategy Performance vs Buy & Hold', fontsize=16)

    # Annotate the final portfolio value
    final_value = total_values[-1]
    ax.annotate(f'Final Portfolio Value: ${final_value:,.2f}', 
                xy=(data['timestamp'].iloc[-1], final_value),
                xytext=(30, 30), textcoords='offset points',
                bbox=dict(boxstyle='round,pad=0.5', fc='yellow', alpha=0.5),
                arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0'))

    # Calculate and display ROI and comparison to buy-and-hold
    initial_value = total_values[0]
    roi = (final_value - initial_value) / initial_value * 100
    buy_hold_roi = (buy_hold_values.iloc[-1] - initial_value) / initial_value * 100
    plt.figtext(-0.02, -0.02, f'Strategy ROI: {roi:.2f}%\nBuy & Hold ROI: {buy_hold_roi:.2f}%', fontsize=12, ha='left')

    # Adjust layout and show plot
    plt.tight_layout()
    return fig

if st.button('Run Simulation'):
    balances, btc_values, total_values, buy_signals, sell_signals = implement_strategy(
        data, buy_threshold, sell_threshold, initial_balance, trade_amount)
    fig = plot_strategy(data, balances, btc_values, total_values, buy_signals, sell_signals)
    fig2 = plot_strategy2(data, balances, btc_values, total_values, buy_signals, sell_signals)
    
    st.pyplot(fig2)
    st.pyplot(fig)
