import pandas as pd
import streamlit as st
from concurrent.futures import as_completed
from stqdm import stqdm
import glob
import streamlit as st
from streamlit_extras.app_logo import add_logo
from zipfile import ZipFile
import re
import time

import sys, os
workingDirectory = os.getcwd()
chromaDirectory = os.path.join(workingDirectory, "ChromaDB")
sys.path.append(chromaDirectory)

from ingestPdf import pdfUpload

st.set_page_config(layout="wide")
add_logo("images/htpd_text.png", height=100)

st.markdown("<h1 style='text-align: left; color: Black;'>PDF Analysis</h1>", unsafe_allow_html=True)
st.markdown('#')
st.header('PDF Analysis')

import asyncio

async def my_async_function():
    await asyncio.sleep(2)  # Asynchronously sleep for 2 seconds

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
            with ZipFile(uploaded_file, 'r') as zip:
                extraction_path = os.path.join(workingDirectory, "data/")
                zip.extractall(extraction_path)
                foldername_match = re.search(r'^([^/]+)/', zip.infolist()[0].filename) # Search for folder name in zip file
                foldername = foldername_match.group(1)
            
            pdfList = glob.glob(os.path.join('data', foldername, '*.pdf'))
            st.write(uploaded_file.name[:-4])
            (issues, executor, futures) = pdfUpload(pdfList)
            
            progessBar1 = st.progress(0, text="Uploading main pdf sections:")
            numDone, numFutures = 0, len(futures)
            PARTS_ALLOCATED_UPLOAD_MAIN = 0.25
            for future in stqdm(as_completed(futures)):
                result = future.result()
                numDone += 1
                progress = float(numDone/numFutures) * PARTS_ALLOCATED_UPLOAD_MAIN
                progessBar1.progress(progress,text="Uploading main pdf sections:") 
            
            # DUMMY FOR FILTERING
            PARTS_ALLOCATED_FILTER = 0.7
            for percent_complete in range(30,100):
                time.sleep(0.1)
                progessBar1.progress(float(percent_complete/100), text="Uploading main pdf sections:")
            st.session_state.pdf_filtered = True
            st.experimental_rerun()
            
if st.session_state.pdf_filtered:
    st.subheader("Here are the articles relevant to your prompt:")

    reupload_button = st.button('Reupload another prompt and zip file')
    if reupload_button:
        st.session_state.pdf_filtered = False
        st.experimental_rerun()