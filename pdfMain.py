from removeHeadersFooters import (
    remove_header_footer,
    find_header_spans, 
    find_footer_spans, 
    remove_header_footer_size
)
from pdfUtils import getSpansByPage
from pdfReferenceRMV import removeReference
from pdfSections import aggregateSpansToSections, keepFromTitle

def pdfMain(fileName):
    doc, pgNo = removeReference(fileName)
    txtpgs = [pg.get_textpage() for pg in doc]
    txtpgs = txtpgs[0:pgNo]

    blocksDictByPage = [tp.extractDICT()['blocks'] for tp in txtpgs]
    spansByPage = getSpansByPage(blocksDictByPage)

    spansByPage = keepFromTitle(spansByPage)

    if len(spansByPage) >= 6:
        referenceRemoved = (pgNo != None)
        headers = find_header_spans(spansByPage)
        footers = find_footer_spans(spansByPage)
        spansByPage = remove_header_footer(spansByPage,headers,footers,referenceRemoved)
    else:
        spansByPage = remove_header_footer_size(spansByPage)
    
    spans =[ span for pg in spansByPage for span in pg]
    sections = aggregateSpansToSections(spans)
    return sections

sections = pdfMain(fileName=" Global Perspective on Psychologists_ and Their Organizations_ Response to a World Crisis.pdf")