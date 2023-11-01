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
  # Base logic that identifies and groups spans into sections
  sections = []

  prevSpan = spans[0][0]
  prevSectionText = [prevSpan['text']] # only concat text at the end of each section as string concat is O(N) time
  # Round the font size as PyMuPDF reads in documents in the form of images. Hence there is some discrepancies in the size attribute. The size attribute comes close to the actual but needs rounding, otherwise it will be diffcult to make any comparison with other spans
  prevSpanFontSize = round(prevSpan['size'])
  prevSpanFont = prevSpan['font']
  section_num = 0
  prevPage = [spans[0][1]]

  for i in range(1, len(spans)):
    span = spans[i][0]
    spanText = span['text']
    fontSize = round(span['size'])
    font = span['font']

    # Span is not from the current section. Terminate the growth of current section and begin building the next section.
    if isDiffSection(prevSpanFontSize, fontSize, prevSpanFont, font, prevSectionText[-1], spanText):
      sections.append((prevSectionText,prevPage))
      section_num += 1

      prevSpan = span
      prevSectionText = [spanText]
      prevSpanFontSize =  fontSize
      prevSpanFont = font
      prevPage = [spans[i][1]]

    # Span still continues from the current section hence we append it to the growing section
    else:
      prevSectionText.append(spanText)
      if spans[i][1] not in prevPage:
        prevPage.append(spans[i][1]) 

  sections.append((prevSectionText,prevPage))
  return sections

# Account for incomplete aggregation of sections due to special characters (Different font size/type from the rest of the text)
# Incomplete sections can also be identified by trailing spaces before or after it.
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