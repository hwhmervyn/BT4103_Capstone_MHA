import streamlit as st
import pandas as pd

import sys, os
workingDirectory = os.getcwd()
costDirectory = os.path.join(workingDirectory, "cost_breakdown")

st.markdown("<h1 style='text-align: left; color: Black;'>Usage Tracking</h1>", unsafe_allow_html=True)
st.markdown('#')

file_path = os.path.join(costDirectory, 'API Cost.csv')
# Check if the file exists
if os.path.exists(file_path):
    # If the file exists, read it into a DataFrame
    df = pd.read_csv(file_path)
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

# st.dataframe(df_cost)
st.subheader('Time series chart of Cumulative Total Cost ($USD)')
st.line_chart(df_cost, use_container_width=True)
st.markdown('#')
st.subheader('Time series chart of Cumulative Total Input Tokens')
st.line_chart(df_input, use_container_width=True)
st.markdown('#')
st.subheader('Time series chart of Cumulative Total Output Tokens')
st.line_chart(df_output, use_container_width=True)

