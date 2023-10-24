import streamlit as st
from streamlit_extras.switch_page_button import switch_page
from streamlit_extras.app_logo import add_logo
from PIL import Image

import pandas as pd
import numpy as np
import time

import base64

st.set_page_config(layout="wide")
add_logo("images/htpd_text.png", height=100)

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

set_background('images/bg2.jpg')
########################## END BACKGROUND IMAGE ##########################

st.markdown("<h1 style='text-align: left; color: Black;'>User Guide</h1>", unsafe_allow_html=True)
st.write("")
st.write("")
st.write("")

sections = [
    {"icon": "📗", "title": "Excel Filtering", "description": "Filter an excel file of articles with a research prompt and view results", "steps":["Navigate to '📗 Excel Filtering' using the sidebar", 
                                                                                                                                                  "Insert a research prompt and upload an Excel file containing a sheet of article title, abtracts, DOI and database",
                                                                                                                                                  "Click Submit and wait for the file to be processed",
                                                                                                                                                  "View filtered results and download the output"]},
    {"icon": "📂", "title": "PDF Filtering", "description": "Filter a folder of PDF articles with a research prompt and view results", "steps":["Navigate to '☺️ My Collections' using the sidebar", 
                                                                                                                                                "Gather all your PDF articles within a **folder** (Do not immediately compress all the PDF articles into a zip file)",
                                                                                                                                                "Right-click on the folder and select 'Compress' or 'Zip' to create a zip file",
                                                                                                                                                "Name your collection and upload the zip file of PDF articles",
                                                                                                                                                "Navigate to '📂 PDF Filtering' using the sidebar",
                                                                                                                                                "Select your uploaded collection as the input and insert a research prompt",
                                                                                                                                                "Click Submit and wait for the files to be processed"
                                                                                                                                                "View filtered results, extracted findings, and download the output"]},
    {"icon": "⚖️", "title": "Support Analysis", "description": "Query PDF articles with a research hypothesis and view article support", "steps":["Navigate to '⚖️ Support Analysis' using the sidebar", 
                                                                                                                                            "Select a collection of articles to analyse and input a research hypothesis",
                                                                                                                                            "Click Submit and wait for the articles to be analysed",
                                                                                                                                            "View the article response distribution and given evidence"]},
]

# Display sections in a grid layout
#col1, col2, col3 = st.columns([1, 4, 1])
#with col2:
for section in sections:
    st.subheader(f"**{section['icon']} {section['title']}**\n{section['description']}")
    num = 1
    for step in section['steps']:
        st.write(f"**{num}.** {step}")
        num += 1
    st.text("")

st.text("")
st.text("")
st.text("")
st.write("For more details, refer to our full documentation here.")
