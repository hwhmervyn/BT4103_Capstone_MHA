import streamlit as st
from streamlit_extras.app_logo import add_logo
import time
import pandas as pd

import os
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

            print("done resetting and uploading pdfs to db")
            st.session_state.pdf_filtered = True
            st.experimental_rerun()

if st.session_state.pdf_filtered:
    new_input = st.text_input("Enter another research prompt to process the same files:", placeholder='Enter another research prompt to process the same files')
    prompt_reupload_button = st.button('Process files with new prompt')

    if prompt_reupload_button:
        if not new_input:
            st.error("Please enter a new research prompt")
        else:
            progress_text = "Article analysis in progress..."
            loading_bar = st.progress(0, text=progress_text)

            for percent_complete in range(100):
                time.sleep(0.1)
                loading_bar.progress(percent_complete, text=progress_text)

            print("done resetting and uploading pdfs to db")
            st.session_state.pdf_filtered = True
            st.experimental_rerun()

    st.subheader("Here are the articles relevant to your prompt:")

    # Display output (To be changed during integration)
    data = [['Article 1', 'Finding 1'],['Article 2', 'Finding 2']]
    df = pd.DataFrame(data, columns=['Title', 'Key Findings'])

    with ZipFile('output/filtered_pdfs.zip', 'w') as zip_object:
        for folder_name, sub_folders, file_names in os.walk('data/'):
            for filename in file_names:
                file_path = os.path.join(folder_name, filename)
                zip_object.write(file_path, os.path.basename(file_path))

    if os.path.exists('output/filtered_pdfs.zip'):
        print("Zip file created")
    else:
        print("Zip file not created")

    st.download_button(label="Download PDF files", data='output/filtered_pdfs.zip', file_name='filtered_pdfs.zip') 
    st.dataframe(df, width=3000, height=1000)

    st.markdown('##')
    st.subheader('Visualised Findings:')

    count_df = df['Title'].groupby(df['Key Findings']).count().reset_index()
    st.bar_chart(data=count_df, x='Key Findings', y='Title', color=None, width=0, height=0, use_container_width=True)
    
    col1, col2, col3 , col4, col5 = st.columns(5)
    pdf_reupload_button = st.button('Reupload another prompt and zip folder')
    if pdf_reupload_button:
        st.session_state.pdf_filtered = False
        st.experimental_rerun()