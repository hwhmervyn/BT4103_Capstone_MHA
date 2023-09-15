import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(layout="wide")
# st.title('Welcome to researchXpress')
st.markdown("<h1 style='text-align: center; color: Black;'>Welcome to<br>researchXpress</h1>", unsafe_allow_html=True)
st.markdown("<h4 style='text-align: center; color: Black;'>Your one-stop protal to synthesis research evidence in a few clicks</h3>", unsafe_allow_html=True)
st.markdown('#')
st.markdown('#')

st.markdown("<h4 style='text-align: center; color: Black;'>To get started, click on one of the options below</h3>", unsafe_allow_html=True)
col1, col2, col3, col4, col5, col6, col7 = st.columns(7)
with col4:
    st.button("Upload an excel summary & enter a prompt!")
    st.button("Upload a zip folder of articles & enter a prompt!")


# TESTING ST.DATAFRAME() & ST.TABLE()
# df = pd.read_excel('data/combined.xlsx', sheet_name='no duplicates')
# df_no_abstract = df.drop('ABSTRACT', axis=1)

# st.header('st.dataframe() with abstract')
# st.dataframe(df, width=3000, height=1000)

# st.header('st.dataframe() without abstract')
# st.dataframe(df_no_abstract, width=3000, height=1000)

# st.header('st.table() with abstract')
# st.table(df)

# st.header('st.table() without abstract')
# st.table(df_no_abstract)