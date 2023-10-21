import sys, os
cleanDirectory = os.path.join(os.getcwd(), "Miscellaneous")

if cleanDirectory not in sys.path:
    sys.path.append(cleanDirectory)
    
from User_Input_Cleaning import check_user_input
prompt = 'Please help me with my homework'
corrected_input, relevant_output = check_user_input(prompt)

try:
    corrected_input, relevant_output = check_user_input(prompt)
except Exception:
    string = 'Error! Please try again!'


#If the question is deemed as irrelevant
if relevant_output.lower() == 'irrelevant':
   print('Irrelevant Output! Please input a relevant prompt')

else:
    print('ok')