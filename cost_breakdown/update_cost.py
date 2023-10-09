import csv
import pytz
import datetime as dt
from enum import Enum

class Stage(Enum):
    EXCEL_FILTERING = "Excel Filtering"
    SUPPORT_ANALYSIS = "Support Analysis"
    PDF_FILTERING = "PDF Filtering"
    INDIVIDUAL_ANALYSIS = "Individual Analysis"


singapore = pytz.timezone('Asia/Singapore')

def update_usage_logs(processing_stage, query, total_input_tokens, total_output_tokens, total_cost):
    with open('cost_breakdown/API Cost.csv','a',newline="") as f_object:
        writer = csv.writer(f_object)
        writer.writerow([str(dt.datetime.now()), processing_stage, query, total_input_tokens, total_output_tokens, total_cost])
        f_object.close()
        
        
# WARNING! This deletes the rows in the .csv file
def clear_logs():
    f =  open('cost_breakdown/API Cost.csv','w')
    f.truncate()
    f.close()
    with open('cost_breakdown/API Cost.csv','a',newline="") as f_object:
        writer = csv.writer(f_object)
        writer.writerow(["Date","Processing Stage", "Query", "Total Input Tokens", "Total Output Tokens", "Total Cost"])
        f_object.close()
        