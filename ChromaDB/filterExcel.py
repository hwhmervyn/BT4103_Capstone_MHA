import sys, os
workingDirectory = os.getcwd()
sys.path.append(workingDirectory)

from filterConstants import chat, chat_prompt, excel_parser, retry_prompt, output_fixer
import pandas as pd
from json.decoder import JSONDecodeError
from concurrent.futures import ThreadPoolExecutor
from langchain.callbacks import get_openai_callback

def correctFormatToJson(result_content, numTries, error_message):
  if numTries > 3:
     return None
  else:
    try:
      jsonResult = output_fixer.parse_with_prompt(result_content, retry_prompt.format_prompt(error=error_message, output=result_content))
    except JSONDecodeError:
      jsonResult = correctFormatToJson(result_content, numTries+1, error_message) 
    except Exception:
      jsonResult = None
    return jsonResult

def createTask(doi, title, abstract, query):
  with get_openai_callback() as usage_info:
    request = chat_prompt.format_prompt(title=title, abstract=abstract, question=query).to_messages()
    result = chat(request)
    try:
      jsonOutput = excel_parser.parse(result.content)
    except JSONDecodeError as e:
      jsonOutput = correctFormatToJson(result.content, 1, str(e))
    except Exception:
      jsonOutput = None
    total_input_tokens = usage_info.prompt_tokens
    total_output_tokens = usage_info.completion_tokens
    total_cost = usage_info.total_cost
    return (doi, title, abstract, result.content, jsonOutput, total_input_tokens, total_output_tokens, total_cost)

def filterExcel(fileName, query):
  df = pd.read_excel(fileName).dropna(how='all')[['DOI','TITLE','ABSTRACT']].iloc[:5]
  executor = ThreadPoolExecutor(max_workers=2)
  futures = []
  for _, row in df.iterrows():
      doi, title, abstract = row
      futures.append(executor.submit(createTask, doi, title, abstract, query))
  return (executor, futures)

def getOutputDF(dfOut):
    json_exists = ~dfOut["jsonOutput"].isna()
    dfOut.insert(3,'prediction', None, True)
    dfOut.loc[json_exists, 'prediction'] = dfOut.loc[json_exists, "jsonOutput"].apply(lambda x: x.get('answer'))
    dfOut.insert(4,'justification_for_relevancy', None, True)
    dfOut.loc[json_exists, 'justification_for_relevancy'] = dfOut.loc[json_exists, "jsonOutput"].apply(lambda x: x.get('explanation'))
    dfOut = dfOut.drop('jsonOutput', axis=1)
    return dfOut

# # FOR TESTING
# executor, futures = filterExcel("data/combined.xlsx",  "Is the article about Food.")
# from concurrent.futures import as_completed
# from tqdm import tqdm
# issues = []
# results = []
# with tqdm(total=len(futures)) as pbar:
#     for future in as_completed(futures):
#         row = future.result()
#         results.append(row)
#         pbar.update(1)

# dfOut = pd.DataFrame(results, columns = ["DOI","TITLE","ABSTRACT","llmOutput", "jsonOutput"])
# dfOut['prediction'] = dfOut["jsonOutput"].apply(lambda x: x['answer'])
# dfOut['justification_for_relevancy'] = dfOut["jsonOutput"].apply(lambda x: x['explanation'])
# dfOut.to_excel("test_output_pfa.xlsx")
# print()