import re 
import json
from json.decoder import JSONDecodeError


def fix_output(string):
	json_string = re.sub(r"(\{|\})", "", string)
	json_string = "{" + json_string + "}"
	return json_string

string = """{"answer": "Yes", "evidence": ["Psychological organizations engaged in preventive and mitigation efforts targeted, among others, the general public, local communities, and high-risk groups such as health care providers. They disseminated mental health information to the general public, trained laypersons to provide psychological first aid, and used research to design and evaluate public health responses to the pandemic.", "Professional organizations have organized their response to psychologists with information and training on effectively addressing mental health issues during the COVID-19 crisis. This has been done through the development of documents, virtual seminars, and panel discussions.", "Additionally, many resources have been dedicated to providing psychological services using online platforms."]"""


evidence = None
try:
	result_dict = json.loads(string)
	evidence = result_dict['evidence']
except JSONDecodeError:
	print('decode error')
	json_string = fix_output(string)
	try:
		result_dict = json.loads(json_string)
		evidence = result_dict['evidence']
	except Exception:
		evidence = string
except Exception:
	print('final')
	evidence = string


print(evidence)
