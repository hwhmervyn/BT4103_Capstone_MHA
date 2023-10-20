import sys, os
workingDirectory = os.getcwd()
miscellaneousDirectory = os.path.join(workingDirectory, "Miscellaneous")
sys.path.append(miscellaneousDirectory)
from User_Input_Cleaning import  run_spell_check, run_relevancy_check

error_query = "Doe 123 the artcle mention && ^^ any cultre relted adaption??"
corrected_question = run_spell_check(error_query)
print(f'Corrected Question is {corrected_question}')

irrelevant_error_query = "Does the article mention drug harms"
relevancy = run_relevancy_check(irrelevant_error_query)
print(f'Relevancy is {relevancy}')