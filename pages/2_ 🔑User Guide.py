import streamlit as st
from streamlit_extras.switch_page_button import switch_page
from streamlit_extras.app_logo import add_logo
from PIL import Image
from streamlit_lottie import st_lottie 

import pandas as pd
import numpy as np
import time
import json

import base64

st.set_page_config(layout="wide")
add_logo("images/temp_logo.png", height=100)

#Incorporate bootstrap
st.markdown("""
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet"
	integrity="sha384-T3c6CoIi6uLrA9TneNEoa7RxnatzjcDSCmG1MXxSR1GAsXEV/Dwwykc2MPK8M2HN" crossorigin="anonymous">
""",unsafe_allow_html=True)

#Add the animation
path = "images/lightbulb.json"
with open(path,"r",encoding="utf-8") as file: 
    url = json.load(file) 

#Other CSS
st.markdown("""
<style>
            
.header {
    text-align: left;
    color: Black;
    font-weight:bold;
    
}

.research {
    color: purple;
    font-weight:bold;
     
}
            
.xpress {
    color: green;
    font-weight:bold;
}
            
.flame {
    font-style: normal;
}
            
.arm {
    font-style: normal;
}
            
.moon {
    font-style:normal;
}

.feature {
    font-weight:bold;
}          
            
</style>
""", unsafe_allow_html=True)

st.markdown("<h1 class = 'header'>User Guide</h1>", unsafe_allow_html=True)

#The Description Test
with st.container():
    col_1, col_2 = st.columns([3, 1])
    with col_1:
        st.markdown("<p style = 'font-style: italic; font-size: 20px;'>\
                Welcome to the user guide of <span class='research'>research</span><span class='xpress'>Xpress</span>,\
                a platform created to simplify research for researchers<span class = 'flame'>🔥🔥🔥</span></p>", 
                unsafe_allow_html=True)

        st.markdown("<p style = 'font-style: italic; font-size: 20px;'>The dashboard provides <span class='feature'>four features</span> to improve your research experience<span class = 'arm'>💪💪💪</span>: \
                     Excel Filtering, Collection Management, PDF Filtering, and PDF Analysis.</p>", unsafe_allow_html=True)

        st.markdown("<p style = 'font-style: italic; font-size: 20px;'>For additional information, please visit this  \
                    <a href= 'https://docs.google.com/document/d/1wXieeEDL4kXgPkc74QqiVeczD5VBau8Ww2-GQJjIZXQ/edit?usp=sharing' class='link-primary link-opacity-50-hover'>link</a>.</p>", unsafe_allow_html=True)
    with col_2:
    #Animation
        st_lottie(url, 
            height =200,
            loop=True, 
            quality='high',
            key='second'
            )
	
sections = [
    {"icon": "📗", "title": "Excel Filtering", "description": "***Filter an excel file of articles with a research prompt and view results***", "steps":["Navigate to '📗 **Excel Filtering**' using the sidebar", 
                                                                                                                                                  "Insert a **research prompt** and upload an **Excel file** containing a sheet of article title, abtracts, DOI and database",
                                                                                                                                                  "Click **Submit** and wait for the file to be processed",
                                                                                                                                                  "View filtered results and download the output"]},
     {"icon" : "☺️", "title": "My Collections", "description" : "***Create your own collection of pdfs with a few clicks***", "steps": ["Navigate to '☺️ **My Collections**' using the sidebar",
                                                                                                                                 "Gather all your PDF articles within a **folder** (Do not immediately compress all the PDF articles into a zip file)",
                                                                                                                                "Right-click on the folder and select **'Compress' or 'Zip'** to create a zip file",
                                                                                                                                "Name your collection and upload the zip file of PDF articles"]},
    {"icon": "📂", "title": "PDF Filtering", "description": "***Filter a folder of PDF articles with a yes/no research prompt and view results***", "steps":[ "Navigate to '📂 **PDF Filtering**' using the sidebar",
                                                                                                                                                "Select your **uploaded collection** as the input and insert a **research prompt**",
                                                                                                                                                "Click **Submit** and wait for the files to be processed",
                                                                                                                                                "View filtered results, extracted findings, and download the output"]},
    {"icon": "🔍", "title": "PDF Analysis", "description": "***Query PDF articles with a research prompt***", "steps":["Navigate to '🔍 **PDF Analysis**' using the sidebar", 
                                                                                                                                            "Select a **collection of articles** and input a **research prompt**",
                                                                                                                                            "Click **Submit** and wait for the article(s) to be analysed",
                                                                                                                                            "View the response and download the output"]},
]

# Display sections in a grid layout
#col1, col2, col3 = st.columns([1, 4, 1])
#with col2:
with st.container():
    for section in sections:
        st.subheader(f"**{section['icon']} {section['title']}**\n{section['description']}")
        num = 1
        for step in section['steps']:
            st.write(f"**{num}.** {step}")
            num += 1
        st.text("")

