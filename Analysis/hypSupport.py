import json
import textwrap
import plotly.graph_objects as go
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA
from langchain.chains import LLMChain

from llmConstants import chat

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

def is_support_qn(input):
  prompt_template = """Determine if the given question is asking for a Yes/No answer. Give your answer as yes or no.
    Ex 1: "Is drug A harmful?"
    Ans: yes
    Ex 2: "Are mental health issues prevalent in Singapore?"
    Ans: yes
    Ex 3: "Explain the causes of addiction"
    Ans: no
    Ex 4: "How can we deal with repeat offenders?"
    Ans: no
    Ex. 5: "Does X result in greater damage compared to Y?"
    Ans: yes
    Question: ### {question} ###
    Ans: 
  """
  prompt = PromptTemplate(template=prompt_template,
                            input_variables=["question"])
  result = LLMChain(llm=LLM, prompt=prompt).run(input)
  return result

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

def correct_format_json(response):
  prompt_template = """Convert the given string to a JSON object. 
    Format: ### {format_instructions} ###
    String to convert: ### {string} ###
  """
  prompt = PromptTemplate(template=prompt_template,
                            input_variables=["string"],
                            partial_variables={"format_instructions": OUTPUT_FORMAT_INSTRUCTIONS})
  format_correction_chain = LLMChain(llm=LLM, prompt=prompt)
  result = format_correction_chain.run(response)
  return result

def get_stance_and_evidence(response):
  response_dict_obj = json.loads(response)
  # Ensure consistency of reponse by removing whitespaces, converting to lowercase, and capitalising first letter
  stance = response_dict_obj["stance"].strip().lower().capitalize()
  evidence_list = response_dict_obj["evidence"]
  # Join list of evidence into a single string.
  evidence_str = ". ".join(evidence_list).strip()
  return stance, evidence_str

def get_full_cleaned_df(support_df):
  df = support_df.copy()
  df["evidence"] = df["evidence"].apply(lambda x: " ".join(x.split(". ")))
  return df

def add_line_breaks(text):
  text_list = text.split(". ")
  new_text_list = []
  for text in text_list:
    # Add line breaks for easier viewing of output
    new_text = '<br>' + "<br>".join(WRAPPER.wrap(text.strip())) + '.</br>'
    new_text_list.append(new_text)
  return "".join(new_text_list).replace("..", ".")

### Output functions ###

def get_support_table(support_df):
    df = support_df.copy()[["article", "stance", "evidence"]]
    # Add line breaks to separate sentences
    df["evidence"] = df["evidence"].apply(lambda x: add_line_breaks(x))

    layout = go.Layout(
      margin=go.layout.Margin(
        l=0, #left margin
        r=0, #right margin
        b=0, #bottom margin
        t=0, #top margin
        pad=0
      )
    )
    fig = go.Figure(data=[go.Table(
      columnorder = [1,2,3],
      columnwidth = [60,170,420],
      header = dict(
        values = ['<b>Answer</b>', '<b>Article Name</b>', '<b>Evidence</b>'],
        fill_color='#203864',
        align='left',
        font=dict(color='white', size=14),
        height=40
      ),
      cells=dict(
        values=[df.stance, df.article, df.evidence],
        fill_color=[df["stance"].map(COLOUR_MAPPING).fillna("black"), "white", "white"],
        align=['center', 'left', 'left'],
        font_size=14
        ))
    ], layout=layout)
    return fig

def get_support_chart(support_df):
  df = support_df.copy()[["stance"]].value_counts().reset_index(name="count")
  fig = go.Figure(data=[go.Bar(
      x=df["stance"],
      y=df["count"],
      marker_color=list(df["stance"].map(COLOUR_MAPPING).fillna("black")),
  )])
  return fig