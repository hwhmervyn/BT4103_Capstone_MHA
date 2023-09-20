import streamlit as st
from streamlit_extras.app_logo import add_logo
import time

import sys
import os
sys.path.append('ChromaDB/')
import ingestExcel
from concurrent.futures import as_completed
from stqdm import stqdm

st.sidebar.markdown("researchXpress")
add_logo("images/htpd_logo.jpeg", height=200)

st.markdown("<h1 style='text-align: left; color: Black;'>Excel Analysis</h1>", unsafe_allow_html=True)

st.markdown('#')

if 'filtered' not in st.session_state:
    st.session_state.filtered = False


if not st.session_state.filtered:

    input = st.text_input("Research Prompt", placeholder='Enter your research prompt')

    st.markdown('##')
    uploaded_file = st.file_uploader("Upload your Excel file here", type=['xlsx'], help='Upload an excel file that contains a list of research article titles and their abstracts')

    st.markdown('##')
    col1, col2, col3 , col4, col5, col6, col7 = st.columns(7)

    with col4:
        button = st.button('Submit')
    
    if button:
        if input and not uploaded_file:
            st.error("Please upload an excel file")
        elif not input and uploaded_file:
            st.error("Please enter a research prompt")
        elif not input or not uploaded_file:
            st.error("Please enter a research prompt and upload an excel file")
        else:
            progress_text = "Article filtering in progress..."
            loading_bar = st.progress(0, text=progress_text)

            for percent_complete in range(100):
                time.sleep(0.1)
                loading_bar.progress(percent_complete, text=progress_text)
            
            # executor, futures = ingestExcel.excelUpload(uploaded_file)
            # numDone, numFutures = 0, len(futures)
            # for future in stqdm(as_completed(futures)):
            #     result = future.result()
            #     numDone += 1
            #     loading_bar.progress((numDone/numFutures), text=progress_text)
                
            print("done resetting and uploading abstract and title to db")
            st.session_state.filtered = True
            st.write(st.session_state.filtered)



if st.session_state.filtered:

    st.markdown("<h1 style='text-align: left; color: Black;'>Excel Analysis Result page</h1>", unsafe_allow_html=True)
            