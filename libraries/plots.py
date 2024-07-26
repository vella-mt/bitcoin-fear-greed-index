import streamlit as st
import plotly.graph_objects as go
import pandas as pd

# Define the strategy implementation function
def implement_strategy(data, initial_balance, trade_amount):
    balance = initial_balance
    btc_held = 0
    balances = []
    btc_values = []
    total_values = []
    buy_signals = []
    sell_signals = []

    def place_buy_order(row):
        nonlocal balance, btc_held
        btc_to_buy = min(trade_amount, balance) / row['close']
        btc_held += btc_to_buy
        balance -= min(trade_amount, balance)
        buy_signals.append(row.name)

    def place_sell_order(row):
        nonlocal balance, btc_held
        btc_to_sell = min(trade_amount / row['close'], btc_held)
        balance += btc_to_sell * row['close']
        btc_held -= btc_to_sell
        sell_signals.append(row.name)

    def count_signals(row, signal_type):
        signal_columns = [
            f'ma_{signal_type}_signal',
            f'fear_greed_{signal_type}_signal',
            f'rsi_{signal_type}_signal',
            f'bollinger_{signal_type}_signal',
            f'momentum_{signal_type}_signal'
        ]
        return sum(row.get(col, False) for col in signal_columns if col in row.index)

    for i, row in data.iterrows():
        buy_signal_count = count_signals(row, 'buy')
        sell_signal_count = count_signals(row, 'sell')

        # TODO: fix logic to compare buy with sell signals
        buy_threshold = 1
        sell_threshold = 1

        if buy_signal_count >= buy_threshold and balance > 0:
            place_buy_order(row)
        elif sell_signal_count > buy_signal_count and sell_signal_count >= sell_threshold and btc_held > 0:
            place_sell_order(row)
        
        btc_value = btc_held * row['close']
        total_value = balance + btc_value
        
        balances.append(balance)
        btc_values.append(btc_value)
        total_values.append(total_value)

    return balances, btc_values, total_values, buy_signals, sell_signals
    
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

import streamlit as st
import pandas as pd
import plotly.graph_objects as go

import streamlit as st
import plotly.graph_objects as go
import pandas as pd

def plot_portfolio(portfolio_df):
    st.header("Portfolio and Bitcoin Analysis")

    # Ensure 'Date' column is in datetime format
    portfolio_df['Date'] = pd.to_datetime(portfolio_df['Date'])

    # Set 'Date' as the index
    portfolio_df.set_index('Date', inplace=True)

    # Create a new dataframe for the stacked area chart
    chart_df = portfolio_df[['USD Balance', 'BTC Value']]

    # Plot portfolio balance
    st.subheader("Portfolio Performance")
    st.area_chart(chart_df, color=["#FE9F0D", "#119323"], height=500)

    # Reset index for further operations if needed
    portfolio_df.reset_index(inplace=True)

    # Calculate and display performance metrics
    initial_value = portfolio_df['Total Value'].iloc[0]
    final_value = portfolio_df['Total Value'].iloc[-1]
    total_return = (final_value - initial_value) / initial_value * 100

    st.metric("Total Return", f"{total_return:.2f}%")


def plot_signals(dataset, buy_signals, sell_signals):
    # Plot Bitcoin price with signals
    st.subheader("Bitcoin Price with Buy/Sell Signals")
    fig_bitcoin = go.Figure()

    # Add Bitcoin price line
    fig_bitcoin.add_trace(go.Scatter(
        x=dataset['timestamp'],
        y=dataset['close'],
        mode='lines',
        name='Bitcoin Price'
    ))

    # Add buy signals
    fig_bitcoin.add_trace(go.Scatter(
        x=dataset['timestamp'][buy_signals],
        y=dataset['close'][buy_signals],
        mode='markers',
        marker=dict(symbol='triangle-up', size=10, color='green'),
        name='Buy Signal'
    ))

    # Add sell signals
    fig_bitcoin.add_trace(go.Scatter(
        x=dataset['timestamp'][sell_signals],
        y=dataset['close'][sell_signals],
        mode='markers',
        marker=dict(symbol='triangle-down', size=10, color='red'),
        name='Sell Signal'
    ))

    fig_bitcoin.update_layout(
        title=f'Bitcoin Price with Buy/Sell Signals',
        xaxis_title='Date',
        yaxis_title='Price (USD)',
        legend_title='Legend',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )

    st.plotly_chart(fig_bitcoin)
