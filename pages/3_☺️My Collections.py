import streamlit as st
from streamlit_extras.app_logo import add_logo
from zipfile import ZipFile
from concurrent.futures import as_completed
from shutil import rmtree
import glob
import re
import time
from os import listdir
from os.path import abspath
from os.path import isdir
from os.path import join

import sys, os
workingDirectory = os.getcwd()
chromaDirectory = os.path.join(workingDirectory, "ChromaDB")
dataDirectory = os.path.join(workingDirectory, "data")
if dataDirectory not in sys.path:
    sys.path.append(dataDirectory)
if workingDirectory not in sys.path:
    sys.path.append(workingDirectory)
if chromaDirectory not in sys.path:
    sys.path.append(chromaDirectory)

from ingestPdf import schedulePdfUpload
from chromaUtils import getListOfCollection, clearCollection, is_valid_name
import streamlit.components.v1 as components

def ChangeWidgetFontSize(wgt_txt, wch_font_size = '12px'):
    htmlstr = """<script>
    var elements = window.parent.document.querySelectorAll('*'), i;
    for (i = 0; i < elements.length; ++i) { 
        if (elements[i].innerText == |wgt_txt|) { 
            elements[i].style.fontSize='""" + wch_font_size + """';
            }
     } </script>  """

    htmlstr = htmlstr.replace('|wgt_txt|', "'" + wgt_txt + "'")
    components.html(f"{htmlstr}", height=0, width=0)

if 'tick_delete_function' not in st.session_state:
    st.session_state['tick_delete_function'] = False

def flip(session_state):
      st.session_state[session_state] = not st.session_state[session_state] 

def clearCollection_and_updateState(collection_name, confirm_button, feedback):
    clearCollection([collection_name])
    feedback.warning(f"collection {collection_name} has been deleted")
    confirm_button.button("Okay", key="finish_deleting", on_click=flip, args=('tick_delete_function',))
    
########################## PAGE LAYOUT ###################################################################################################################

st.set_page_config(layout="wide")
add_logo("images/htpd_text.png", height=100)

#Header
st.markdown("<h1 style='text-align: left; color: Black;'>My Collections</h1>", unsafe_allow_html=True)
st.markdown('#')

st.markdown("<h2 style='text-align: left; color: Black;'>Create Collection</h1>", unsafe_allow_html=True)
st.markdown('#') 

collection_name = st.text_input("Name of new Collection", placeholder='e.g. psychological-first-aid')
st.markdown('##')

uploaded_file = st.file_uploader("Upload your zip folder here", type=['zip'], help='Upload a zip folder containing only PDF research articles')
st.markdown('##')
col1, col2, col3 , col4, col5, col6, col7 = st.columns(7)
with col4:
    create = st.empty()
    create.button("Upload", key="create_but")
progress_placeholder = st.empty()

st.markdown('##')
show_delete_container = st.empty()
show_delete = show_delete_container.checkbox(":red[Delete a Collection]", key='tick_delete_function', disabled=st.session_state['create_but'])
if st.session_state['tick_delete_function']:
    ChangeWidgetFontSize("Delete a Collection", '1.8rem')
    delete_function_container = st.container()
    if st.session_state['tick_delete_function']: 
        with delete_function_container:
            collections_available = getListOfCollection()
            collection_to_delete = st.selectbox(
                'Select a Collection To Delete', collections_available,
                placeholder="Select Collection to Delete"
            )

            st.markdown('##')
            col1, col2, col3 , col4, col5, col6, col7 = st.columns(7)
            with col4:
                delete = st.button("Delete", key="delete_but", disabled=(collection_to_delete==None or st.session_state['create_but']))
            confirm_delete_container = st.container()
            if st.session_state['delete_but'] and collection_to_delete:
                with confirm_delete_container:
                    feedback = st.empty()
                    feedback.warning(f"WARNING! Are you sure you want to delete the collection: '{collection_to_delete}'?", icon= "🚨")
                    confirm_button = st.empty()
                    confirm_button.button("Yes I want to delete", type="primary",on_click=clearCollection_and_updateState, args=(collection_to_delete, confirm_button, feedback))

                    
else:
    ChangeWidgetFontSize("Delete a Collection", '1em')
########################## CREATE ###################################################################################################################

if st.session_state['create_but']:
    st.session_state['disabled'] = True
    start_time = time.time()
    if collection_name and not uploaded_file:
        progress_placeholder.error("Please upload a zip folder")
    elif not collection_name and uploaded_file:
        progress_placeholder.error("Please enter a Collection Name")
    elif not collection_name and not uploaded_file:
        progress_placeholder.error("Please enter a Collection Name and upload a zip folder")
    elif collection_name in getListOfCollection():
        progress_placeholder.error("Collection Name has already been taken, please choose something else")
    elif not is_valid_name(collection_name):
        naming_format = """
        Collection Name format MUST satisfy the following format:\n
        - The length of the name must be between 3 and 63 characters.\n
        - The name must start and end with a lowercase letter or a digit, and it can contain dots, dashes, and underscores in between.\n
        - The name must not contain two consecutive dots.\n
        - The name must not be a valid IP address."""
        progress_placeholder.error(naming_format)
    else:
        create.empty()
        with ZipFile(uploaded_file, 'r') as zip:
            extraction_path = os.path.join(workingDirectory, "data/")
            zip.extractall(extraction_path)
            foldername = zip.infolist()[0].filename
            foldername_match = re.search(r'^([^/]+)/', foldername) # Search for folder name in zip file
            if foldername_match:
                foldername = foldername_match.group(1)
            else:
                foldername = ""
    
        pdfList = glob.glob(os.path.join('data', foldername, '*.pdf'))
        issues, executor, futures = schedulePdfUpload(pdfList, collection_name)
        
        progressBar1 = progress_placeholder.progress(0, text="Uploading documents...")
        numDone, numFutures = 0, len(futures)
        for future in as_completed(futures):
            result = future.result()
            numDone += 1
            progress = float(numDone/numFutures)
            progressBar1.progress(progress,text="Uploading documents...")
        st.success(f'Successfully uploaded {collection_name}')
        
        # Remove all folders in 'data' folder
        for file in listdir(dataDirectory):
            full_path = join(abspath(dataDirectory), file)
            if isdir(full_path):
                rmtree(full_path)
            elif full_path.endswith('.pdf'):
                os.remove(full_path)  

        st.experimental_rerun()
    end_time = time.time()
    time_taken_seconds = end_time - start_time
    time_taken_minute_seconds =  time.strftime("%M:%S", time.gmtime(time_taken_seconds))
    print(f'Time taken in seconds is {time_taken_seconds} seconds')
    print(f'Time taken in minutes and seconds is {time_taken_minute_seconds}')

    st.session_state['disabled'] = False