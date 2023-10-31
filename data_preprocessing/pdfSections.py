import re
import fitz
fitz.TOOLS.set_small_glyph_heights(True)

# Remove hyphen Rejoin hyphenated words
def removeHypenAndJoin(listOfText):
  text = ' '.join(listOfText)
  pattern = '\s+-\s*|\s*-\s+'
  return re.sub(pattern, '', text.strip())

# Differentiate sections (Section headers have a different font size/type from the rest of the text)
def isDiffSection(prevSpanFontSize, fontSize, prevSpanFont, font, prevSpanText, currentSpanText):
  conditions = [
      prevSpanFontSize != fontSize,
      prevSpanFontSize == fontSize and prevSpanFont != font
  ]
  return sum(conditions) > 0

def BaseAggregateSpansToSections(spans):
  sections = []

  prevSpan = spans[0][0]
  prevSectionText = [prevSpan['text']] #only concat text at the end of each section
  prevSpanFontSize = round(prevSpan['size'])
  prevSpanFont = prevSpan['font']
  section_num = 0
  prevPage = [spans[0][1]]

  for i in range(1, len(spans)):
    span = spans[i][0]
    spanText = span['text']
    fontSize = round(span['size'])
    font = span['font']

    # Seperate different sections
    if isDiffSection(prevSpanFontSize, fontSize, prevSpanFont, font, prevSectionText[-1], spanText):
      sections.append((prevSectionText,prevPage))
      section_num += 1

      prevSpan = span
      prevSectionText = [spanText]
      prevSpanFontSize =  fontSize
      prevSpanFont = font
      prevPage = [spans[i][1]]

    else:
      prevSectionText.append(spanText)
      if spans[i][1] not in prevPage:
        prevPage.append(spans[i][1]) 

  sections.append((prevSectionText,prevPage))
  return sections

# Account for incorrect splitting of sections due to special characters (Different font size/type from the rest of the text)
def joinIncompleteSections(sections):
  joinedSections = []
  numSections = len(sections)
  prevSection = sections[0][0]
  spec_char = "[@_#$%^&*<>}{~:]�•·"
  prevPage = [sections[0][1][0],sections[0][1][-1]]
  for i in range(1,numSections):
    nxtSec = sections[i][0]
    nxtPage = [sections[i][1][0],sections[i][1][-1]]
    if prevSection[-1][-1] in (' ', ',', '-',"'", "‘","’",":","(", ")","—","–","–","−",'“','”',"…") or nxtSec[0][0] in (' ', ',', '-',"'","‘",".", "’", ":", "(", ")","—","–","–","−",'“','”',"…"):
      prevSection.extend(nxtSec)
      if prevPage[1] < nxtPage[1]:
        prevPage[1] = nxtPage[1]
    elif prevSection[-1][-1] in spec_char or nxtSec[0][0] in spec_char:
      prevSection.extend(nxtSec)
      if prevPage[1] < nxtPage[1]:
        prevPage[1] = nxtPage[1]
    else:
      joinedSections.append([removeHypenAndJoin(prevSection),prevPage])
      prevSection = nxtSec
      prevPage = nxtPage

  joinedSections.append([removeHypenAndJoin(prevSection),prevPage])
  return joinedSections

# Aggregate all the helper methods above (Split Sections)
def aggregateSpansToSections(spans):
  return joinIncompleteSections(BaseAggregateSpansToSections(spans))