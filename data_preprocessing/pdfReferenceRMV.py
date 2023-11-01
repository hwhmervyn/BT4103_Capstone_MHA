import fitz

import sys, os
workingDirectory = os.getcwd()
preProcessingDirectory = os.path.join(workingDirectory, "data_preprocessing")
sys.path.append(preProcessingDirectory)

from pdfUtils import find_Reference, remove_reference
from customExceptions import CannotFindReference

def removeReference(doc, fileName):
    '''takes in a pdf file path and outputs a new pdf with reference removed. 
    Throws an exception if there is no reference detected'''
    try:
        pgNo, _, reference_blks = find_Reference(doc)
        output_doc = remove_reference(doc, reference_blks, pgNo)

    # Raises an error, prints out the file path, and terminates the function when no reference is found.
    except CannotFindReference as e:
        print(f"{e} -- {fileName} output is just a copy of source")
        output_doc = (doc,None)
    
    # If reference was found and removed, any blank pages remaining at the back of the document are also deleted.
    if output_doc[1] == None or output_doc[1] + 1 == output_doc[0].page_count:
        pgNo = output_doc[0].page_count
    else:
        pgNo = output_doc[1] + 1

    doc = output_doc[0]

    return (doc, pgNo)