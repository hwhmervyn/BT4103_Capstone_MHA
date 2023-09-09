import re
import fitz
from customExceptions import CannotFindReference


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


def remove_reference(og_doc, output_doc, reference_blks, pgNo):
    source_page = og_doc[pgNo]
    output_doc.delete_pages(from_page=pgNo, to_page=output_doc.page_count-1)

    _, _, pg_width, pg_height = source_page.rect

    copy_page = output_doc.new_page(
        pno=-1,
        width=pg_width,
        height=pg_height
    )
    for blk in reference_blks:
        rect = fitz.Rect(*blk[:4])
        source_page.add_redact_annot(rect)

    source_page.apply_redactions()
    copy_page.show_pdf_page(copy_page.rect, og_doc, pno=pgNo)
    return output_doc
