import streamlit as st
from streamlit_extras.app_logo import add_logo
import time

from zipfile import ZipFile

st.set_page_config(layout="wide")
add_logo("images/htpd_text.png", height=100)

st.markdown("<h1 style='text-align: left; color: Black;'>PDF Analysis</h1>", unsafe_allow_html=True)
st.markdown('#')

if 'pdf_filtered' not in st.session_state:
    st.session_state.pdf_filtered = False

if not st.session_state.pdf_filtered:
    input = st.text_input("Research Prompt", placeholder='Enter your research prompt')

    st.markdown('##')
    uploaded_file = st.file_uploader("Upload your zip folder here", type=['zip'], help='Upload a zip folder containing only PDF research articles')

    st.markdown('##')
    col1, col2, col3 , col4, col5, col6, col7 = st.columns(7)

    with col4:
        button = st.button('Submit')
        
    if button:
        if input and not uploaded_file:
            st.error("Please upload a zip folder")
        elif not input and uploaded_file:
            st.error("Please enter a research prompt")
        elif not input or not uploaded_file:
            st.error("Please enter a research prompt and upload a zip folder")
        else:
            progress_text = "Article analysis in progress..."
            loading_bar = st.progress(0, text=progress_text)

            with ZipFile(uploaded_file, 'r') as zip:
                extraction_path = "data/"
                zip.extractall(extraction_path)

            for percent_complete in range(100):
                time.sleep(0.1)
                loading_bar.progress(percent_complete, text=progress_text)

            st.session_state.pdf_filtered = True

if st.session_state.pdf_filtered:
    st.subheader("Here are the articles relevant to your prompt:")