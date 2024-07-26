import streamlit as st
from libraries.plots import *
from libraries.data import *
import pandas as pd
import plotly.express as px
import numpy as np

def calculate_window_changes(dataset, window_sizes=[7, 30]):
    for window in window_sizes:
        dataset[f'close_change_{window}d'] = dataset['close'].pct_change(periods=window) * 100
        dataset[f'fear_greed_avg_{window}d'] = dataset['fear_greed'].rolling(window=window).mean()
    return dataset.dropna()

def multi_window_scatter_plot(dataset, window_sizes=[7, 30]):
    for window in window_sizes:
        fig = px.scatter(dataset, 
                         x=f'fear_greed_avg_{window}d', 
                         y=f'close_change_{window}d',
                         color="value_classification",
                         hover_data=["timestamp"],
                         labels={f'fear_greed_avg_{window}d': f'{window}-Day Avg Fear & Greed Index',
                                 f'close_change_{window}d': f'{window}-Day Close Price Change (%)',
                                 "value_classification": "Classification"},
                         title=f'{window}-Day Avg Fear & Greed Index vs {window}-Day Close Price Change')
        
        fig.add_hline(y=0, line_dash="dash", line_color="gray", annotation_text="No Change")
        fig.update_yaxes(range=[-100, 100])  # Adjust range as needed for multi-day changes
        
        st.plotly_chart(fig)
        correlation = dataset[f'fear_greed_avg_{window}d'].corr(dataset[f'close_change_{window}d'])
        st.write(f":gray[This scatter plot compares the {window}-day average Fear & Greed Index with the {window}-day Bitcoin price change. Each dot represents a {window}-day period.]")
        st.write(f"**Correlation coefficient for {window}-day window**: {correlation:.4f}")
        st.write(f"**Interpretation:** A correlation of {correlation:.4f} suggests a {'weak' if abs(correlation) < 0.3 else 'moderate' if abs(correlation) < 0.5 else 'strong'} relationship between the {window}-day average Fear & Greed Index and {window}-day price changes.")

# Main code
dataset = getData()
addFeatures(dataset)

st.title("Fear & Greed Index vs. Bitcoin Price Change Analysis")
st.write("This dashboard explores the relationship between the Fear & Greed Index and Bitcoin's price changes over various time windows.")

# Date range selection
st.header("Date Range Selection")
date_range = st.date_input("Select Date Range", 
                           [dataset['timestamp'].min().date(), dataset['timestamp'].max().date()],
                           min_value=dataset['timestamp'].min().date(),
                           max_value=dataset['timestamp'].max().date())

if len(date_range) == 2:
    start_date, end_date = pd.to_datetime(date_range)
    dataset = dataset[(dataset['timestamp'] >= start_date) & (dataset['timestamp'] <= end_date)]

# Calculate multi-day window changes
window_sizes = [7, 30]
dataset = calculate_window_changes(dataset, window_sizes)

st.header("Multi-day Window Analysis")
st.write("This section analyzes the relationship between average Fear & Greed Index values and price changes over 7-day and 30-day windows.")

# Display multi-window scatter plots
multi_window_scatter_plot(dataset, window_sizes)

st.header("Conclusion")
st.write("Based on the analysis presented in this dashboard:")
for window in window_sizes:
    correlation = dataset[f'fear_greed_avg_{window}d'].corr(dataset[f'close_change_{window}d'])
    st.write(f"{window}-day window: Correlation coefficient of {correlation:.4f}")
    if abs(correlation) < 0.3:
        st.write(f"- There appears to be a weak relationship between the {window}-day average Fear & Greed Index and {window}-day price changes.")
    elif abs(correlation) < 0.5:
        st.write(f"- There appears to be a moderate relationship between the {window}-day average Fear & Greed Index and {window}-day price changes.")
    else:
        st.write(f"- There appears to be a strong relationship between the {window}-day average Fear & Greed Index and {window}-day price changes.")

st.write("These findings suggest that:")
st.write("1. Short-term (daily) fluctuations in the Fear & Greed Index may not be strongly predictive of price movements.")
st.write("2. Longer-term trends in market sentiment (as measured by the Fear & Greed Index) may have a more noticeable relationship with price changes.")
st.write("3. The strength of the relationship may vary depending on the time window considered.")
st.write("However, it's important to note that correlation does not imply causation, and other factors not considered in this analysis may also influence Bitcoin price movements.")

