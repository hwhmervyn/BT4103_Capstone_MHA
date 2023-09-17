def remove_tables(span_lst):
    for page in range(0,len(span_lst)):
        sizes = [span['size'] for span in span_lst[page]]
        text_size = statistics.mode(sizes)
        
        header_span = 0
        for span in range(0,len(sizes)):
            if sizes[span] < text_size:
                header_span += 1
            else:
                break
                
        footer_span = None
        
        for span in range(-1,-len(sizes),-1):
            if sizes[span] != text_size:
                footer_span = span
            else:
                break


        if footer_span == None:
            span_lst[page] = span_lst[page][header_span:]
        else:
            span_lst[page] = span_lst[page][header_span:footer_span:1]
    
    return span_lst