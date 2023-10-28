import textwrap
import plotly.graph_objects as go
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA

from llmConstants import chat

### Aesthetic parameters ###
# Text wrap for output in table
WRAPPER = textwrap.TextWrapper(width=80) # creates a split every 80 characters

### LLM ###
LLM = chat
  
### Prompt template ###
PROMPT_TEMPLATE = """
    You are a psychology researcher extracting information from research papers.
    Answer the question using only the provided context below. Follow the additional instructions given (if any).
    Context: ### {context} ###
    Qn: ### {question} ###
    Additional instructions: ### {instructions} ###
    If you do not know the answer, output "Unsure". 
  """

### Helper functions ###

def get_llm_response(db, query, article_title, chunk_search_method="similarity", num_chunks_retrieved=3, additional_inst=""):
  # Initialise prompt template with 2 variables --> context and question
  prompt = PromptTemplate(template=PROMPT_TEMPLATE,
                          input_variables=["context", "question"],
                          partial_variables={"instructions": additional_inst})

  # RAG chain
  qa_chain = RetrievalQA.from_chain_type(
      llm=LLM,
      # Only chunks from a particular article are retrieved
      # Chunk search method and number of chunks retrieved can be tweaked
      retriever=db.as_retriever(
          search_type=chunk_search_method,
          search_kwargs={'k': num_chunks_retrieved,
                        'filter': {"fileName": article_title}
          }),
      chain_type="stuff",
      chain_type_kwargs={"prompt": prompt},
      return_source_documents=True
  )

  result = qa_chain({"query": query})
  return (result["result"], result["source_documents"])

def add_line_breaks(text):
  # Add line breaks for easier viewing of output
  new_text = "<br>".join(WRAPPER.wrap(text.strip()))
  return new_text

### Output functions ###

def get_support_table(support_df):
    df = support_df.copy()[["article", "answer"]]
    # Add line breaks to separate sentences
    df["answer"] = df["answer"].apply(lambda x: add_line_breaks(x))

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
      columnorder = [1,2],
      columnwidth = [170,420],
      header = dict(
        values = ['<b>Article Name</b>', '<b>Answer</b>'],
        fill_color='#203864',
        align='left',
        font=dict(color='white', size=14),
        height=40
      ),
      cells=dict(
        values=[df.article, df.answer],
        fill_color=["white", "white"],
        align=['left', 'left'],
        font_size=14
        ))
    ], layout=layout)
    return fig