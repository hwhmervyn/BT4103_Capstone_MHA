from ChromaDB.chromaUtils import getCollection
from llmConstants import chat
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
import pandas as pd
import textwrap
import plotly.graph_objects as go



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
def get_findings_from_llm(query, pdf_collection, specific_filename, mention_y_n_prompt_template, llm):
  #Create a Retrieval Chain
  qa_chain = RetrievalQA.from_chain_type(llm=llm,
                                         chain_type="stuff",
                                         retriever= pdf_collection.as_retriever(search_type="similarity", search_kwargs={'k': 3, 'filter': {'fileName': specific_filename}}),
                                         chain_type_kwargs={"prompt": mention_y_n_prompt_template},
                                         return_source_documents=True)
  #Get the results
  result_dict = qa_chain({"query": query})
  result = result_dict['result']
  return result

#Queries the pdfs and outputs a dataframe
def get_findings_from_pdfs(pdf_collection, query, mention_y_n_prompt_template, llm):
  #Get the unique filenames from the pdf collection
  unique_filename_lst = get_unique_filenames(pdf_collection)
  #Just a placeholder to limit the number of filenames to 5
  unique_filename_lst =  unique_filename_lst[:5]
  #List to store yes or no
  yes_no_lst = []
  #List to store the evidence
  evidence_lst = []
  print(len(unique_filename_lst))
  for specific_filename in unique_filename_lst:
    print('\n')
    print(f'File Name: {specific_filename}')
    #Get the findings using the LLM
    result = get_findings_from_llm(query, pdf_collection, specific_filename, mention_y_n_prompt_template, llm)
    #Check whether the pdf is related to the research question and update the lists accordingly
    if 'Yes' in result:
      yes_no_lst.append('Yes')
    else:
      yes_no_lst.append('No')
    print(result)
    evidence_lst.append(result)

  #Output a dataframe
  uncleaned_findings_dict= {'Article Name': unique_filename_lst, 'Answer' : yes_no_lst, 'Evidence' : evidence_lst}
  uncleaned_findings_df = pd.DataFrame(uncleaned_findings_dict)
  return uncleaned_findings_df


#Cleans the evidence strings
def clean_evidence(finding_str):
  #Split the string based on new lines
  finding_str_lst = finding_str.split("\n")
  #Filter out the unnecessary strings
  #str_removed = ['Yes', "No", None]
  #filter_condition = lambda string : '' not in string
  finding_str_lst_filtered = list(filter(None, finding_str_lst))
  finding_str_lst_filtered = finding_str_lst_filtered[1:]
  #Combine into a string again
  finding_str_filtered = ''.join(finding_str_lst_filtered)
  #Text Wrap the string
  str_wrap_lst = textwrap.fill(finding_str_filtered, 30)
  finding_str_final = ''.join(str_wrap_lst)
  return finding_str_final

#Clean the findings df
def clean_findings_df(uncleaned_findings_df):
  cleaned_findings_df = uncleaned_findings_df.copy()
  cleaned_findings_df['Findings'] = cleaned_findings_df['Evidence'].apply(lambda evidence : clean_evidence(evidence))
  #Drop the Evidence columns
  cleaned_findings_df = cleaned_findings_df.drop(columns = 'Evidence')
  return cleaned_findings_df

#Generate a table visualisation
def generate_visualisation(cleaned_findings_df):
  fig = go.Figure(data=[go.Table(
    columnwidth = [10,50],
    header=dict(values=list(cleaned_findings_df.columns),
                fill_color='paleturquoise',
                align='left'),
    cells=dict(values=[cleaned_findings_df['Article Name'], cleaned_findings_df['Answer'], cleaned_findings_df['Findings']],
               fill_color='lavender',
               align='left'))
])
  fig.show()

#Get the pdf collection
collection_name = 'pdf'
pdf_collection = getCollection(collection_name)

#Initialise the prompt template
query = "Does the article mention Psychological First Aid?"
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

#Get the findings and output a placeholder dataframe
uncleaned_findings_df = get_findings_from_pdfs(pdf_collection, query, mention_y_n_prompt_template, chat)

#Clean the findings
cleaned_findings_df = clean_findings_df(uncleaned_findings_df)

#Generate the visualisations
generate_visualisation(cleaned_findings_df)