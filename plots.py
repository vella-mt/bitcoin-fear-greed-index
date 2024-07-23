import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import seaborn as sns


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

def plot_buy_and_hold_comparison(data, balances, btc_values, total_values, buy_signals, sell_signals):
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

def plot_btc_against_fgi(data):
    # Create a plot with dual y-axes
    fig, ax1 = plt.subplots(figsize=(16, 8))

    # Plot BTC price on the first y-axis
    ax1.plot(data['timestamp'], data['close'], color='tab:blue', label='BTC Price')
    ax1.set_xlabel('Date', fontsize=12)
    ax1.set_ylabel('BTC Price (EUR)', color='tab:blue', fontsize=12)
    ax1.tick_params(axis='y', labelcolor='tab:blue')

    # Create a second y-axis to plot the Fear and Greed Index value
    ax2 = ax1.twinx()
    ax2.plot(data['timestamp'], data['fear_greed'], color='tab:orange', label='Fear and Greed Index')
    ax2.set_ylabel('Fear and Greed Index Value', color='tab:orange', fontsize=12)
    ax2.tick_params(axis='y', labelcolor='tab:orange')

    # Customize x-axis
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    ax1.xaxis.set_major_locator(mdates.AutoDateLocator())
    fig.autofmt_xdate()  # Rotate and align the tick labels

    # Show gridlines
    ax1.grid(True, linestyle='--', alpha=0.3)

    # Add title and legend
    plt.title('Bitcoin Price and Fear and Greed Index Over Time', fontsize=16)
    fig.tight_layout()  # To ensure the labels do not overlap
    fig.legend(loc='upper left', bbox_to_anchor=(0.1, 1), fontsize=10)

    return fig

def plot_btc_against_fgi_classification(data):
    ordered_classifications = [
        ('Extreme Fear', 'red'),
        ('Fear', 'orange'),
        ('Neutral', 'gray'),
        ('Greed', 'lightblue'),
        ('Extreme Greed', 'blue')
    ]

    # Create the plot
    fig, ax = plt.subplots(figsize=(16, 10))

    # Plot Fear/Greed Index as color-coded bars up to the Bitcoin price
    bar_width = 0.8  # Width of each bar
    bars = ax.bar(data['timestamp'], data['close'], width=bar_width, 
                color=data['color'], alpha=0.6)

    # Plot Bitcoin price as a line on top of the bars
    line = ax.plot(data['timestamp'], data['close'], color='black', label='Bitcoin Price')

    # Customize y-axis
    ax.set_ylabel('Bitcoin Price (USD)', color='black')
    ax.tick_params(axis='y', labelcolor='black')

    # Customize x-axis
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    ax.xaxis.set_major_locator(mdates.AutoDateLocator())
    fig.autofmt_xdate()

    # Set title and labels
    plt.title('Bitcoin Price vs Fear/Greed Index Classification', fontsize=16)
    ax.set_xlabel('Date', fontsize=12)

    # Add legend for Fear/Greed Index classifications
    legend_elements = [plt.Rectangle((0,0),1,1, facecolor=color, edgecolor='none', alpha=0.6, label=class_name) 
                    for class_name, color in ordered_classifications]
    legend_elements += line
    ax.legend(handles=legend_elements, loc='upper left', title='Legend', fontsize=10)

    # Show gridlines
    ax.grid(True, linestyle='--', alpha=0.3)

    # Adjust layout and display the plot
    plt.tight_layout()
    return fig

def lag_plot_btc_against_fgi(data):
    # Create the lag plot
    plt.figure(figsize=(12, 8))
    sns.scatterplot(x='fear_greed', y='next_day_close_change', data=data, alpha=0.6)

    plt.title("Lag Plot: Fear/Greed Index vs Next Day's Bitcoin Price Change", fontsize=16)
    plt.xlabel("Fear/Greed Index Value (Day t)", fontsize=12)
    plt.ylabel("Bitcoin Price Change % (Day t+1)", fontsize=12)

    # Add a horizontal line at y=0 to show the boundary between positive and negative changes
    plt.axhline(y=0, color='r', linestyle='--', alpha=0.5)

    # Add a vertical line at x=50 to show the boundary between fear and greed
    plt.axvline(x=50, color='g', linestyle='--', alpha=0.5)

    # Annotate the quadrants
    plt.text(25, 0.05, "Fear → Price Increase", fontsize=10, ha='center')
    plt.text(75, 0.05, "Greed → Price Increase", fontsize=10, ha='center')
    plt.text(25, -0.05, "Fear → Price Decrease", fontsize=10, ha='center')
    plt.text(75, -0.05, "Greed → Price Decrease", fontsize=10, ha='center')

    plt.tight_layout()

    return plt

def lag_plot_btc_against_fgi_classification(data):
    # Create a categorical order for the Fear/Greed Index classifications
    category_order = ['Extreme Fear', 'Fear', 'Neutral', 'Greed', 'Extreme Greed']

    # Ensure 'value_classification' is treated as a category with the specified order
    data['value_classification'] = pd.Categorical(data['value_classification'], categories=category_order, ordered=True)

    # Create the lag plot
    plt.figure(figsize=(14, 8))
    sns.boxplot(x='value_classification', y='next_day_close_change', data=data, 
                order=category_order, palette='RdYlGn')

    plt.title("Lag Plot: Fear/Greed Index Classification vs Next Day's Bitcoin Price Change", fontsize=16)
    plt.xlabel("Fear/Greed Index Classification (Day t)", fontsize=12)
    plt.ylabel("Bitcoin Price Change % (Day t+1)", fontsize=12)

    # Add a horizontal line at y=0 to show the boundary between positive and negative changes
    plt.axhline(y=0, color='r', linestyle='--', alpha=0.5)

    # Rotate x-axis labels for better readability
    plt.xticks(rotation=45)

    plt.tight_layout()
    
    return plt