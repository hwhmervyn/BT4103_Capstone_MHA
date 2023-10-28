import streamlit as st
from streamlit_extras.app_logo import add_logo
import pandas as pd
from langchain.callbacks import get_openai_callback
from json.decoder import JSONDecodeError
import time

# Build path from working directory and add to system paths to facilitate local module import
import os, sys
sys.path.append(os.path.join(os.getcwd(), "ChromaDB"))
sys.path.append(os.path.join(os.getcwd(), "analysis"))
sys.path.append(os.path.join(os.getcwd(), "cost_breakdown"))
sys.path.append(os.path.join(os.getcwd(), "Miscellaneous"))

from chromaUtils import getCollection, getDistinctFileNameList, getListOfCollection
from hypSupport import is_support_qn, get_llm_response, correct_format_json, get_stance_and_evidence, get_support_chart, get_support_table, get_full_cleaned_df
from update_cost import update_usage_logs, Stage
from User_Input_Cleaning import run_spell_check

st.set_page_config(layout="wide")
add_logo("images/temp_logo.png", height=100)


st.markdown("<h1 style='text-align: left; color: Black;'>Support Analysis</h1>", unsafe_allow_html=True)
st.markdown('#')

if 'support_analysis_prompt' not in st.session_state:
    st.session_state.support_analysis_prompt = False
if 'collection' not in st.session_state:
    st.session_state.collection = None

if not st.session_state.support_analysis_prompt:
    input_collection_name = st.selectbox(
        'Input Collection', getListOfCollection(), 
        placeholder="Select the collection you would like to use"
    )
    input = st.text_input("Research Prompt", placeholder='Enter your research prompt (e.g. Is drug A more harmful than drug B?)')
    skip_support_prompt_check = st.toggle("Skip prompt checking", value=False)
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
                # Initialise empty article title list
                article_title_list = []
                total_num_articles = len(article_title_list)
                article_title_list = getDistinctFileNameList(input_collection_name)
                total_num_articles = len(article_title_list)
                # Obtain dataframe of LLM responses. Only run if number of articles > 0
                if total_num_articles > 0:
                    st.warning("DO NOT navigate to another page while the analysis is in progress!")
                    progressBar = st.progress(0, text="Analysing articles...")
                    # Connect to selected database collection
                    db = getCollection(input_collection_name)

                    # Initialise holder lists to temporarily store output
                    response_list = ['']*total_num_articles
                    source_docs_list = ['']*total_num_articles
                    stance_list = ['']*total_num_articles
                    evidence_list = ['']*total_num_articles
                    # Holder list to store article titles with error in obtaining output
                    article_error_list = []

                    # Perform prompt checking
                    if skip_support_prompt_check == False:
                        with get_openai_callback() as usage_info:
                            # Check and correct wrong spelling
                            try: 
                                input = run_spell_check(input)
                            except:
                                progressBar.empty()
                                st.error("Processing Error! Please try again!")
                            # Check suitability of prompt
                            is_support_qn = is_support_qn(input).lower()
                            if is_support_qn != "yes":
                                progressBar.empty()
                                st.error("Please rephrase your prompt")
                            update_usage_logs(Stage.MISCELLANEOUS.value, input, usage_info.prompt_tokens, usage_info.completion_tokens, usage_info.total_cost)

                    # Run Support Analysis
                    if skip_support_prompt_check == True or is_support_qn == "yes":
                        with get_openai_callback() as usage_info:
                            for i in range(total_num_articles):
                                try: 
                                    article_title = article_title_list[i]
                                    # Make LLM call to get response
                                    response, source_docs = get_llm_response(db, input, article_title)
                                    response_list[i] = response
                                    source_docs_list[i] = source_docs
                                    # Extract stance and evidence from response
                                    stance, evidence = get_stance_and_evidence(response)
                                    stance_list[i] = stance
                                    evidence_list[i] = evidence
                                except JSONDecodeError:
                                    corrrected_response = correct_format_json(response_list[i])
                                    response_list[i] = corrrected_response
                                    try: 
                                        stance, evidence = get_stance_and_evidence(response_list[i])
                                        stance_list[i] = stance
                                        evidence_list[i] = evidence
                                    except Exception:
                                        article_error_list.append(article_title)
                                except Exception:
                                    article_error_list.append(article_title)

                                # Update progress
                                progress_display_text = f"Analysing articles: {i+1}/{total_num_articles} completed"
                                progressBar.progress((i+1)/total_num_articles, text=progress_display_text)
                                
                            support_df_raw = pd.DataFrame({"article": article_title_list, "stance": stance_list, "evidence": evidence_list, "source_docs": source_docs_list, "raw_output": response_list})
                            # Store dataframe as Excel file in local output folder
                            support_df_cleaned = get_full_cleaned_df(support_df_raw)
                            support_df_cleaned.to_excel("output/support_analysis_results.xlsx", index=False)
                            
                            # Display success message
                            progressBar.empty()
                            st.success(f"Analysis Complete")

                            # Display error message if there are articles that cannot be analysed due to error
                            if len(article_error_list) > 0:
                                st.error("Error in extracting output for the articles below")
                                with st.expander("Articles with error:"):
                                    for article_title in article_error_list:
                                        st.markdown(f"- {article_title}")
                            
                            end_time = time.time()
                            time_taken_seconds = end_time - start_time
                            time_taken_hours_minute_seconds =  time.strftime("%H:%M:%S", time.gmtime(time_taken_seconds))
                            print(f'Time taken in seconds is {time_taken_seconds} seconds')
                            print(f'Time taken in hours minutes and seconds is {time_taken_hours_minute_seconds}')
                            st.success(f'Successful! Time taken: {time_taken_hours_minute_seconds}')
                        
                            # Update usage info
                            update_usage_logs(Stage.SUPPORT_ANALYSIS.value, input, 
                                usage_info.prompt_tokens, usage_info.completion_tokens, usage_info.total_cost)
                            
                            # TEST
                            # support_df_raw = pd.read_csv("C:/Users/laitz/OneDrive/Documents/BT4103_Capstone_MHA/output/support_output [Is cannabis more harmful than tobacco_].csv")
                            # support_df_cleaned = get_full_cleaned_df(support_df_raw)
                            # support_df_cleaned.to_excel("output/support_analysis_results.xlsx", index=False)

                            st.session_state.support_analysis_prompt = input
                            st.session_state.support_analysis_collection = input_collection_name
                            st.experimental_rerun()
                else:
                    st.error("You have no PDF articles in this collection")
            else:
                st.error("Please input a prompt")
        else: 
            st.error("Please select a collection. If a collection has not been created, please use the My Collections page to do so.")
       
else:
    st.subheader("Prompt")
    st.markdown(st.session_state.support_analysis_prompt)
    st.subheader("Collection")
    st.markdown(st.session_state.support_analysis_collection)

    # Read output Excel file
    support_df = pd.read_excel("output/support_analysis_results.xlsx")
    st.subheader("Results")
    
    st.markdown("Support Summary Chart:")
    fig1 = get_support_chart(support_df)
    fig1.update_layout(title_text='Distribution of article response')
    st.session_state.support_chart = fig1
    st.plotly_chart(st.session_state.support_chart, use_container_width=True)

    st.markdown("Support Summary Table:")
    fig2 = get_support_table(support_df)
    support_table_height = min(support_df.shape[0]*270, 800)
    fig2.update_layout(title_text='Article response and evidence', margin_autoexpand=True, height=support_table_height)
    st.session_state.support_table = fig2
    st.plotly_chart(st.session_state.support_table, use_container_width=True)

    st.markdown("Download Output File:")
    # Download output as Excel file
    with open("output/support_analysis_results.xlsx", 'rb') as my_file:
        st.download_button(label="Download Excel",
                            # Store output results in a csv file
                            data=my_file,
                            # Query appended at end of output file name
                            file_name=f'support_output [{st.session_state.support_analysis_collection}] [{st.session_state.support_analysis_prompt}].xlsx',
                            mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    
    st.markdown("#")
    retry_button = st.button('Submit another prompt')
    if retry_button:
        st.session_state.support_analysis_prompt = False
        st.experimental_rerun()