import streamlit as st
from streamlit_extras.app_logo import add_logo
import time
import pandas as pd
from langchain.callbacks import get_openai_callback

# Build path from working directory and add to system paths to facilitate local module import
import os, sys
sys.path.append(os.path.join(os.getcwd(), "analysis"))
sys.path.append(os.path.join(os.getcwd(), "cost_breakdown"))

from hypSupport import get_support_df, get_support_chart, get_support_table
from cost_breakdown.update_cost import update_usage_logs

st.set_page_config(layout="wide")
add_logo("images/htpd_text.png", height=100)

st.markdown("<h1 style='text-align: left; color: Black;'>Support Analysis</h1>", unsafe_allow_html=True)
st.markdown('#')

input = st.text_input("Research Prompt", placeholder='Enter your prompt (e.g. Is drug A harmful?)')
if st.button("Analyse literature support"):
    with get_openai_callback() as usage_info:
        st.markdown('#')
        try:
            # # TODO: Add progress bar
            # # DUMMY FOR FILTERING
            # PARTS_ALLOCATED_FILTER = 0.7
            # for percent_complete in range(30,100):
            #     time.sleep(0.1)
            #     progessBar1.progress(float(percent_complete/100), text="Uploading main pdf sections:")
            # st.session_state.pdf_filtered = True
            # st.experimental_rerun()
            # progess_bar = st.progress(0, text="Analysing ar:")
            
            support_df = get_support_df(input)
            # TEST
            # support_df = pd.read_csv("C:/Users/laitz/OneDrive/Documents/BT4103_Capstone_MHA/output/support_output [Is cannabis more harmful than tobacco_].csv")

            st.text("Support Summary Chart:")
            fig1 = get_support_chart(support_df)
            fig1.update_layout(title_text='Distribution of article response')
            st.plotly_chart(fig1, use_container_width=True)

            st.text("Support Summary Table:")
            fig2 = get_support_table(support_df)
            fig2.update_layout(title_text='Article response and evidence', margin_autoexpand=True, height=800)
            st.plotly_chart(fig2, use_container_width=True, )

            # TODO
            st.download_button(label="Download output dataframe (csv file)",
                               # Store output results in a csv file
                               data=support_df.to_csv(index=False),
                               # Query appended at end of output file name
                               file_name=f'support_output [{input}].csv',
                               mime='text/csv')
        except Exception as err:
            st.error(f"Unexpected Error: {err}")
            st.error(f"Error Type: {type(err)}")

        # Update usage info
        update_usage_logs("Support Analysis", input, 
                          usage_info.prompt_tokens, usage_info.completion_tokens, usage_info.total_cost)