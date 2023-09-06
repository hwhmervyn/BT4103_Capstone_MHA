import streamlit as st
import pandas as pd
import numpy as np

# st.set_page_config(layout="wide")
st.title('BT4103 Capstone Project')

df = pd.read_excel('data/combined.xlsx', sheet_name='no duplicates')
df_no_abstract = df.drop('ABSTRACT', axis=1)

st.header('st.dataframe() with abstract')
st.dataframe(df, width=3000, height=1000)

st.header('st.dataframe() without abstract')
st.dataframe(df_no_abstract, width=3000, height=1000)

st.header('st.table() with abstract')
st.table(df)

st.header('st.table() without abstract')
st.table(df_no_abstract)