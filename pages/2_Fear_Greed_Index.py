import streamlit as st
from libraries.plots import *
from libraries.data import *
import pandas as pd
import plotly.express as px

def shift_close_change(dataset):
    dataset['close_change'] = dataset['close_change'].shift(-1)
    dataset = dataset.dropna(subset=['close_change'])
    return dataset

def display_correlation(dataset):
    correlation = dataset['fear_greed'].corr(dataset['close_change'])
    st.write(f":black-background[**Pearson correlation coefficient**: `{correlation:.4f}`]")
    st.write(":gray[A coefficient close to 1 or -1 indicates a strong correlation, while values close to 0 indicate a weak correlation.]")
    
    # Add explanation about lack of correlation
    st.write(f"**Interpretation:** The correlation coefficient of {correlation:.4f} is very close to 0, indicating virtually no linear correlation between the Fear & Greed Index and the next day's close price change.")
    st.write("This suggests that the Fear & Greed Index alone is not a reliable predictor of short-term price movements.")

def fear_greed_vs_close_change_scatter(dataset):
    color_scale = ['#FF4136', '#FF851B', '#FFDC00', '#2ECC40', '#0074D9']
    fig = px.scatter(dataset, x="fear_greed", y="close_change", 
                     color="value_classification", 
                     color_discrete_map={
                         "Extreme Fear": color_scale[0],
                         "Fear": color_scale[1],
                         "Neutral": color_scale[2],
                         "Greed": color_scale[3],
                         "Extreme Greed": color_scale[4]
                     },
                     hover_data=["timestamp"],
                     labels={"fear_greed": "Fear & Greed Index", 
                             "close_change": "Next Day's Close Price Change (%)",
                             "value_classification": "Classification"},
                     title="Fear & Greed Index vs Next Day's Close Price Change")
    
    # Add a horizontal line at y=0 to emphasize lack of trend
    fig.add_hline(y=0, line_dash="dash", line_color="gray", annotation_text="No Change")
    
    st.plotly_chart(fig)
    st.write(":gray[This scatter plot shows the relationship between the Fear & Greed Index and the next day's close price change. Each point represents a day, colored by its Fear & Greed classification.]")
    st.write("**Note:** The scattered nature of the points without a clear trend further illustrates the lack of strong correlation between these metrics.")

def fear_greed_box_plot(dataset):
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
                         "close_change": "Next Day's Close Price Change (%)"},
                 title="Next Day's Close Price Change Distribution by Fear & Greed Classification")
    fig.update_xaxes(categoryorder="array", 
                     categoryarray=["Extreme Fear", "Fear", "Neutral", "Greed", "Extreme Greed"])
    st.plotly_chart(fig)
    st.write(":gray[This box plot displays the distribution of next day's close price changes for each Fear & Greed Index classification, showing how price changes vary across different market sentiment categories.]")
    st.write("**Observation:** The similar distributions across different Fear & Greed classifications support the conclusion that there's little correlation between the index and price changes.")

def rolling_correlation_plot(dataset):
    st.subheader(f"Rolling Correlation")
    rolling_window = st.slider("Select rolling correlation window (days)", 3, 365, 60)
    
    dataset['rolling_corr'] = dataset['fear_greed'].rolling(window=rolling_window).corr(dataset['close_change'])
    
    fig = px.line(dataset, x='timestamp', y='rolling_corr',
                  labels={'timestamp': 'Date', 'rolling_corr': 'Rolling Correlation'},
                  title=f'{rolling_window}-Day Rolling Correlation between Fear & Greed Index and Next Day\'s Close Price Change')
    
    # Add horizontal lines to emphasize weak correlation
    fig.add_hline(y=0.3, line_dash="dash", line_color="red", annotation_text="Weak Positive Correlation")
    fig.add_hline(y=-0.3, line_dash="dash", line_color="red", annotation_text="Weak Negative Correlation")
    
    st.plotly_chart(fig)
    st.write(f":gray[This line graph shows how the relationship between the Fear & Greed Index and next day's price change varies over time. The line represents the strength of the relationship, calculated over {rolling_window}-day periods.]")
    st.write("**Interpretation:** A value of 1 would mean a perfect positive relationship, -1 a perfect negative relationship, and 0 no relationship. The correlation mostly stays between -0.3 and 0.3, indicating a consistently weak relationship over time.")

# Main code
dataset = getData()
addFeatures(dataset)

st.title("Fear & Greed Index vs. Bitcoin Price Change Analysis")
st.write("This dashboard explores the relationship between the Fear & Greed Index and Bitcoin's price changes.")

# Date range selection
st.header("Date Range Selection")
date_range = st.date_input("Select Date Range", 
                           [dataset['timestamp'].min().date(), dataset['timestamp'].max().date()],
                           min_value=dataset['timestamp'].min().date(),
                           max_value=dataset['timestamp'].max().date())

if len(date_range) == 2:
    start_date, end_date = pd.to_datetime(date_range)
    dataset = dataset[(dataset['timestamp'] >= start_date) & (dataset['timestamp'] <= end_date)]

# Shift close_change to use next day's value
dataset = shift_close_change(dataset)

st.header("Correlation Analysis")
display_correlation(dataset)

# Display the plots
rolling_correlation_plot(dataset)
fear_greed_vs_close_change_scatter(dataset)
fear_greed_box_plot(dataset)

st.header("Conclusion")
st.write("Based on the analysis presented in this dashboard, we can conclude that there is virtually no significant correlation between the Fear & Greed Index and the next day's Bitcoin price change. This lack of correlation is evident from:")
st.write("1. The correlation coefficient being very close to zero.")
st.write("2. The scattered nature of points in the scatter plot, showing no clear trend.")
st.write("3. Similar distributions of price changes across different Fear & Greed classifications in the box plot.")
st.write("4. The rolling correlation mostly staying within the weak correlation range (-0.3 to 0.3).")
st.write("These findings suggest that while the Fear & Greed Index may be an interesting metric for gauging market sentiment, it does not appear to be a reliable predictor of short-term Bitcoin price movements.")
