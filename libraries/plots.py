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

        # total_signals = buy_signal_count + sell_signal_count
        # buy_threshold = max(3, total_signals // 2 + 1)  # At least 3, or more than half of total signals

        buy_threshold = 1

        if buy_signal_count >= buy_threshold and balance > 0:
            place_buy_order(row)
        elif sell_signal_count > buy_signal_count and sell_signal_count >= 3 and btc_held > 0:
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

def plot_portfolio_balance(dataset, portfolio_df):
    
    st.header("Portfolio Performance")

    # Ensure 'Date' column is in datetime format
    portfolio_df['Date'] = pd.to_datetime(portfolio_df['Date'])

    # Create a line plot for portfolio composition
    fig = go.Figure()

    fig.add_trace(go.Scatter(x=portfolio_df['Date'], y=portfolio_df['USD Balance'],
                             mode='lines', name='USD Balance'))
    fig.add_trace(go.Scatter(x=portfolio_df['Date'], y=portfolio_df['BTC Value'],
                             mode='lines', name='BTC Value'))
    fig.add_trace(go.Scatter(x=portfolio_df['Date'], y=portfolio_df['Total Value'],
                             mode='lines', name='Total Value'))

    fig.update_layout(title='Portfolio Composition Over Time',
                      xaxis_title='Date',
                      yaxis_title='Value (USD)',
                      legend_title='Asset')

    st.plotly_chart(fig)

    # Calculate and display performance metrics
    initial_value = portfolio_df['Total Value'].iloc[0]
    final_value = portfolio_df['Total Value'].iloc[-1]
    total_return = (final_value - initial_value) / initial_value * 100

    st.metric("Total Return", f"{total_return:.2f}%")

    # Allow users to select a specific date range
    date_range = st.date_input("Select Date Range", 
                               [portfolio_df['Date'].min().date(), portfolio_df['Date'].max().date()],
                               min_value=portfolio_df['Date'].min().date(),
                               max_value=portfolio_df['Date'].max().date())

    if len(date_range) == 2:
        start_date, end_date = pd.to_datetime(date_range)
        filtered_df = portfolio_df[(portfolio_df['Date'] >= start_date) & (portfolio_df['Date'] <= end_date)]

        # Create a line plot for the selected date range
        fig = go.Figure()

        fig.add_trace(go.Scatter(x=filtered_df['Date'], y=filtered_df['USD Balance'],
                                 mode='lines', name='USD Balance'))
        fig.add_trace(go.Scatter(x=filtered_df['Date'], y=filtered_df['BTC Value'],
                                 mode='lines', name='BTC Value'))
        fig.add_trace(go.Scatter(x=filtered_df['Date'], y=filtered_df['Total Value'],
                                 mode='lines', name='Total Value'))

        fig.update_layout(title=f'Portfolio Composition ({start_date.date()} to {end_date.date()})',
                          xaxis_title='Date',
                          yaxis_title='Value (USD)',
                          legend_title='Asset')

        st.plotly_chart(fig)

        # Calculate and display performance metrics for the selected range
        range_initial_value = filtered_df['Total Value'].iloc[0]
        range_final_value = filtered_df['Total Value'].iloc[-1]
        range_return = (range_final_value - range_initial_value) / range_initial_value * 100

        st.metric("Return for Selected Range", f"{range_return:.2f}%")
