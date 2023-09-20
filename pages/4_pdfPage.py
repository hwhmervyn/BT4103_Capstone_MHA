import pandas as pd
import streamlit as st
from concurrent.futures import as_completed
from time import sleep
from stqdm import stqdm
import asyncio

import sys, os
# For streamlit the parent directory will the folder in which your root page is at. And this directory will also 
# be your default working directory
workingDirectory = os.getcwd()
print(workingDirectory)
chromaDirectory = os.path.join(workingDirectory, "ChromaDB")
sys.path.append(chromaDirectory)

from ingestPdf import pdfUpload

st.header('PDF Analysis')

prompt = st.text_input(
    label='Research_Prompt',
    value="",
    type="default",
    placeholder='enter research prompt',
    label_visibility="visible",
    )

startNewSheet = st.checkbox(
    'Upload new PDFs',
    value=False,
    label_visibility="visible",
    )

pdfList = None

if startNewSheet:
    pdfList = st.file_uploader(
        label='pdf_uploader',
        type=['pdf'],
        accept_multiple_files=True,
        label_visibility='collapsed'
    )

if (startNewSheet and pdfList) and prompt:
    (issues, executor, futures) = pdfUpload(pdfList)
    
    #Keep this here to help with debugging
    st.write( f"Found {len(issues)} pdfs with issues, these files will be excluded, as we try to improve pdf-processing")
    st.write(issues)
    
    progessBar = st.progress(0, text="done uploading:")
    
    numDone, numFutures = 0, len(futures)
    for future in stqdm(as_completed(futures)):
        result = future.result()
        numDone += 1
        progessBar.progress((numDone/numFutures))
        
    print("done resetting and uploading pdfs db")
    
elif (startNewSheet == None) and prompt:
    pass