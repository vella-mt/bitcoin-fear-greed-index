import streamlit as st
import plotly.graph_objects as go
import pandas as pd

# Define the strategy implementation function

def count_signals(row, signal_type):
        signal_columns = [
            f'ma_{signal_type}_signal',
            f'fear_greed_{signal_type}_signal',
            f'rsi_{signal_type}_signal',
            f'bollinger_{signal_type}_signal',
            f'momentum_{signal_type}_signal'
        ]
        return sum(row.get(col, False) for col in signal_columns if col in row.index)

def implement_strategy(data, config):    
    balance = config['initial_balance']
    btc_held = 0
    balances = []
    btc_values = []
    total_values = []
    buy_signals = []
    sell_signals = []

    trade_amount = config['trade_amount']
    stop_loss_enabled = config['stop_loss_enabled']
    stop_loss_percentage = config['stop_loss_percentage'] / 100
    take_profit_enabled = config['take_profit_enabled']
    take_profit_percentage = config['take_profit_percentage'] / 100

    last_buy_price = None

    def place_buy_order(row):
        nonlocal balance, btc_held, last_buy_price
        btc_to_buy = min(trade_amount, balance) / row['close']
        btc_held += btc_to_buy
        balance -= min(trade_amount, balance)
        buy_signals.append(row.name)
        last_buy_price = row['close']

    def place_sell_order(row):
        nonlocal balance, btc_held, last_buy_price
        btc_to_sell = min(trade_amount / row['close'], btc_held)
        balance += btc_to_sell * row['close']
        btc_held -= btc_to_sell
        sell_signals.append(row.name)
        if btc_held == 0:
            last_buy_price = None

    for i, row in data.iterrows():
        buy_signal_count = count_signals(row, 'buy')
        sell_signal_count = count_signals(row, 'sell')

        # TODO: fix logic to compare buy with sell signals
        buy_threshold = 0
        sell_threshold = 0

        # print(f"Stop loss enabled: {stop_loss_enabled}")
        # print(f"Take profit enabled: {take_profit_enabled}")
        # print(f"Last buy price: {last_buy_price}")

        # Check for stop-loss and take-profit
        if stop_loss_enabled and last_buy_price is not None:
            if row['close'] <= last_buy_price * (1 - stop_loss_percentage):
                print("STOP LOSS ORDER")
                place_sell_order(row)

        elif take_profit_enabled and last_buy_price is not None:
            if row['close'] >= last_buy_price * (1 + take_profit_percentage):
                print("TAKE PROFIT ORDER")
                place_sell_order(row)

        elif buy_signal_count > sell_signal_count and buy_signal_count >= buy_threshold and balance > 0:
            place_buy_order(row)
        elif sell_signal_count > buy_signal_count and sell_signal_count >= sell_threshold and btc_held > 0:
            place_sell_order(row)
        
        btc_value = btc_held * row['close']
        total_value = balance + btc_value
        
        balances.append(balance)
        btc_values.append(btc_value)
        total_values.append(total_value)

    return balances, btc_values, total_values, buy_signals, sell_signals
    

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

    col1, col2 = st.columns(2)
    col1.metric(label="Final Portfolio Value", value=f"{final_value: .2f} USD", delta=f"{final_value - initial_value: .2f} USD")
    col2.metric(label="Total Return", value=f"{total_return: .2f}%",delta=f"{total_return: .2f}%")


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

def plot_strategy_signals(dataset):
    st.subheader("Strategy Buy/Sell Signals")

    # Count signals
    buy_counts = []
    sell_counts = []

    for _, row in dataset.iterrows():
        buy_count = count_signals(row, 'buy')
        sell_count = count_signals(row, 'sell')
        buy_counts.append(buy_count)
        sell_counts.append(sell_count)

    # Create the figure
    fig = go.Figure()

    # Add Bitcoin price line
    fig.add_trace(go.Scatter(
        x=dataset['timestamp'],
        y=dataset['close'],
        mode='lines',
        name='Bitcoin Price',
        line=dict(color='#FFA500', width=1)
    ))

    # Add buy signal count
    fig.add_trace(go.Bar(
        x=dataset['timestamp'],
        y=buy_counts,
        name='Buy Signals',
        marker_color='rgba(0, 255, 0, 0.9)'
    ))

    # Add sell signal count
    fig.add_trace(go.Bar(
        x=dataset['timestamp'],
        y=[-count for count in sell_counts],  # Negative to show below x-axis
        name='Sell Signals',
        marker_color='rgba(255, 0, 0, 0.9)'
    ))

    # Update layout
    fig.update_layout(
        title='Bitcoin Price with Strategy Buy/Sell Signals',
        xaxis_title='Date',
        yaxis_title='Price (USD) / Signal Count',
        legend_title='Legend',
        height=600,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        hovermode="x unified"
    )

    # Create a secondary y-axis for the signal counts
    fig.update_layout(
        yaxis2=dict(
            title="Signal Count",
            overlaying="y",
            side="right",
            range=[-max(max(sell_counts), max(buy_counts)) * 1.1,
                   max(max(sell_counts), max(buy_counts)) * 1.1]
        )
    )

    # Assign the bar traces to the secondary y-axis
    fig.data[1].update(yaxis="y2")
    fig.data[2].update(yaxis="y2")

    # Show the plot
    st.plotly_chart(fig, use_container_width=True)
