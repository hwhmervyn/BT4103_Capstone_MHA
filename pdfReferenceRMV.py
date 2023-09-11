import fitz
from pdfUtils import find_Reference, remove_reference
from customExceptions import CannotFindReference

def removeReference(pdf_file_name):
    '''takes in a pdf file path and outputs a new pdf with reference removed. 
    Throws an exception if there is no reference detected'''
    try:
        doc = fitz.open(pdf_file_name)

        pgNo, _, reference_blks = find_Reference(doc)
        output_doc = remove_reference(doc, reference_blks, pgNo)

    except CannotFindReference as e:
        print(f"{e} -- output is just a copy of source")
        output_doc = (doc,None)
        
    if output_doc[1] == None or output_doc[1] + 1 == output_doc[0].page_count:
        pgNo = output_doc[0].page_count
    else:
        pgNo = output_doc[1] + 1

    doc = output_doc[0]

    return (doc, pgNo)
