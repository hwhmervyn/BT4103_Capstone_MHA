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

def stringEndsOnFullStop(text):
   trailingSpacesRmved = text.strip()
   if len(trailingSpacesRmved) == 0: return False
   else: return trailingSpacesRmved.strip()[-1] != '.'

def isDiffSection(prevSpanFontSize, fontSize, prevSpanFont, font):
  conditions = [
      prevSpanFontSize != fontSize,
      prevSpanFontSize == fontSize and prevSpanFont != font
  ]
  return sum(conditions) > 0

def aggregateSpansToSections(spans):
    sections = []

    prevSpan = spans[0]
    prevSectionText = [prevSpan['text']] #only concat text at the end of each section
    prevSpanFontSize = round(prevSpan['size'])
    prevSpanFont = prevSpan['font']
    section_num = 0

    for i in range(1, len(spans)):
      span = spans[i]
      spanText = span['text']
      fontSize = round(span['size'])
      font = span['font']
      
      if isDiffSection(prevSpanFontSize, fontSize, prevSpanFont, font):
        section_text = ' '.join(prevSectionText)#.replace('\n','')
        sections.append(section_text)
        section_num += 1

        prevSpan = span
        prevSectionText = [spanText]
        prevSpanFontSize =  fontSize
        prevSpanFont = font

      else:
        prevSectionText.append(spanText)

    section_text = ' '.join(prevSectionText)#.replace('\n','')
    sections.append(section_text)
    return sections