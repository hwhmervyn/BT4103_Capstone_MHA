from ChromaDB.chromaUtils import getCollection
from llmConstants import chat
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain.callbacks import get_openai_callback
import pandas as pd
import re
import textwrap
from random import sample
import plotly.graph_objects as go
import time

import sys,os
sys.path.append('cost_breakdown')
from update_cost import update_usage_logs

### Aesthetic parameters ###
COLOUR_MAPPING = {"Yes": "paleturquoise", "No": "lightsalmon", "Unsure": "lightgrey"}
# Text wrap for output in table
WRAPPER = textwrap.TextWrapper(width=160) # creates a split every 160 characters

#Get the unique file names in the pdf collection
def get_unique_filenames(pdf_collection):
  #Get the pdf collection with metadatas which include the filename
  pdf_collection_with_metadata = pdf_collection.get(include=["metadatas"])
  #Get the metadata list
  metadata_dict_lst = pdf_collection_with_metadata['metadatas']
  #Get every single filename that maps to each document
  duplicated_filename_lst = [metadata_dict['fileName'] for metadata_dict in metadata_dict_lst]
  #Get the unique filenames
  unique_filename_lst = list(set(duplicated_filename_lst))
  return unique_filename_lst

#Retrieve findings from the llm
def get_findings_from_llm(query, pdf_collection, specific_filename, mention_y_n_prompt, llm):
  #Create a Retrieval Chain
  qa_chain = RetrievalQA.from_chain_type(llm=llm,
                                         chain_type="stuff",
                                         retriever= pdf_collection.as_retriever(search_type="similarity", search_kwargs={'k': 3, 'filter': {'fileName': specific_filename}}),
                                         chain_type_kwargs={"prompt": mention_y_n_prompt},
                                         return_source_documents=True)
  #Get the results
  result_dict = qa_chain({"query": query})
  result = result_dict['result']
  return result

#Queries the pdfs and outputs a dataframe
def get_findings_from_pdfs(pdf_collection, query, mention_y_n_prompt, llm, progressBar1):
  #Get the unique filenames from the pdf collection
  unique_filename_lst = get_unique_filenames(pdf_collection)
  total_num_articles = len(unique_filename_lst)
  #Just a placeholder to limit the number of filenames to 5
  #unique_filename_lst =  sample(unique_filename_lst, 5)
  #List to store yes or no
  yes_no_lst = []
  #List to store the evidence
  evidence_lst = []
  print(total_num_articles)

  # For progress bar
  PARTS_ALLOCATED_UPLOAD_MAIN = 0.3
  PARTS_ALLOCATED_IND_ANALYSIS = 0.5
  numDone = 0
  progressBar1.progress(PARTS_ALLOCATED_UPLOAD_MAIN, text=f"Analysing articles: {numDone}/{total_num_articles} completed...") 

  with get_openai_callback() as usage_info:
    for specific_filename in unique_filename_lst:
      print('\n')
      print(f'File Name: {specific_filename}')
      #Get the findings using the LLM
      result = get_findings_from_llm(query, pdf_collection, specific_filename, mention_y_n_prompt, llm)
      #Check whether the pdf is related to the research question and update the lists accordingly
      if 'Yes' in result:
        yes_no_lst.append('Yes')
      else:
        yes_no_lst.append('No')
      print(result)
      evidence_lst.append(result)

      numDone += 1
      progress = PARTS_ALLOCATED_UPLOAD_MAIN + (float(numDone/total_num_articles) * PARTS_ALLOCATED_IND_ANALYSIS)
      progress_display_text = f"Analysing articles: {numDone}/{total_num_articles} completed..."
      progressBar1.progress(progress, text=progress_display_text)
      
  total_input_tokens = usage_info.prompt_tokens
  total_output_tokens = usage_info.completion_tokens
  total_cost = usage_info.total_cost
  update_usage_logs("Individual Analysis", query, total_input_tokens, total_output_tokens, total_cost)

  #Output a dataframe
  uncleaned_findings_dict= {'Article Name': unique_filename_lst, 'Answer' : yes_no_lst, 'Evidence' : evidence_lst}
  uncleaned_findings_df = pd.DataFrame(uncleaned_findings_dict)
  return (uncleaned_findings_df, total_input_tokens, total_output_tokens, total_cost)

#Cleans the evidence strings
def clean_evidence(finding_str):
  #Remove the Yes No
  yes_no_pattern = r'\b(?:Yes|No)\b'
  finding_str = re.sub(yes_no_pattern, '', finding_str)
  #Remove the . in the case of Yes.
  full_stop_pattern = r'^[.\s]*'
  finding_str = re.sub(full_stop_pattern, '', finding_str)
  #Remove the 1., 2., 3. and replace with the *
  numbering_pattern = r'^\d+\.\s'  # Matches lines starting with a number, period, and space
  finding_str = re.sub(numbering_pattern, '', finding_str, flags=re.MULTILINE)
  #Insert newline after full stops
  full_stop_pattern2 = r'\.'
  finding_str = re.sub(full_stop_pattern2, '.\n', finding_str)
  #Text Wrap the string (may not need)
  #finding_str = textwrap.fill(finding_str, 30)
  #Replace the * with breaks so that we can display a line break 
  #finding_str_final = finding_str.replace('*', "")
  return finding_str

#Clean the findings df
def clean_findings_df(uncleaned_findings_df):
  cleaned_findings_df = uncleaned_findings_df.copy()
  cleaned_findings_df['Findings'] = cleaned_findings_df['Evidence'].apply(lambda evidence : clean_evidence(evidence))
  
  #Drop the Evidence columns
  cleaned_findings_df = cleaned_findings_df.drop(columns = 'Evidence')
  return cleaned_findings_df

def add_line_breaks(text):
  text_list = text.split(". ")
  new_text_list = []
  for text in text_list:
    # Add line breaks for easier viewing of output
    new_text = "<br>".join(WRAPPER.wrap(text.strip())) + '</br>'
    new_text_list.append(new_text)
  return "".join(new_text_list)

#Generate a table visualisation
def generate_visualisation(cleaned_findings_df):
  cleaned_findings_df['Findings_Visualised'] = cleaned_findings_df['Findings'].apply(lambda x: add_line_breaks(x))

  layout = go.Layout(
    margin=go.layout.Margin(
      l=0, #left margin
      r=0, #right margin
      b=0, #bottom margin
      t=0,  #top margin
      pad=0
    )
  )

  fig = go.Figure(data=[go.Table(
    columnwidth = [50,50,280],
    header=dict(values=['Article Name', 'Answer', 'Findings'],
                fill_color='paleturquoise',
                align='left'),
    cells=dict(values=[cleaned_findings_df['Article Name'], cleaned_findings_df['Answer'], cleaned_findings_df['Findings_Visualised']],
               fill_color='lavender',
               align='left')
    )
  ], layout=layout)

  fig.update_layout(autosize=False,
                    height=200)

  return fig

#Get pdf filenames that mention the topic
def get_yes_pdf_filenames(cleaned_findings_df):
  answer = 'yes'
  yes_pdf = cleaned_findings_df.query('Answer = @answer')
  return yes_pdf['Article Name'].values.tolist()

def ind_analysis_main(query, progressBar1):
  #Get the pdf collection
  collection_name = 'pdf'
  pdf_collection = getCollection(collection_name)

  #Initialise the prompt template
  #query = "Does the article mention Psychological First Aid?"
  mention_y_n_prompt_template = """
    [INST]<<SYS>>
    You are a psychology researcher extracting findings from research papers.
    If you don't know the answer, just say that you don't know, do not make up an answer.
    Use only the context below to answer the question.<</SYS>>
    Context: {context}
    Question: {question}
    Only provide your answer. Do not provide comments.
    Answer Yes or No in 1 word. List 3 sentences of evidence to explain.
    [/INST]
    """
  mention_y_n_prompt = PromptTemplate.from_template(mention_y_n_prompt_template)
  
  results_tup = get_findings_from_pdfs(pdf_collection, query, mention_y_n_prompt, chat, progressBar1)

  #Retrieve the dataframe
  uncleaned_findings_df = results_tup[0]

  #Clean the findings
  cleaned_findings_df = clean_findings_df(uncleaned_findings_df)

  #Generate the visualisations
  fig = generate_visualisation(cleaned_findings_df)

  return cleaned_findings_df[["Article Name", "Answer", "Findings"]], fig