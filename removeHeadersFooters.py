import statistics
import re

def find_header_spans(span_lst):
    dict_header_spans = {}
    # Split between even & odd pages
    for page in [1,2]:
        spans = []
        for span in range(0,len(span_lst[page])):
            try:
                is_similar = (re.sub(r'[0-9]','',span_lst[page][span]['text']).strip() == re.sub(r'[0-9]','',span_lst[page+2][span]['text']).strip())
                if is_similar:
                    spans.append(span)
                else:
                    if page == 2:
                        dict_header_spans['Odd'] = spans
                    else:
                        dict_header_spans['Even'] = spans
                    break
            except IndexError as e:
                print(e)
    return dict_header_spans



# Find the index of blocks that are Footers
def find_footer_spans(span_lst):
    dict_footer_spans = {}
    for page in [1,2]:
        spans = []
        for span in range(-1,-len(span_lst[page]),-1):
            try:
                is_similar = (re.sub(r'[0-9]','',span_lst[page][span]['text']).strip() == re.sub(r'[0-9]','',span_lst[page+2][span]['text']).strip())
                if is_similar:
                    spans.append(span)
                else:
                    if page == 2:
                        dict_footer_spans['Odd'] = spans
                    else:
                        dict_footer_spans['Even'] = spans
                    break
            except IndexError as e:
                print(e)
    
    return dict_footer_spans


def remove_header_helper(span_lst,headers,page,oddEven):
    if len(headers[oddEven]) != 0:
        return span_lst[page][headers[oddEven][-1]+1:]
    else:
        return span_lst[page]

def remove_footer_helper(span_lst,footers,page,oddEven):
    if len(footers[oddEven]) != 0:
        return span_lst[page][0:footers[oddEven][-1]:1]
    else:
        return span_lst[page]

def remove_header_footer_firstPage(firstPage,secondPage):
    left_border = min([span['bbox'][0] for span in secondPage])
    right_border = max([span['bbox'][2] for span in secondPage])
    bottom_border = max([span['bbox'][3] for span in secondPage])
    top_border = firstPage[0]['bbox'][1]

    for span in range(-1,-len(firstPage),-1):
        bbox = firstPage[span]['bbox']
        if bbox[2] < left_border or bbox[0] > right_border or bbox[1] > bottom_border or bbox[3] < top_border:
            continue
        else:
            if span == -1:
                return firstPage
            else:
                return firstPage[0:span+1:1] 
        

# Remove Headers and Footers
def remove_header_footer(span_lst,headers,footers,referenceRemoved):
    for page in range(1, len(span_lst)):
        if page == len(span_lst) - 1 and referenceRemoved:
            if page % 2 == 0:
                span_lst[page] = remove_header_helper(span_lst,headers,page,'Odd')
            else:
                span_lst[page] = remove_header_helper(span_lst,headers,page,'Even')
        else:
            if page % 2 == 0:
                span_lst[page] = remove_header_helper(span_lst,headers,page,'Odd')
                span_lst[page] = remove_footer_helper(span_lst,footers,page,'Odd')
            else:
                span_lst[page] = remove_header_helper(span_lst,headers,page,'Even')
                span_lst[page] = remove_footer_helper(span_lst,footers,page,'Even')

    second_page_ref = remove_header_footer_firstPage(span_lst[0],span_lst[1])
    third_page_ref = None
        

    if second_page_ref != None:
        span_lst[0] = second_page_ref
    elif len(span_lst) >= 3:
        third_page_ref = remove_header_footer_firstPage(span_lst[0],span_lst[2])
        if third_page_ref != None:
            span_lst[0] = third_page_ref
        

    return span_lst




              




