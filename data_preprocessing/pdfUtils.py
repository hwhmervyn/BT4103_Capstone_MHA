import re
import fitz

import sys, os
workingDirectory = os.getcwd()
preProcessingDirectory = os.path.join(workingDirectory, "data_preprocessing")
sys.path.append(preProcessingDirectory)

from customExceptions import CannotFindReference

def getSpansByPage(listOfBlockByPage, excludeNonText=True):
  spansByPage = []
  for page in listOfBlockByPage:
    spans = []
    for blk in page:
      if excludeNonText:
        if blk['type'] != 0 or len(blk['lines']) == 0: continue
      spans.extend([span for line in blk['lines'] for span in line['spans']])

    spansByPage.append(spans)
  return spansByPage


def get_block_with_reference_heading(page_blocks):
    pattern = re.compile(r'\breferences?\b', re.IGNORECASE)
    results = list(filter(lambda blk: pattern.findall(blk[4]), page_blocks))
    if len(results) == 1:
        return results[0]

    single_word_results = list(
        filter(lambda x: len(x[4].split(' ')) == 1, results))

    if len(single_word_results) == 1:
        return single_word_results[0]

    elif len(single_word_results) > 1:
        raise Exception("found more than one block of reference")
    else:
        return None


def find_Reference(doc):
    '''returns a tuple of (pNo, text-page, reference-block(s))'''
    last_pg_index = doc.page_count - 1
    for i in range(last_pg_index, 0, -1):
        text_pg = doc[i].get_textpage()
        page_blocks = text_pg.extractBLOCKS()
        blk = get_block_with_reference_heading(page_blocks)
        if blk != None:
            blk_no = blk[-2]
            reference_blks = page_blocks[blk_no:]
            return (i, text_pg, reference_blks)
    raise CannotFindReference('Warning: No Reference Found')


def remove_reference(og_doc, reference_blks, pgNo):
    source_page = og_doc[pgNo]

    for blk in reference_blks:
        rect = fitz.Rect(*blk[:4])
        source_page.add_redact_annot(rect)

    source_page.apply_redactions()


    return (og_doc,pgNo)

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

def removeSpecial(spans):
  notSuperScript = lambda s: not (s[0]['flags'] & 2 ** 0)
  return list(filter(notSuperScript, spans))