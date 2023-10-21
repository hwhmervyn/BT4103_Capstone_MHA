import streamlit as st
from llmConstants import chat
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.prompts.few_shot import FewShotPromptTemplate
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
import json
from json.decoder import JSONDecodeError

############################################ SPELL CHECKING ######################################################################

#Create a parser to correct the input and output as a parser
class CorrectInput(BaseModel):
	corrected_question: str = Field(description= "Correct the question if necessary")

#Initialise LLM chain with the prompt
def initialise_LLM_chain(llm, prompt):
    return LLMChain(llm=llm, prompt=prompt)

#Creates a spell checker prompt that helps to check for any grammatical or spelling errors
def create_spell_checker_prompt(): 
	# Set up a parser for spell checking
	spell_checker_parser = PydanticOutputParser(pydantic_object=CorrectInput)

	#Spell checker prompt template
	spell_checker_prompt_template = """
	[INST]<<SYS>>
	Check the question given by the user to see if there are any grammatical, spelling errors or unnecessary characters<</SYS>>
	Question: {question}
	Format: {format_instructions}
	"""
		
	#Create the spell_checking_prompt
	spell_checking_prompt = PromptTemplate(
		template= spell_checker_prompt_template,
		input_variables=["question"],
		partial_variables={"format_instructions": spell_checker_parser.get_format_instructions()}
	)
	return spell_checking_prompt


#Gets the corrected text after text cleaning. Outputs an error if the LLM doesn't understand the question
def get_corrected_text(llm_response):
	corrected_question = None
	error_message = "error"
	try:
		corrected_question = llm_response['text']
		corrected_qn_dict = json.loads(corrected_question)
		corrected_question = corrected_qn_dict['corrected_question']
	except JSONDecodeError:
		corrected_question = error_message
	except Exception:
		corrected_question = error_message
	return corrected_question

#Run the spell check
def run_spell_check(query):
	#Create the prompt for spell check
	spell_checker_prompt = create_spell_checker_prompt()
	#Initialise the LLM chain with the prompt for spell check
	spell_checker_llm_chain = initialise_LLM_chain(chat, spell_checker_prompt)
	#Get the response from the LLM
	spell_checker_llm_response = spell_checker_llm_chain(query)
	return get_corrected_text(spell_checker_llm_response)


############################################ RELEVANCY CHECKING ######################################################################

#Creates a relevant question checker prompt that determines whether the user question is relevant or not
def create_relevant_qn_checker_prompt():
	#Set up a prompt template 
	relevant_qn_checker_prompt_template = """
	[INST]<<SYS>>
	You are a psychology researcher extracting findings from research papers.
	Check the question given by the user to see whether it has a similar phrasing to the examples. The question should be related to an academic topic/SYS>>
	Question: {question}
	Format: Answer either Relevant or Irrelevant to an academic topic in 1 word.
	"""
	#Input examples for the llm to check against
	examples = [{'question': 'Is the article relevant to a topic?',
				},
             	{'question': 'Does the article mention how a topic should be mentioned?',
				},
                { 'question': 'Regarding topic, what did the article mention?',
				},
                {'question' : 'What is mentioned about topic?',
				}]
		
	#Create a prompt without the examples
	relevant_qn_checker_prompt = PromptTemplate(input_variables=["question"], template= relevant_qn_checker_prompt_template)
      
	#Create a prompt template including the examples
	relevant_qn_checker_few_shot_prompt = FewShotPromptTemplate(
		examples=examples,
		example_prompt=relevant_qn_checker_prompt,
		suffix="Question: {question}",
		input_variables=["question"]
	)
	return relevant_qn_checker_few_shot_prompt

#Gets either a word Irrelevant or Relevant 
def get_relevancy(llm_response):
	relevancy = None
	error_message = "error"
	try:
		relevancy = llm_response['text']
	except JSONDecodeError:
		relevancy = error_message
	except Exception:
		relevancy = error_message
	return relevancy

#Runs the relevancy check
def run_relevancy_check(query):
	#Create the prompt for relevancy
	relevant_qn_checker_prompt = create_relevant_qn_checker_prompt()
	#Initialise the LLM chain with the prompt for relevancy
	relevant_qn_checker_llm_chain = initialise_LLM_chain(chat, relevant_qn_checker_prompt)
	#Get the response from the LLM
	relevant_qn_checker_llm_response = relevant_qn_checker_llm_chain(query)
	return get_relevancy(relevant_qn_checker_llm_response)

	
