import sys, os
cleanDirectory = os.path.join(os.getcwd(), "Miscellaneous")

if cleanDirectory not in sys.path:
    sys.path.append(cleanDirectory)
    
from User_Input_Cleaning import run_spell_check, run_relevancy_check

input = "list the hams of cannabis?"

corrected_question = run_spell_check(input)

print(f"Corrected Input is {corrected_question}")


