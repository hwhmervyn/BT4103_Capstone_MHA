import streamlit as st
from concurrent.futures import as_completed
import streamlit as st
from streamlit_extras.app_logo import add_logo
import time

import sys, os
workingDirectory = os.getcwd()
dataDirectory = os.path.join(workingDirectory, "data")
chromaDirectory = os.path.join(workingDirectory, "ChromaDB")
analysisDirectory = os.path.join(workingDirectory, "Analysis")
miscellaneousDirectory = os.path.join(workingDirectory, "Miscellaneous")


sys.path.append(chromaDirectory)
sys.path.append(analysisDirectory)
sys.path.append(miscellaneousDirectory)

import chromaUtils
from ingestPdf2 import copyCollection
from Individual_Analysis2 import ind_analysis_main, get_yes_pdf_filenames
from Aggregated_Analysis2 import agg_analysis_main
from User_Input_Cleaning import process_user_input

from os import listdir
from os.path import abspath
from os.path import isdir
from os.path import join
from shutil import rmtree
import asyncio

st.set_page_config(layout="wide")
add_logo("images/htpd_text.png", height=100)

st.markdown("<h1 style='text-align: left; color: Black;'>PDF Filtering</h1>", unsafe_allow_html=True)
st.markdown('#')

async def my_async_function():
    await asyncio.sleep(2)  # Asynchronously sleep for 2 seconds

if 'pdf_filtered' not in st.session_state:
    st.session_state.pdf_filtered = False
if 'collection' not in st.session_state:
    st.session_state.collection = None

#collection_name, file_upload, prompt
err_messages = {
    "000": "Please select an input collection to use, enter a research prompt and, enter a collection name(that hasn't been used yet) to store the filtered articles",
    "100": "Please enter a research prompt and a collection name(that hasn't been used yet) to store the filtered articles",
    "010": "Please select an input collection to use and and a collection name(that hasn't been used yet) to store the filtered articles",
    "001": "Please select an input collection to used andenter a research prompt",
    "011": "Please select an input collection to use",
    "101": "Please enter a research prompt",
    "110": "Please enter a collection name(that hasn't been used yet) to store the filtered articles",
}

if not st.session_state.pdf_filtered:
    # Remove all folders in 'data' folder
    for file in listdir(dataDirectory):
        full_path = join(abspath(dataDirectory), file)

    if isdir(full_path):
        rmtree(full_path)

    # Page layout
    input_collection_name = st.selectbox(
        'Input Collection', chromaUtils.getListOfCollection(), 
        placeholder="Select the Collection you would like to use"
    )

    prompt = st.text_input("Research Prompt", placeholder='Enter your research prompt')
    output_collection_name = st.text_input("Output Collection Name", placeholder='e.g. pfa-and-culture', help="It is recommended to pick a name that is similar to your prompt")

    st.markdown('##')
    col1, col2, col3 , col4, col5, col6, col7 = st.columns(7)

    with col4:
        button = st.button('Submit')
        
    if button:
        err_code = str(int(bool(input_collection_name)))+\
                                    str(int(bool(prompt)))+\
                                                str(int(bool(output_collection_name and output_collection_name not in chromaUtils.getListOfCollection())))

        if not err_messages.get(err_code):
            relevant_output = process_user_input(prompt)
            if relevant_output == 'irrelevant':
                st.error('Irrelevant Output! Please input a relevant prompt')
            else:
                PARTS_ALLOCATED_IND_ANALYSIS = 0.5
                PARTS_ALLOCATED_AGG_ANALYSIS = 0.3
                PARTS_ALLOCATED_COPY = 0.2
                progressBar1 = st.progress(0, text="Processing documents...")
                time.sleep(2)
                ind_findings, findings_visual = ind_analysis_main(prompt, input_collection_name, progressBar1)
                ind_findings.to_excel("output/pdf_analysis_results.xlsx", index=False)
                time.sleep(2)

                rel_ind_findings  = ind_findings[ind_findings["Answer"].str.lower() == "yes"]
                agg_findings = agg_analysis_main(rel_ind_findings, progressBar1)
                
                rel_file_names = rel_ind_findings['Article Name'].values.tolist()
                executor, futures = copyCollection(input_collection_name, output_collection_name, rel_file_names)
                numDone, numFutures = 0, len(futures)
                for future in as_completed(futures):
                    result = future.result()
                    numDone += 1
                    progress = float(numDone/numFutures)*PARTS_ALLOCATED_COPY+(PARTS_ALLOCATED_IND_ANALYSIS+PARTS_ALLOCATED_AGG_ANALYSIS)
                    progressBar1.progress(progress,text="Uploading documents...")
                    
                st.session_state.pdf_filtered = prompt
                st.session_state.pdf_ind_fig1 = findings_visual
                st.session_state.pdf_ind_fig2 = ind_findings
                st.session_state.pdf_agg_fig = agg_findings
                st.experimental_rerun()
        else:
           st.error(err_messages[err_code]) 
            
if st.session_state.pdf_filtered:
    st.subheader("Prompt")
    st.markdown(st.session_state.pdf_filtered)

    st.subheader("Results")

    # Summary visualisations (in the form of cards)
    num_relevant_articles = len(get_yes_pdf_filenames(st.session_state.pdf_ind_fig2))
    num_articles = st.session_state.pdf_ind_fig2.shape[0]

    st.markdown("""
    <style>
    div[data-testid="metric-container"] {
    background-color: rgba(28, 131, 225, 0.1);
    border: 1px solid rgba(28, 131, 225, 0.1);
    padding: 5% 5% 5% 10%;
    border-radius: 5px;
    color: rgb(30, 103, 119);
    overflow-wrap: break-word;
    }

    div[data-testid="metric-container"] > label[data-testid="stMetricLabel"] > div {
    overflow-wrap: break-word;
    white-space: break-spaces;
    color: red;
    }
                
    div[data-testid="metric-container"] > label[data-testid="stMetricLabel"] > div p {
    font-size: 150% !important;
    }
    </style>
    """
    , unsafe_allow_html=True)

    col1, col2, col3, col4, col5 = st.columns(5)
    with col2:
        st.metric("Articles Analysed", num_articles)
    
    with col4:
        st.metric("Relevant Articles", num_relevant_articles)

    st.text("")
    st.text("")
    st.text("")

    # Result Table
    with open("output/pdf_analysis_results.xlsx", 'rb') as my_file:
        st.download_button(label = 'Download Excel', data = my_file, file_name='pdf_analysis_results.xlsx', mime = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    st.plotly_chart(st.session_state.pdf_ind_fig1, use_container_width=True)

    # Key Themes
    st.subheader("Key Themes")
    st.markdown(st.session_state.pdf_agg_fig)

    reupload_button = st.button('Reupload another prompt and zip file')
    if reupload_button:
        st.session_state.pdf_filtered = False
        st.experimental_rerun()