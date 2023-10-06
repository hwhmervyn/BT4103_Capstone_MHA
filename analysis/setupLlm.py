import os
import openai
from dotenv import load_dotenv, find_dotenv
from langchain.chat_models import ChatOpenAI

def get_chat_llm():
    # Read local .env file to retrieve API key
    _ = load_dotenv(find_dotenv())
    openai.api_key = os.environ["OPENAI_API_KEY"]
    # Initialise LLM
    # LLM settings can be configured below
    llm = ChatOpenAI(temperature=0, # lower temperature --> more predictable responses
                model_name = 'gpt-3.5-turbo')
    return llm