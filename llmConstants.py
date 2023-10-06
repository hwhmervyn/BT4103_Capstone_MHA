import os
import openai
from dotenv import load_dotenv, find_dotenv
from langchain.chat_models import ChatOpenAI
from langchain.llms import OpenAI

_ = load_dotenv(find_dotenv())
openai.api_key = os.environ["OPENAI_API_KEY"] 
    # Read local .env file to retrieve API key

chat = ChatOpenAI(temperature=0, # lower temperature --> more predictable responses
            model_name = 'gpt-3.5-turbo')