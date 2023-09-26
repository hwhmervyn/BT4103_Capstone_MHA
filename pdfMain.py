from removeHeadersFooters import (
    remove_header_footer,
    find_header_spans, 
    find_footer_spans, 
    remove_header_footer_firstPage,
)

from removeTables import remove_tables, remove_empty_pages, remove_citations
from pdfUtils import getSpansByPage, keepFromTitle, removeSpecial
from pdfReferenceRMV import removeReference
from pdfSections import aggregateSpansToSections
import fitz

def pdfMain(uploaded_pdf, fileName):
    doc = fitz.open(stream=uploaded_pdf.read(), filetype="pdf")
    doc, pgNo = removeReference(doc, fileName)
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
        removed_pages, spansByPage = remove_empty_pages(spansByPage)
        spansByPage = remove_tables(spansByPage)
    else:
        removed_pages, spansByPage = remove_empty_pages(spansByPage)
        spansByPage = remove_tables(spansByPage)
        if len(spansByPage) >= 2:
            second_page_ref = remove_header_footer_firstPage(spansByPage[0],spansByPage[1])
            if second_page_ref != None:
                spansByPage[0] = second_page_ref
            elif len(spansByPage) >= 3:
                third_page_ref = remove_header_footer_firstPage(spansByPage[0],spansByPage[2])
                if third_page_ref != None:
                    spansByPage[0] = third_page_ref
    
    spans = [ span for pg in spansByPage for span in pg]
    spans = removeSpecial(spans)
    sections = aggregateSpansToSections(spans)
    sections = remove_citations(sections)
    
    return sections

# sections is still very buggy(in progress)
# sections = pdfMain(fileName="‘You’re Not Alone for China’_ The First Song in Times of COVID-19 to Keep the Faith in a World Crying in Silence.pdf")