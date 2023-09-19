import pandas as pd
import streamlit as st
import sys
import os
print(os.path)
sys.path.append('ChromaDB/')
import ingestExcel
from concurrent.futures import as_completed
from time import sleep
from stqdm import stqdm
import asyncio

if "disabled" not in st.session_state:
    st.session_state["disabled"] = False

st.header('Excel Analysis')

prompt = st.text_input(
    label='Research_Prompt',
    value="",
    type="default",
    placeholder='enter research prompt',
    label_visibility="visible",
    disabled=st.session_state['disabled']
    )

startNewSheet = st.checkbox(
    'Upload a new Excel sheet',
    value=False,
    label_visibility="visible",
    disabled=st.session_state['disabled']
    )

excelFile = None

if startNewSheet:
    excelFile = st.file_uploader(
        label='excel_uploader',
        type=['xlsx'],
        accept_multiple_files=False,
        label_visibility='collapsed'
    )

if (startNewSheet and excelFile) and prompt:
    
    executor, futures = ingestExcel.excelUpload(excelFile)
    
    progessBar = st.progress(0, text="done uploading:")
    
    numDone, numFutures = 0, len(futures)
    for future in stqdm(as_completed(futures)):
        result = future.result()
        numDone += 1
        progessBar.progress((numDone/numFutures))
        
    print("done resetting and uploading abstract and title to db")
    
elif (startNewSheet == None) and prompt:
    pass