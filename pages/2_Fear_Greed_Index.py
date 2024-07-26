import streamlit as st
from libraries.plots import *
from libraries.data import *
import pandas as pd
import plotly.express as px
import numpy as np

def process_data(dataset, window):
    if window == 1:
        dataset['close_change'] = dataset['close_change'].shift(-1)
        dataset['fear_greed_avg'] = dataset['fear_greed']
    else:
        dataset['close_change'] = dataset['close'].pct_change(periods=window).shift(window) * 100 #periods=window or periods=-window ???
        dataset['fear_greed_avg'] = dataset['fear_greed'].rolling(window=window).mean()
    
    dataset = dataset.dropna(subset=['close_change', 'fear_greed_avg'])
    return dataset

def display_correlation(dataset):
    correlation = dataset['fear_greed_avg'].corr(dataset['close_change'])
    st.write(f"**Pearson correlation coefficient**: `{correlation:.4f}`")
    st.write(":gray[A coefficient close to 1 or -1 indicates a strong correlation, while values close to 0 indicate a weak correlation.]")
    
def fear_greed_vs_close_change_scatter(dataset, window):
    color_scale = ['#FF4136', '#FF851B', '#FFDC00', '#2ECC40', '#0074D9']
    fig = px.scatter(dataset, x="fear_greed_avg", y="close_change", 
                     color="value_classification", 
                     color_discrete_map={
                         "Extreme Fear": color_scale[0],
                         "Fear": color_scale[1],
                         "Neutral": color_scale[2],
                         "Greed": color_scale[3],
                         "Extreme Greed": color_scale[4]
                     },
                     hover_data=["timestamp"],
                     labels={"fear_greed_avg": f"Average Fear & Greed Index ({window}-day)", 
                             "close_change": f"{window}-day Close Price Change (%)",
                             "value_classification": "Classification"},
                     title=f"Average Fear & Greed Index vs {window}-day Close Price Change")
    
    fig.add_hline(y=0, line_dash="dash", line_color="gray", annotation_text="No Change")
    fig.update_yaxes(range=[-max(abs(dataset['close_change'])), max(abs(dataset['close_change']))])
    fig.update_layout(legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))

    st.plotly_chart(fig, use_container_width=True)
    st.write(f":gray[This scatter plot compares the {window}-day average Fear & Greed Index with the {window}-day Bitcoin price change. Each dot represents a {window}-day period.]")

def fear_greed_box_plot(dataset, window):
    color_scale = ['#FF4136', '#FF851B', '#FFDC00', '#2ECC40', '#0074D9']
    fig = px.box(dataset, x="value_classification", y="close_change",
                 color="value_classification",
                 color_discrete_map={
                     "Extreme Fear": color_scale[0],
                     "Fear": color_scale[1],
                     "Neutral": color_scale[2],
                     "Greed": color_scale[3],
                     "Extreme Greed": color_scale[4]
                 },
                 labels={"value_classification": "Fear & Greed Classification", 
                         "close_change": f"{window}-day Close Price Change (%)"},
                 title=f"{window}-day Close Price Change Distribution by Fear & Greed Classification")
    fig.update_xaxes(categoryorder="array", 
                     categoryarray=["Extreme Fear", "Fear", "Neutral", "Greed", "Extreme Greed"])
    fig.update_layout(legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))

    st.plotly_chart(fig, use_container_width=True)
    st.write(f":gray[This box plot shows how Bitcoin's {window}-day price changes are distributed for different Fear & Greed Index categories. The boxes represent the middle 50% of price changes, with the line inside each box showing the median.]")

def rolling_correlation_plot(dataset, window):
    st.subheader(f"Rolling Correlation")
    rolling_window = st.slider("Select rolling correlation window (periods)", 3, 365, 60)
    
    dataset['rolling_corr'] = dataset['fear_greed_avg'].rolling(window=rolling_window).corr(dataset['close_change'])
    
    fig = px.line(dataset, x='timestamp', y='rolling_corr',
                  labels={'timestamp': 'Date', 'rolling_corr': 'Rolling Correlation'},
                  title=f'{rolling_window}-Period Rolling Correlation between Average Fear & Greed Index and {window}-day Close Price Change')
    
    fig.add_hline(y=0.3, line_dash="dash", line_color="red", annotation_text="Weak Positive Correlation")
    fig.add_hline(y=-0.3, line_dash="dash", line_color="red", annotation_text="Weak Negative Correlation")
    fig.update_yaxes(range=[-1, 1])
    fig.update_layout(legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))

    
    st.plotly_chart(fig, use_container_width=True)
    st.write(f":gray[This line graph shows how the relationship between the {window}-day average Fear & Greed Index and {window}-day price change varies over time. The line represents the strength of the relationship, calculated over {rolling_window}-period windows.]")

# Main code
dataset = getData()
addFeatures(dataset)

st.title("Fear & Greed Index vs. Bitcoin Price Change Analysis")
st.write("This dashboard explores the relationship between the Fear & Greed Index and Bitcoin's price changes over different time windows.")

# Time window selection
window = st.selectbox("Select time window", [1, 7, 30], format_func=lambda x: f"{x} day{'s' if x > 1 else ''}")

# Date range selection
st.header("Date Range Selection")
date_range = st.date_input("Select Date Range", 
                           [dataset['timestamp'].min().date(), dataset['timestamp'].max().date()],
                           min_value=dataset['timestamp'].min().date(),
                           max_value=dataset['timestamp'].max().date())

if len(date_range) == 2:
    start_date, end_date = pd.to_datetime(date_range)
    dataset = dataset[(dataset['timestamp'] >= start_date) & (dataset['timestamp'] <= end_date)]

# Process data based on selected window
dataset = process_data(dataset, window)

st.header("Correlation Analysis")
display_correlation(dataset)

# Display the plots
rolling_correlation_plot(dataset, window)
fear_greed_vs_close_change_scatter(dataset, window)
fear_greed_box_plot(dataset, window)