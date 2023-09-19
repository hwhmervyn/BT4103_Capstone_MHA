import streamlit as st
import time

st.markdown("<h1 style='text-align: left; color: Black;'>Excel Analysis</h1>", unsafe_allow_html=True)

st.markdown('#')
input = st.text_input("Enter your research prompt")

st.markdown('##')
uploaded_file = st.file_uploader("Upload your Excel file here", type=['xlsx'], help='Upload an excel file that contains a list of research article titles and their abstracts')

st.markdown('##')
col1, col2, col3 , col4, col5, col6, col7 = st.columns(7)

with col7:
    button = st.button('Submit')

if button:
    if len(input) == 0 or uploaded_file == None:
        st.error("Please insert a research prompt and upload an excel file")
    else:
        progress_text = "Article filtering in progress..."
        loading_bar = st.progress(0, text=progress_text)

        for percent_complete in range(100):
            time.sleep(0.1)
            loading_bar.progress(percent_complete + 5, text=progress_text)