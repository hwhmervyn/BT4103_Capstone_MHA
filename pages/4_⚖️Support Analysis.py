import streamlit as st
from streamlit_extras.app_logo import add_logo
import time
import pandas as pd
from langchain.callbacks import get_openai_callback

# Build path from working directory and add to system paths to facilitate local module import
import os, sys
sys.path.append(os.path.join(os.getcwd(), "ChromaDB"))
sys.path.append(os.path.join(os.getcwd(), "analysis"))
sys.path.append(os.path.join(os.getcwd(), "cost_breakdown"))

from chromaUtils import getCollection, getDistinctFileNameList
from hypSupport import get_llm_response, get_stance_and_evidence, get_support_chart, get_support_table
from Individual_Analysis import get_yes_pdf_filenames
from update_cost import update_usage_logs

st.set_page_config(layout="wide")
add_logo("images/htpd_text.png", height=100)

st.markdown("<h1 style='text-align: left; color: Black;'>Support Analysis</h1>", unsafe_allow_html=True)
st.markdown('#')

input = st.text_input("Research Prompt", placeholder='Enter your prompt (e.g. Is drug A more harmful than drug B?)')
col1, col2 = st.columns(2)
with col1: 
    start_analysis = st.button("Analyse literature support")
with col2:
    analyse_all_articles = st.toggle("All articles", value=False, 
                                     help="Select the toggle to analyse all uploaded articles. If not selected, analysis will only be conducted on filtered articles.")

# Run if "Analyse literature support" button is clicked
if start_analysis:
    # Run if user has included a prompt
    if input:
        # Initialise holder lists to temporarily store output
        stance_list = []
        evidence_list = []
        source_docs_list = []
        article_title_list = []
        total_num_articles = len(article_title_list) # initialised to 0

        # 2 options: Analyse only filtered PDF articles or all PDF articles
        if not analyse_all_articles:
            # Retrieve output dataframe of PDF analysis from Streamlit session state
            if 'pdf_ind_fig2' not in st.session_state:
                st.error("You have no filtered PDF articles")
            else: 
                # Extract output of PDF upload and filtering stage
                ind_findings_df = st.session_state.pdf_ind_fig2
                article_title_list = get_yes_pdf_filenames(ind_findings_df)[:3] # RESTRICT TO 3 FOR TESTING
                total_num_articles = len(article_title_list)
        else:
            article_title_list = getDistinctFileNameList("pdf")[:3] # RESTRICT TO 3 FOR TESTING
            total_num_articles = len(article_title_list)
            if total_num_articles == 0:
                st.error("You have no PDF articles in the database. Please use the PDF Analysis page to upload the articles.")

        with get_openai_callback() as usage_info:
            # Connect to database
            db = getCollection("pdf")
    
            # Obtain dataframe for LLM response
            # Only run if number of articles is greater than 0
            if total_num_articles > 0: 
                progressBar = st.progress(0, text="Analysing articles...")

                start_total = time.time()
                for i in range(total_num_articles):
                    article_title = article_title_list[i]
                    start = time.time()
                    response, source_docs = get_llm_response(db, input, article_title)
                    end = time.time()
                    # Get stance and evidence. Append to holder lists
                    stance, evidence = get_stance_and_evidence(response)
                    stance_list.append(stance)
                    evidence_list.append(evidence)
                    source_docs_list.append(source_docs)
                    # Track time taken
                    time_taken = round(end - start, 0)
                    progress_display_text = f"Analysing articles: {i+1}/{total_num_articles} completed. Time taken: {time_taken}s."
                    progressBar.progress((i+1)/total_num_articles, text=progress_display_text)
                
                support_df = pd.DataFrame({"article": article_title_list, "stance": stance_list, "evidence": evidence_list, "source_docs": source_docs_list})
                end_total = time.time()
                
                # Display success message
                progressBar.empty()
                time_taken_total = round((end_total - start_total)/60, 1)
                st.success(f"Analysis Complete. Total time taken: {time_taken_total}min.")
                
                # TEST
                # support_df = pd.read_csv("C:/Users/laitz/OneDrive/Documents/BT4103_Capstone_MHA/output/support_output [Is cannabis more harmful than tobacco_].csv")

                st.markdown('#')
                st.text("Support Summary Chart:")
                fig1 = get_support_chart(support_df)
                fig1.update_layout(title_text='Distribution of article response')
                st.plotly_chart(fig1, use_container_width=True)

                st.text("Support Summary Table:")
                fig2 = get_support_table(support_df)
                fig2.update_layout(title_text='Article response and evidence', margin_autoexpand=True, height=800)
                st.plotly_chart(fig2, use_container_width=True, )

                # TODO
                # st.download_button(label="Download output dataframe (csv file)",
                #                     # Store output results in a csv file
                #                     data=support_df.to_csv(index=False),
                #                     # Query appended at end of output file name
                #                     file_name=f'support_output [{input}].csv',
                #                     mime='text/csv')
                
                # Update usage info
                update_usage_logs("Support Analysis", input, 
                                usage_info.prompt_tokens, usage_info.completion_tokens, usage_info.total_cost)
    else:
        st.warning("Please input a prompt")