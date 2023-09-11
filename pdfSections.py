import fitz
fitz.TOOLS.set_small_glyph_heights(True)


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

def aggregateSpansToSections(spans):
    sections = []

    prevSpan = spans[0]
    prevSpanText = [prevSpan['text']] #only concat text at the end of each section
    prevSpanFontSize = round(prevSpan['size'])
    prevSpanFont = prevSpan['font']
    section_num = 0

    for i in range(1, len(spans)):
      span = spans[i]
      spanText = span['text']
      fontSize = round(span['size'])
      font = span['font']

      if prevSpanFontSize != fontSize or (prevSpanFontSize == fontSize and prevSpanFont != font and '.' != prevSpanText[-1].strip()):
        section_text = ' '.join(prevSpanText)#.replace('\n','')
        sections.append(section_text)
        section_num += 1

        prevSpan = span
        prevSpanText = [spanText]
        prevSpanFontSize =  fontSize
        prevSpanFont = font

      else:
        prevSpanText.append(spanText)

    section_text = ' '.join(prevSpanText)#.replace('\n','')
    sections.append(section_text)
    return sections