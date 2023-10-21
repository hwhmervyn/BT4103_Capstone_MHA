import sys, os
cleanDirectory = os.path.join(os.getcwd(), "Miscellaneous")

if cleanDirectory not in sys.path:
    sys.path.append(cleanDirectory)
    
from User_Input_Cleaning import process_user_input

input = "Does the article mention ** psychological first aid?"

corrected_input, relevant_output = process_user_input(input)

print(f"Corrected Input is {corrected_input}")


print(f"The Input: {corrected_input} is {relevant_output}")