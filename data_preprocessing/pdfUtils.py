import re
import fitz

import sys, os
workingDirectory = os.getcwd()
preProcessingDirectory = os.path.join(workingDirectory, "data_preprocessing")
sys.path.append(preProcessingDirectory)

from customExceptions import CannotFindReference

# Function that takes in a list of ordered pages. Each page is represented as a nested list containing an ordered sequence of blocks that make up the page.
# The function tries to map each block into spans which providing access to text attributes. It then outputs back the list of output pages, with each page 
# now represented as a nested list of spans.
def getSpansByPage(listOfBlockByPage, excludeNonText=True):
  spansByPage = []
  for page in listOfBlockByPage:
    spans = []
    for blk in page:
      if excludeNonText:
        if blk['type'] != 0 or len(blk['lines']) == 0: continue
      spans.extend([span for line in blk['lines'] for span in line['spans']]) # Each PyMuPDF Block is made of lines. And each line is made up of Spans. Hence we need to unnest

    spansByPage.append(spans)
  return spansByPage

# Helper function that that takes in a page respresented as a list of blocks and checks whether Reference Header is present in it.
def get_block_with_reference_heading(page_blocks):
    # REGEX MATCHING
    # \b is used to ensure that "reference" or "references" is a whole word and not part of another word.
    # Filter the page_blocks list to find blocks that match the pattern
    pattern = re.compile(r'\breferences?\b', re.IGNORECASE)
    results = list(filter(lambda blk: pattern.findall(blk[4]), page_blocks))
    # If there is exactly one matching block, return that block
    if len(results) == 1:
        return results[0]
    
    # If there are multiple blocks, Filter the results to find blocks with a single word in their content
    single_word_results = list(
        filter(lambda x: len(x[4].split(' ')) == 1, results))

    # If there is exactly one matching block with a single word after the post filtering, return that block
    if len(single_word_results) == 1:
        return single_word_results[0]

    # If there are still multiple blocks, raise an error
    elif len(single_word_results) > 1:
        raise Exception("found more than one block of reference")
    
    # Else it means no blocks were found. This page is assumed to not contain References and we return None
    else:
        return None

# Takes in a pymupdf doc object and tries to locate the Page and Block Number of the reference header among all the pages 
def find_Reference(doc):
    '''returns a tuple of (pNo, text-page, reference-block(s))'''
    last_pg_index = doc.page_count - 1
    for i in range(last_pg_index, 0, -1): # Loops through the pages from the last page
        text_pg = doc[i].get_textpage()
        page_blocks = text_pg.extractBLOCKS()
        blk = get_block_with_reference_heading(page_blocks)
        if blk != None:
            blk_no = blk[-2]
            reference_blks = page_blocks[blk_no:]
            return (i, text_pg, reference_blks)
    raise CannotFindReference('Warning: No Reference Found')

# Takes in a pymupdf doc, and the location of the reference(found using find_Reference) and deletes the reference from the doc permanently
def remove_reference(og_doc, reference_blks, pgNo):
    source_page = og_doc[pgNo]

    for blk in reference_blks:
        rect = fitz.Rect(*blk[:4])
        source_page.add_redact_annot(rect)

    source_page.apply_redactions() # deletes the reference permanently.


    return (og_doc,pgNo)

# Function that takes in a list of ordered pages. Each page is represented as a nested list containing an ordered sequence
# of spans that make up the page. The function tries to exclude texts before the title by idenitfying the span with the largest font
# and throwing the spans that comes before it.
def keepFromTitle(spansByPage):
    pageOne = spansByPage[0]

    largestFont = max(pageOne, key = lambda span: span['size'])['size']

    for i in range(len(pageOne)):
        span = pageOne[i]
        font = span['size']
        if font == largestFont:
            pageOne = pageOne[i:]
            break
        
    spansByPage[0] = pageOne
    #print(f"removed {b4-len(block_font)} lines")
    return spansByPage

# removes superscripts from text by using PyMuPDF's flags attribute
def removeSpecial(spans):
  notSuperScript = lambda s: not (s[0]['flags'] & 2 ** 0)
  return list(filter(notSuperScript, spans))