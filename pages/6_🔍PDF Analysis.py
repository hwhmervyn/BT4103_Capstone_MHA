import streamlit as st
from streamlit_extras.app_logo import add_logo
import pandas as pd
from langchain.callbacks import get_openai_callback
import time

# Build path from working directory and add to system paths to facilitate local module import
import os, sys
sys.path.append(os.path.join(os.getcwd(), "ChromaDB"))
sys.path.append(os.path.join(os.getcwd(), "analysis"))
sys.path.append(os.path.join(os.getcwd(), "cost_breakdown"))
sys.path.append(os.path.join(os.getcwd(), "Miscellaneous"))

from chromaUtils import getCollection, getDistinctFileNameList, getListOfCollection
from Freeform_Analysis import get_llm_response, get_support_table
from update_cost import update_usage_logs, Stage
from User_Input_Cleaning import run_spell_check

st.set_page_config(layout="wide")
add_logo("images/temp_logo.png", height=100)


st.markdown("<h1 style='text-align: left; color: Black;'>PDF Analysis</h1>", unsafe_allow_html=True)
st.markdown('#')

if 'pdf_analysis_prompt' not in st.session_state:
    st.session_state.pdf_analysis_prompt = False
if 'collection' not in st.session_state:
    st.session_state.collection = None

if not st.session_state.pdf_analysis_prompt:
    # Select collection to analyse
    input_collection_name = st.selectbox(
        'Input Collection', getListOfCollection(), 
        placeholder="Select the collection you would like to use"
    )
    # Provide option to analyse single article
    if input_collection_name:
        analyse_single_article = st.toggle("Analyse single article", value=False, help="Select only 1 article from input collection to analyse. All articles in the collection will be analysed by default.")
        if analyse_single_article:
            selected_article_name = st.selectbox(
                'Select Article', getDistinctFileNameList(input_collection_name), 
                placeholder="Select the article you would like to analyse"
            )

    # Get user prompt
    input = st.text_input("Research Prompt", placeholder='Enter your research prompt')

    # Initialise retrieval settings
    chunk_search_method = "similarity"
    num_chunks_retrieved = 3
    # Configure retrieval settings
    configure_retrieval_settings = st.toggle("Configure retrieval settings", value=False, help="Default settings will be used if no configuration selected")
    if configure_retrieval_settings:
        col1, col2 = st.columns(2)
        with col1:
            chunk_search_method = st.radio("Chunk search method", ["Similarity", "Maximal Marginal Relevance (MMR)"], index=0, 
                                           help="Similarity option selects chunks that are most relevant to input prompt. MMR option does the same while optimising for diversity among the selected chunks (i.e. chunks that are highly similar to an already selected chunk will not be included)")
        with col2:
            num_chunks_retrieved = st.slider("Num. article chunks to feed to LLM", min_value=3, max_value=10, value=3, 
                                             help="Select number of relevant chunks from the article for the LLM to analyse. Each chunk contains approximately 150 words. More chunks fed will incur higher cost and processing time.")
    # Configure output with additional instructions
    additional_inst = ""
    provide_additional_inst = st.toggle("Provide additional instructions", value=False, help="Add further instructions for LLM")
    if provide_additional_inst:
        additional_inst = st.text_input("Additional Instructions", placeholder='Enter your instructions (e.g. limit output to 3 sentences)')

    # Button to start analysis
    st.markdown('##')
    col1, col2, col3, col4, col5, col6, col7 = st.columns(7)
    with col4: 
        start_analysis = st.button("Submit")

    # Run if "Submit" button is clicked
    if start_analysis:
        start_time = time.time()
        # Run if user has selected a collection of PDFs to analyse
        if input_collection_name:
            # Run if user has included a prompt
            if input:
                if selected_article_name:
                    # Use the single article selected
                    article_title_list = [selected_article_name]
                else:
                    # Get list of article titles in the collection
                    article_title_list = getDistinctFileNameList(input_collection_name)
                total_num_articles = len(article_title_list)
            
                # Run if number of articles > 0
                if total_num_articles > 0:
                    st.warning("DO NOT navigate to another page while the analysis is in progress!")
                    progressBar = st.progress(0, text="Analysing...")

                    # Connect to selected database collection
                    db = getCollection(input_collection_name)

                    # Initialise holder lists to temporarily store output
                    response_list = ['']*total_num_articles
                    source_docs_list = ['']*total_num_articles
                    # Holder list to store article titles with error in obtaining output
                    article_error_list = []

                    # Check and correct wrong spelling
                    with get_openai_callback() as usage_info:
                        try: 
                            input = run_spell_check(input)
                            st.markdown(f'<small style="text-align: left; color: Black;">Prompt taken in as:  <em>"{input}</em>"</small>', unsafe_allow_html=True)
                        except:
                            progressBar.empty()
                            st.error("Processing Error! Please try again!")
                        update_usage_logs(Stage.MISCELLANEOUS.value, input, usage_info.prompt_tokens, usage_info.completion_tokens, usage_info.total_cost)
                    
                    # Run PDF Analysis
                    with get_openai_callback() as usage_info:
                        for i in range(total_num_articles):
                            try: 
                                article_title = article_title_list[i]
                                # Make LLM call to get response
                                response, source_docs = get_llm_response(db, input, article_title, chunk_search_method, num_chunks_retrieved, additional_inst)
                                # Record response and source documents
                                response_list[i] = response
                                source_docs_list[i] = source_docs
                            except Exception:
                                # Track articles that had error in obtaining response
                                article_error_list.append(article_title)
                            # Update progress
                            progress_display_text = f"Analysing: {i+1}/{total_num_articles} completed"
                            progressBar.progress((i+1)/total_num_articles, text=progress_display_text)
                                
                        pdf_analysis_output_df = pd.DataFrame({"article": article_title_list, "answer": response_list, "source_docs": source_docs_list})
                        # Store dataframe as Excel file in local output folder
                        pdf_analysis_output_df.to_excel("output/pdf_analysis_results.xlsx", index=False)
                            
                        # Display success message
                        progressBar.empty()
                        st.success(f"Analysis Complete")

                        # Display error message if there are articles that cannot be analysed due to error
                        if len(article_error_list) > 0:
                            st.error("Error in extracting output for the articles below")
                            with st.expander("Articles with error:"):
                                for article_title in article_error_list:
                                    st.markdown(f"- {article_title}")
                        
                        # Display time taken
                        end_time = time.time()
                        time_taken_seconds = end_time - start_time
                        time_taken_minute_seconds =  time.strftime("%M:%S", time.gmtime(time_taken_seconds))
                        print(f'Time taken in seconds is {time_taken_seconds} seconds')
                        print(f'Time taken in minutes and seconds is {time_taken_minute_seconds}')
                        st.success(f'Successful! Time taken: {time_taken_minute_seconds}')
                        
                        # Update usage info
                        update_usage_logs(Stage.PDF_ANALYSIS.value, input, 
                            usage_info.prompt_tokens, usage_info.completion_tokens, usage_info.total_cost)

                        st.session_state.pdf_analysis_prompt = input
                        st.session_state.pdf_analysis_collection = input_collection_name
                        st.experimental_rerun()
                else:
                    st.error("You have no PDF articles in this collection")
            else:
                st.error("Please input a prompt")
        else: 
            st.error("Please select a collection. If a collection has not been created, please use the My Collections page to do so.")
       
else:
    st.subheader("Prompt")
    st.markdown(st.session_state.pdf_analysis_prompt)
    st.subheader("Collection")
    st.markdown(st.session_state.pdf_analysis_collection)

    # Read output Excel file
    pdf_analysis_df = pd.read_excel("output/pdf_analysis_results.xlsx")
    st.subheader("Results")

    # Download output as Excel file
    with open("output/pdf_analysis_results.xlsx", 'rb') as my_file:
        st.download_button(label="Download Excel",
                            # Store output results in a csv file
                            data=my_file,
                            # Query appended at end of output file name
                            file_name=f'analysis_output [{st.session_state.pdf_analysis_collection}] [{st.session_state.pdf_analysis_prompt}].xlsx',
                            mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    
    # Display output
    fig1 = get_support_table(pdf_analysis_df)
    support_table_height = min(pdf_analysis_df.shape[0]*270, 800)
    fig1.update_layout(title_text='Article response and evidence', margin_autoexpand=True, height=support_table_height)
    st.session_state.support_table = fig1
    st.plotly_chart(st.session_state.support_table, use_container_width=True)
    
    # Repeat process with another question
    retry_button = st.button('Ask another question')
    if retry_button:
        st.session_state.pdf_analysis_prompt = False
        st.experimental_rerun()