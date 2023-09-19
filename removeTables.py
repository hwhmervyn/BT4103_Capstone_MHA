import statistics
import re 

def remove_tables(span_lst):
    page_sizes = []
    span_sizes = []
    
    font_lst = []
    fonts_mode_lst = []
    
    for page in range(0,len(span_lst)):
        sizes = []
        fonts = []
        for span in span_lst[page]:
            sizes.append(span['size'])
            fonts.append(span['font'])
            
        
        text_size = statistics.mode(sizes)
        font_mode_page = statistics.mode(fonts)
        
        page_sizes.append(text_size)
        span_sizes.append(sizes)
        font_lst.append(fonts)
        fonts_mode_lst.append(font_mode_page)

    
    text_mode_size = statistics.mode(page_sizes)
    font_mode_type = statistics.mode(fonts_mode_lst)
    
    size_mode_pct = page_sizes.count(text_mode_size)/len(page_sizes)
    font_mode_pct = fonts_mode_lst.count(font_mode_type)/len(fonts_mode_lst)

    print(f"{size_mode_pct},{font_mode_pct}")
    
    for page in range(0,len(span_lst)):
        header_span = 0

        if text_mode_size in span_sizes[page]:
            text_size = text_mode_size
        else:
            text_size = page_sizes[page]

        if font_mode_type in font_lst[page]:
            font_mode = font_mode_type
        else:
            font_mode = fonts_mode_lst[page]

        for span in range(0,len(span_sizes[page])):
            if span_sizes[page][span] < text_size and size_mode_pct > 0.65:
                header_span += 1
            else:
                break
                
        footer_span = None
        
        for span in range(-1,-len(span_sizes[page]),-1):
            if (span_sizes[page][span] != text_size and size_mode_pct > 0.65) or (font_lst[page][span] != font_mode and page != 0 and font_mode_pct>0.65) or re.sub(r'[0-9]','',span_lst[page][span]['text']).strip() == "Table":
                if page == 0 and span_sizes[page][span] == page_sizes[0]:
                    break
                footer_span = span
            else:
                break


        if footer_span == None:
            span_lst[page] = span_lst[page][header_span:]
        else:
            span_lst[page] = span_lst[page][header_span:footer_span:1]
    
    return span_lst