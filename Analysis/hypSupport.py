import json
import textwrap
import time
import pandas as pd
import plotly.graph_objects as go
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA

# Build path from working directory and add to system paths to facilitate local module import
import os, sys
sys.path.append(os.path.join(os.getcwd(), "ChromaDB"))

from llmConstants import chat
from ChromaDB.chromaUtils import getCollection, getDistinctFileNameList

### Aesthetic parameters ###
COLOUR_MAPPING = {"Yes": "paleturquoise", "No": "lightsalmon", "Unsure": "lightgrey"}
# Text wrap for output in table
WRAPPER = textwrap.TextWrapper(width=80) # creates a split every 80 characters

### LLM ###
LLM = chat
  
### Prompt template ###
PROMPT_TEMPLATE = """
    You are a psychology researcher extracting information from research papers.
    Answer the question using only the provided context below.
    Context: ### {context} ###
    Format: ### {format_instructions} ###
    Qn: ### {question} ###
  """

### Parser object ###
from typing import List
from langchain.output_parsers import PydanticOutputParser
from langchain.pydantic_v1 import BaseModel, Field

class Support(BaseModel):
    stance: str = Field(description="1-word stance (Yes/No/Unsure) to answer question")
    evidence: List[str] = Field(description="list of 3 sentences from the context as evidence to explain answer")
  
OUTPUT_PARSER = PydanticOutputParser(pydantic_object=Support)
OUTPUT_FORMAT_INSTRUCTIONS = OUTPUT_PARSER.get_format_instructions()

### Helper functions ###

def get_llm_response(db, query, article_title):
  # Initialise prompt template with 2 variables --> context and question
  prompt = PromptTemplate(template=PROMPT_TEMPLATE,
                          input_variables=["context", "question"],
                          partial_variables={"format_instructions": OUTPUT_FORMAT_INSTRUCTIONS})

  # RAG chain
  qa_chain = RetrievalQA.from_chain_type(
      llm=LLM,
      # Only chunks from a particular article are retrieved
      retriever=db.as_retriever(
          search_type="similarity",
          search_kwargs={'k': 3,
                        'filter': {"fileName": article_title}
          }),
      chain_type="stuff",
      chain_type_kwargs={"prompt": prompt},
      return_source_documents=True
  )

  result = qa_chain({"query": query})
  return (result["result"], result["source_documents"])

def get_stance_and_evidence(response):
  print(response) # TODO REMOVE
  response_dict_obj = json.loads(response)
  stance = response_dict_obj["stance"]
  evidence_list = response_dict_obj["evidence"]
  # Join list of evidence into a single string.
  evidence_str = ". ".join(evidence_list)
  return stance, evidence_str

def add_line_breaks(text):
  text_list = text.split(". ")
  new_text_list = []
  for text in text_list:
    # Add line breaks for easier viewing of output
    new_text = '<br>' + "<br>".join(WRAPPER.wrap(text.strip())) + '</br>'
    new_text_list.append(new_text)
  return "".join(new_text_list)

### Output functions ###

def get_support_df(query):
  # Instantiate database
  db = getCollection("pdf")

  # Initialise holder lists
  stance_list = []
  evidence_list = []
  source_docs_list = []
  article_title_list = getDistinctFileNameList("pdf")[:1] # RESTRICT TO 1 FOR TESTING
  total_num_articles = len(article_title_list)

  for i in range(total_num_articles):
    article_title = article_title_list[i]
    start = time.time()
    response, source_docs = get_llm_response(db, query, article_title)
    end = time.time()
    # Get stance and evidence. Append to holder lists
    stance, evidence = get_stance_and_evidence(response)
    stance_list.append(stance)
    evidence_list.append(evidence)
    source_docs_list.append(source_docs)
    # Log to track progress
    time_taken = round(end - start, 0)
    print(f"{i+1}/{total_num_articles} completed. Time taken: {time_taken}s.")
  
  support_df = pd.DataFrame({"article": article_title_list, "stance": stance_list, "evidence": evidence_list, "source_docs": source_docs_list})
  return support_df

def get_support_table(support_df):
    df = support_df.copy()[["article", "stance", "evidence"]]

    # TODO REMOVE
    df["article"] = df["article"].apply(lambda x: x.replace('data\\Compilation of articles\\', ''))

    # Add line breaks to separate sentences
    df["evidence"] = df["evidence"].apply(lambda x: add_line_breaks(x))
    fig = go.Figure(data=[go.Table(
      columnorder = [1,2,3],
      columnwidth = [50,180,420],
      header = dict(
        values = ['<b>Answer</b>', '<b>Article Title</b>', '<b>Evidence</b>'],
        fill_color='midnightblue',
        align='center',
        font=dict(color='white', size=14),
        height=40
      ),
      cells=dict(
        values=[df.stance, df.article, df.evidence],
        fill_color=[df["stance"].map(COLOUR_MAPPING), "white", "white"],
        align=['center', 'left', 'left'],
        font_size=14
        ))
    ])
    return fig

def get_support_chart(support_df):
  df = support_df.copy()[["stance"]].value_counts().reset_index(name="count")
  fig = go.Figure(data=[go.Bar(
      x=df["stance"],
      y=df["count"],
      marker_color=list(df["stance"].map(COLOUR_MAPPING)),
  )])
  return fig