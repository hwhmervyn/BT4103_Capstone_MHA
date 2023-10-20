from llmConstants import chat
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.prompts.few_shot import FewShotPromptTemplate
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
import json

## Spell Checking ##

#Create a parser to correct the input and output as a parser
class CorrectInput(BaseModel):
    corrected_question: str = Field(description= "Correct the question if needed and output it as a question")
    
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
	You are a psychology researcher extracting findings from research papers.
	Check the question given by the user to see if there are any grammatical or spelling errors. Check for unnecessary characters too<</SYS>>
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

#Gets the corrected text after text cleaning
def get_corrected_text(llm_response):
      corrected_question = llm_response['text']
      corrected_qn_dict = json.loads(corrected_question)
      return corrected_qn_dict['corrected_question']

#Creates a relevant question checker prompt that determines whether the user question is relevant or not
def create_relevant_qn_checker_prompt():
	#Set up a prompt template 
	relevant_qn_checker_prompt_template = """
	[INST]<<SYS>>
	You are a psychology researcher extracting findings from research papers.
	Check the question given by the user to see whether it has a similar phrasing to the examples<</SYS>>
	Question: {question}
	Format: Answer either Relevant or Irrelevant in 1 word
	"""
	#Input examples for the llm to check against
	examples = [ {'question': 'Does the article mention how psychological first aid should be mentioned?',
				 },
                { 'question': 'Regarding psychological first aid, what did the article mention?',
				},
                {'question' : 'What is mentioned about culture related information?',
				}]
		
	#Create a prompt without the examples
	relevant_qn_checker_prompt = PromptTemplate(input_variables=["question"], 
														template= relevant_qn_checker_prompt_template)
      
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
	return llm_response['text']

### Testing purposes ###

## To check for grammar and spelling
error_query = "Doe 678 the artcle mention && ^^ any cultre relted adaption??"
spell_checker_prompt = create_spell_checker_prompt()
spell_checker_llm_chain = initialise_LLM_chain(chat, spell_checker_prompt)
spell_checker_llm_response = spell_checker_llm_chain(error_query)
corrected_question = get_corrected_text(spell_checker_llm_response)
print(f'Corrected Question is {corrected_question}')


## To check for relevant of irrelevant
irrelevant_error_query = "Does the article mention drug harms"
relevant_qn_checker_prompt = create_relevant_qn_checker_prompt()
relevant_qn_checker_llm_chain = initialise_LLM_chain(chat, relevant_qn_checker_prompt)
relevant_qn_checker_llm_response = relevant_qn_checker_llm_chain(irrelevant_error_query)
relevancy = get_relevancy(relevant_qn_checker_llm_response)
print(f'Relevancy is {relevancy}')