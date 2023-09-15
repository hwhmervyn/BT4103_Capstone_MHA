import re
import fitz
fitz.TOOLS.set_small_glyph_heights(True)

def removeHypenAndJoin(listOfText):
  text = ' '.join(listOfText)
  pattern = '\s+-\s*|\s*-\s+'
  return re.sub(pattern, '', text.strip())

def isDiffSection(prevSpanFontSize, fontSize, prevSpanFont, font, prevSpanText, currentSpanText):
  conditions = [
      prevSpanFontSize != fontSize,
      prevSpanFontSize == fontSize and prevSpanFont != font
  ]
  return sum(conditions) > 0

def BaseAggregateSpansToSections(spans):
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

      if isDiffSection(prevSpanFontSize, fontSize, prevSpanFont, font, prevSectionText[-1], spanText):
        sections.append(prevSectionText)
        section_num += 1

        prevSpan = span
        prevSectionText = [spanText]
        prevSpanFontSize =  fontSize
        prevSpanFont = font

      else:
        prevSectionText.append(spanText)

    sections.append(prevSectionText)
    return sections

def joinIncompleteSections(sections):
    joinedSections = []
    numSections = len(sections)
    prevSection = sections[0]
    for i in range(1,numSections):
      nxtSec = sections[i]
      if prevSection[-1][-1] in (' ', ',', '-',"'", "‘","’",":","(", ")") or nxtSec[0][0] in (' ', ',', '-',"'","‘",".", "’", ":", "(", ")"):
        prevSection.extend(nxtSec)
      else:
        joinedSections.append(removeHypenAndJoin(prevSection))
        prevSection = nxtSec

    joinedSections.append(removeHypenAndJoin(prevSection))
    return joinedSections


def aggregateSpansToSections(spans):
  return joinIncompleteSections(BaseAggregateSpansToSections(spans))