import streamlit as st
from streamlit_extras.switch_page_button import switch_page
from streamlit_extras.app_logo import add_logo
from PIL import Image

import pandas as pd
import numpy as np
import time

import base64

st.set_page_config(layout="wide")


########################## BACKGROUND IMAGE ##########################
def get_base64(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

def set_background(png_file):
    bin_str = get_base64(png_file)
    page_bg_img = '''
    <style>
    .stApp {
    background-image: url("data:image/png;base64,%s");
    background-size: cover;
    }
    </style>
    ''' % bin_str
    st.markdown(page_bg_img, unsafe_allow_html=True)

set_background('images/bg.jpg')
########################## END BACKGROUND IMAGE ##########################


########################## CSS ##########################
st.markdown("""
<style>
.research {
    font-size: 100px;
    font-weight: bold;
    text-align: center;
    color: blue;
    display:inline;
}
            
.xpress {
    font-size: 100px;
    font-weight: bold;
    text-align: center;
    color: green;   
    display:inline;
}
</style>
""", unsafe_allow_html=True)
########################## END CSS ##########################


########################## PAGE CONTENT ##########################
st.markdown("<h1 style='text-align: center; color: Black;'>Welcome to <br> <p class='research'>research<p class='xpress'>Xpress </p></h1>", unsafe_allow_html=True)
st.markdown("<h4 style='text-align: center; color: Black;'>Your one-stop protal to synthesis research evidence in a few clicks</h3>", unsafe_allow_html=True)
st.markdown('#')

st.markdown("<h4 style='text-align: center; color: Black;'>To get started, click on one of the options below</h3>", unsafe_allow_html=True)
col1, col2, col3, col4, col5, col6, col7 = st.columns(7)
with col4:
    excel_page = st.button(":green_book: Upload an excel summary & enter a prompt!")
    if excel_page:
        switch_page("excel analysis")
    pdf_page = st.button(":open_file_folder: Upload a zip folder of articles & enter a prompt!")
    if pdf_page:
        switch_page("pdf analysis")

st.sidebar.markdown("researchXpress")
add_logo("images/htpd_logo.jpeg", height=200)

########################## END PAGE CONTENT ##########################

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