import streamlit as st
from streamlit_extras.app_logo import add_logo
import pandas as pd

import sys, os
workingDirectory = os.getcwd()
costDirectory = os.path.join(workingDirectory, "cost_breakdown")

st.set_page_config(layout="wide")
add_logo("images/temp_logo.png", height=100)

st.markdown("<h1 style='text-align: left; color: Black;'>Usage Tracking</h1>", unsafe_allow_html=True)
st.markdown('#')

file_path = os.path.join(costDirectory, 'API Cost.xlsx')
# Check if the file exists
if os.path.exists(file_path):
    # If the file exists, read it into a DataFrame
    df = pd.read_excel(file_path, sheet_name='Sheet1')
else:
    # If the file doesn't exist, create an empty DataFrame
    columns = ['Date', 'Processing Stage', 'Query', 'Total Input Tokens', 'Total Output Tokens', 'Total Cost']
    df = pd.DataFrame(columns=columns)
df['Date'] = pd.to_datetime(df['Date'])
# df['Date'] = df['Date'].dt.date

# Group data by Date and Category and calculate total cost
grouped_data_cost = df.groupby(['Date', 'Processing Stage'])['Total Cost'].sum().reset_index()
grouped_data_input = df.groupby(['Date', 'Processing Stage'])['Total Input Tokens'].sum().reset_index()
grouped_data_output = df.groupby(['Date', 'Processing Stage'])['Total Output Tokens'].sum().reset_index()

# Pivot the data to create a new DataFrame with categories as columns
df_cost = pd.pivot_table(grouped_data_cost, values='Total Cost', index='Date', columns='Processing Stage', fill_value=0)
df_cost['All'] = df_cost.sum(axis=1)
df_cost = df_cost.cumsum()

df_input = pd.pivot_table(grouped_data_input, values='Total Input Tokens', index='Date', columns='Processing Stage', fill_value=0)
df_input['All'] = df_input.sum(axis=1)
df_input = df_input.cumsum()

df_output = pd.pivot_table(grouped_data_output, values='Total Output Tokens', index='Date', columns='Processing Stage', fill_value=0)
df_output['All'] = df_output.sum(axis=1)
df_output = df_output.cumsum()

# Style for metric card visualisationss
st.markdown("""
<style>
div[data-testid="metric-container"] {
background-color: rgba(28, 131, 225, 0.1);
border: 1px solid rgba(28, 131, 225, 0.1);
padding: 5% 5% 5% 10%;
border-radius: 5px;
color: rgb(30, 103, 119);
overflow-wrap: break-word;
}

div[data-testid="metric-container"] > label[data-testid="stMetricLabel"] > div {
overflow-wrap: break-word;
white-space: break-spaces;
color: red;
}
                
div[data-testid="metric-container"] > label[data-testid="stMetricLabel"] > div p {
font-size: 150% !important;
}
</style>
"""
, unsafe_allow_html=True)

# Display aggregate statistics as metric cards
col1, col2, col3, col4, col5 = st.columns(5)
with col2:
    st.metric("Total Cost ($USD)", round(df['Total Cost'].sum(), 4))

with col3:
    st.metric("Total Input Tokens", df['Total Input Tokens'].sum())
    
with col4:
    st.metric("Total Output Tokens", df['Total Output Tokens'].sum())

st.text("")
st.text("")
st.text("")

# Display usage charts
# st.dataframe(df_cost)
st.subheader('Time series chart of Cumulative Total Cost ($USD)')
st.line_chart(df_cost, use_container_width=True)
st.markdown('#')
st.subheader('Time series chart of Cumulative Total Input Tokens')
st.line_chart(df_input, use_container_width=True)
st.markdown('#')
st.subheader('Time series chart of Cumulative Total Output Tokens')
st.line_chart(df_output, use_container_width=True)
