import statistics
import re 

# Removed Blank Pages (After Headers, Footers & References Removed)
def remove_empty_pages(span_lst):
    removed_pages = []
    new_span_lst = []
    if [] in span_lst:
        for page in range(0,len(span_lst)):
            if [] == span_lst[page]:
                removed_pages.append(page)
            else:
                new_span_lst.append(span_lst[page])

        return removed_pages, new_span_lst
    else:
        return removed_pages, span_lst

# Remove Tables (Tables have inconsistent font size/type with the rest of the text)
def remove_tables(span_lst):
    page_sizes = []
    span_sizes = []
    
    font_lst = []
    fonts_mode_lst = []
    
    # Gather the list of font size and type and the mode font size and type of each page
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

    # Mode font size and type of the entire article
    text_mode_size = statistics.mode(page_sizes)
    font_mode_type = statistics.mode(fonts_mode_lst)
    
    # Find percentage frequency of mode font size and type
    size_mode_pct = page_sizes.count(text_mode_size)/len(page_sizes)
    font_mode_pct = fonts_mode_lst.count(font_mode_type)/len(fonts_mode_lst)

    # print(f"{size_mode_pct},{font_mode_pct}")
    
    # Iterate through the pages
    for page in range(0,len(span_lst)):
        header_span = 0
        
        # Get mode font size of specific page
        if text_mode_size in span_sizes[page]:
            text_size = text_mode_size
        else:
            text_size = page_sizes[page]
            
        # Get mode font type of specific page
        if font_mode_type in font_lst[page]:
            font_mode = font_mode_type
        else:
            font_mode = fonts_mode_lst[page]

        # Start from top to bottom
        for span in range(0,len(span_sizes[page])):
            # Remove only if percentage frequency of mode font size exceed 0.65 & text does not match with the mode font size
            if span_sizes[page][span] < text_size and size_mode_pct > 0.65:
                header_span += 1
            # Consistent with texts (stop removal)
            else:
                break
                
        footer_span = None
        
        # Start from bottom to top
        for span in range(-1,-len(span_sizes[page]),-1):
            # Remove only if percentage frequency of mode font size exceed 0.65 & text font size does not match with the mode font size
            # OR
            # Remove only if percentage frequency of mode font type exceed 0.65 & text font type does not match with the mode font type
            if (span_sizes[page][span] != text_size and size_mode_pct > 0.65) or (font_lst[page][span] != font_mode and page != 0 and font_mode_pct>0.65) or re.sub(r'[0-9]','',span_lst[page][span]['text']).strip() == "Table":
                if page == 0 and span_sizes[page][span] == page_sizes[0]:
                    break
                footer_span = span
            # Consistent with texts (stop removal)
            else:
                break

        # Removal based on the index captured
        if footer_span == None:
            span_lst[page] = span_lst[page][header_span:]
        else:
            span_lst[page] = span_lst[page][header_span:footer_span:1]
    
    return span_lst

# Remove content in () & [] brackets & � characters
def remove_citations(sections):
    for section_index in range (0,len(sections)):
        section = re.sub("\(.*?\)","",sections[section_index][0])
        section = re.sub("\[.*?\]","",section)
        section = re.sub(r"[�]","",section)
        section = re.sub(r'\s+', ' ', section)
        sections[section_index][0] = section
    return sections

# Get Page number range of a section
def get_page_num(spansByPage, removed_pages):
    newSpansByPage = []
    page_num = 1
    for page in spansByPage:
        if (page_num - 1) in removed_pages:
            page_num += 1
        newSpansByPage.append((page, page_num))
        page_num += 1

    return newSpansByPage