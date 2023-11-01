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

from Chroma_DB.ingestPdf import schedulePdfUpload
from Chroma_DB.chromaUtils import getListOfCollection, clearCollection, is_valid_name
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
    feedback.warning(f"Collection {collection_name} has been deleted")
    confirm_button.button("Okay", key="finish_deleting", on_click=flip, args=('tick_delete_function',))
    
########################## PAGE LAYOUT ###################################################################################################################

st.set_page_config(layout="wide")
add_logo("images/temp_logo.png", height=100)

# Header
st.markdown("<h1 style='text-align: left; color: Black;'>My Collections</h1>", unsafe_allow_html=True)
st.markdown('#')

st.subheader("Create Collection")
st.markdown('#') 
# End Header

# Create text input field for naming collection
collection_name = st.text_input("Name of new Collection", placeholder='e.g. psychological-first-aid')
st.markdown('##')

# Create file upload field
uploaded_file = st.file_uploader("Upload your zip folder here", type=['zip'], help='Upload a zip folder containing only PDF research articles')
st.markdown('##')
#create an upload button in the middle
col1, col2, col3 , col4, col5, col6, col7 = st.columns(7)
with col4:
    create = st.empty() #create a placeholder for upload button
    create.button("Upload", key="create_but")
progress_placeholder = st.empty()

# Delete Collection Section
st.markdown('##')
show_delete_container = st.empty()
show_delete = show_delete_container.checkbox(":red[Delete a Collection]", key='tick_delete_function', disabled=st.session_state['create_but'])#delete function will be disabled if create collection is runnning
if st.session_state['tick_delete_function']: 
    ChangeWidgetFontSize("Delete a Collection", '1.8rem')# increase the font size of the Delete header when the delete segment is revealed
    delete_function_container = st.container()
    # propagate the delete segement, thereby revealing the delete segment
    with delete_function_container:
        collections_available = getListOfCollection()
        collection_to_delete = st.selectbox(
            'Select a Collection To Delete', collections_available,
            placeholder="Select Collection to Delete"
        )

        st.markdown('##')
        # create and position a delete button in the middle
        col1, col2, col3 , col4, col5, col6, col7 = st.columns(7)
        with col4:
            delete = st.button("Delete", key="delete_but", disabled=(collection_to_delete==None or st.session_state['create_but']))# delete function will be disabled if create collection is runnning
        confirm_delete_container = st.container()
        if st.session_state['delete_but'] and collection_to_delete: # if user clicks delete and has provided a collection name to delete through the drop down bar, reveal a warning
            with confirm_delete_container:
                feedback = st.empty()
                feedback.warning(f"WARNING! Are you sure you want to delete the collection: '{collection_to_delete}'?", icon= "🚨")
                confirm_button = st.empty() # create a confirm button
                confirm_button.button("Yes I want to delete", type="primary",on_click=clearCollection_and_updateState, args=(collection_to_delete, confirm_button, feedback)) # if user clicks, confirming to delete, a callback will be run to delete the collection, before the page is refreshed
                    
else: 
    # if user unticks the delete function, then do not propagate the delete segment and shrink the font of the delete label
    ChangeWidgetFontSize("Delete a Collection", '1em')
########################## CREATE ###################################################################################################################################################################################################################################################################################
# Create Collection functions has to be run after the creating of delete segments, as we want to make sure the disabled state of the delete segments are updated properly when create collection is running.

if st.session_state['create_but']: # if user clicks on the upload button
    start_time = time.time()
    # validate user inputs, and throw error if there is an issue
    if collection_name and not uploaded_file:
        progress_placeholder.error("Please upload a zip folder")
    elif not collection_name and uploaded_file:
        progress_placeholder.error("Please enter a Collection Name")
    elif not collection_name and not uploaded_file:
        progress_placeholder.error("Please enter a Collection Name and upload a zip folder")
    elif collection_name in getListOfCollection(): # checks to make sure collection name has not been taken
        progress_placeholder.error("Collection Name has already been taken, please choose something else")
    elif not is_valid_name(collection_name): # check to make sure collection name follows the requirements set by Chromadb
        naming_format = """
        Collection Name format MUST satisfy the following format:\n
        - The length of the name must be between 3 and 63 characters.\n
        - The name must start and end with a lowercase letter or a digit, and it can contain dots, dashes, and underscores in between.\n
        - The name must not contain two consecutive dots.\n
        - The name must not be a valid IP address."""
        progress_placeholder.error(naming_format)
    else: # User inputs passed the validation checks, proceed with the uploading of the pdf files and the creation of the collection
        create.empty() # delete the create button when running the upload, as it can look rather distracting to a user while waiting for the progress bar to run finish
        with ZipFile(uploaded_file, 'r') as zip: #generate the list of pdf file paths
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
        # schedule futures to process and upload the pdfs. This is to avoid passing the progress bar to other scripts that are not streamlit pages as:
        # (1) it is hard to track the state across different scripts
        # (2) hard for internal testing
        
        progressBar1 = progress_placeholder.progress(0, text="Uploading documents...")
        numDone, numFutures = 0, len(futures)
        for future in as_completed(futures):
            result = future.result()
            numDone += 1
            progress = float(numDone/numFutures)
            progressBar1.progress(progress,text="Uploading documents...")
        end_time = time.time()
        time_taken_seconds = end_time - start_time
        time_taken_hours_minute_seconds =  time.strftime("%H:%M:%S", time.gmtime(time_taken_seconds))
        print(f'Time taken in seconds is {time_taken_seconds} seconds')
        print(f'Time taken in hours minutes and seconds is {time_taken_hours_minute_seconds}')
        st.success(f'Successful! Time taken: {time_taken_hours_minute_seconds}')
        
        # Remove all folders in 'data' folder after uploading is done, to avoid them from getting mixed up with subsequent pdf uploads.
        for file in listdir(dataDirectory):
            full_path = join(abspath(dataDirectory), file)
            if isdir(full_path):
                rmtree(full_path)
            elif full_path.lower().endswith('.pdf'):
                os.remove(full_path)  

        st.experimental_rerun()