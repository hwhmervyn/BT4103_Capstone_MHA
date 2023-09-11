import statistics

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


def keepFromTitle(spans):
    largestFont = max(spans, key = lambda span: span['size'])['size']

    for i in range(len(spans)):
        span = spans[i]
        font = span['size']
        if font == largestFont:
            spans = spans[i:]
            break

    #print(f"removed {b4-len(block_font)} lines")
    return spans

# Remove Headers and Footers
def remove_header_footer(span_lst):
    for page in range(0,len(span_lst)):
        sizes = [span['size'] for span in span_lst[page]]
        text_size = statistics.mode(sizes)
        
        header_span = 0
        for span in sizes:
            if span < text_size:
                header_span += 1
            else:
                break
                
        footer_span = None
        for span in range(-1,-len(sizes),-1):
            if sizes[span]>text_size or sizes[span]<text_size:
                footer_span = span
            else:
                break

        if footer_span == None:
            span_lst[page] = span_lst[page][header_span:]
        else:
            span_lst[page] = span_lst[page][header_span:footer_span:1]
    
    return span_lst