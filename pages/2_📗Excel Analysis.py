import streamlit as st
from streamlit_extras.app_logo import add_logo
from concurrent.futures import as_completed
import pandas as pd

from cost_breakdown.update_cost import update_usage_logs
import sys,os
sys.path.append('ChromaDB/')
from filterExcel import filterExcel, getOutputDF

st.set_page_config(layout="wide")
add_logo("images/htpd_text.png", height=100)

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
            _, futures = filterExcel(uploaded_file,  input)
            issues, results, numDone, numFutures, total_input_tokens, total_output_tokens, total_cost = [],[], 0, len(futures), 0, 0, 0
            progessBar = st.progress(0, text="Article filtering in progress...")
            for future in as_completed(futures):
                row = future.result()
                total_input_tokens += row[5]
                total_output_tokens += row[6]
                total_cost += row[7]
                results.append(row[0:5])
                numDone += 1
                progessBar.progress(numDone/numFutures)
            
            update_usage_logs("Excel Filtering", input, total_input_tokens,total_output_tokens,total_cost)
            dfOut = pd.DataFrame(results, columns = ["DOI","TITLE","ABSTRACT","llmOutput", "jsonOutput"])
            dfOut = getOutputDF(dfOut)
            dfOut.to_excel("output/excel_result.xlsx", index=False)

            st.session_state.filtered = input
            st.experimental_rerun()

else:
    st.subheader("Prompt")
    st.text(st.session_state.filtered)

    st.subheader("Results")

    # Display output (To be changed during integration)
    df = pd.read_excel("output/excel_result.xlsx")
    # st.download_button(label="Download Excel file", data="output/test_output_pfa.xlsx", file_name='results.xlsx') 

    with open("output/excel_result.xlsx", 'rb') as my_file:
        st.download_button(label = 'Download', data = my_file, file_name='results.xlsx', mime = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet') 
        st.dataframe(df, width=3000, height=1000)

    reupload_button = st.button('Reupload another prompt and excel file')
    if reupload_button:
        st.session_state.filtered = False
        st.experimental_rerun()