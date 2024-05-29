import re
import SenateSQLDB
import fitz
from io import BytesIO
import sys
import os
import commonphraseregexcheck
import ngramlineevaluate
import spellcheck

import ProcessPDFFile

from spellchecker import SpellChecker

spell = SpellChecker()
spell.word_frequency.load_text_file('./words_yes_ispell_no_pyspell.txt')

hyphenatedwords = []


def loadhyphenatedwords():
    with open("./hyphenated_words.txt") as f:
        for line in f:
            line = line.strip()
            if len(line) == 0:
                continue
            else:
                hyphenatedwords.append(line)


def IsWordCorrectlySpelled(word2check):
    # Check against list of legal hyphenated words
    if word2check in hyphenatedwords:
        return True

    # # If it's a hyphenated word, check in list of legit hyphenated words
    # if word2check in hyphenatedwords:
    #     return True

    # If it's a time, it's considered spelled correctly
    if re.match("[p|a]\.m\.,?", word2check):
        return True

    # If it's an ordinal, it's considered spelled correctly
    if re.match("\d{1,5}[st|nd|rd|th],?", word2check):
        return True

    # If it's a number, it's considered spelled correctly
    if re.match("\d", word2check):
        word2check = re.sub(r'[^\w\d]', '', word2check)
        if word2check.isnumeric():
            return True

    word2check = re.sub(r'[^\w\'\-]', '', word2check)

    return spell[word2check]


def highlight_pdffile(pdffilelines):
    for info in pdffilelines:
        page2update = int(info["pdfpage"])
        line2update = int(info["pdfline"]) - 1
        text2update = info["pdftext"]

        if text2update == "Response of Aye.":
            i = 10;

        # Hack 032724
        page2update -= 1

        # Search for text
        page = pdfDoc[page2update]

        # Get pa:ge lines
        page_lines = page.get_text("text").split('\n')

        # Get rectangles for each line
        line_rects = []

        # Substring search
        needle = page_lines[line2update]

        cliprect = page.search_for(needle)

        # the_rect = page.search_for(text2update)
        try:
            the_rect = page.search_for(text2update, clip=cliprect[0])
        except:
            print("Fail on page.search_for '{0}'".format(text2update))

        # highlight = page.add_squiggly_annot(the_rect)
        highlight = page.add_highlight_annot(the_rect)

        highlight.update()
    # out = open("output.txt", "wb")  # create a text output
    # for page in doc:  # iterate the document pages
    #     text = page.get_text().encode("utf8")  # get plain text (is in UTF-8)
    #     out.write(text)  # write text of page
    #     out.write(bytes((12,)))  # write page delimiter (form feed 0x0C)
    # out.close()
    # Save to output
    pdfDoc.save(output_buffer)
    pdfDoc.close()
    # Save the output buffer to the output file
    with open("2024-05-16_highlighted.pdf", mode='wb') as f:
        f.write(output_buffer.getbuffer())


def loadsenateregexes():
    lines = []
    with open('senate_regexes.txt') as file:
        for line in file:
            line = line.strip()
            lines.append(line)

    return lines


def senatewordsnotinspellchecker():
    p1 = SenateSQLDB.SenateWords()

    f = open("words_not_in_pyspell.txt", "w")

    uniquewords = p1.get_words()

    for word in uniquewords:
        if not IsWordCorrectlySpelled(word['token']):
            f.write("{0}\n".format(word['token']))

    f.close()


def loadsenatorregexes():
    returnlines = []

    filelines = []
    with open('senator_regexes.txt') as file:
        for fileline in file:
            fileline = fileline.strip()
            filelines.append(fileline)

    # Go senator and create a series of regexes for that name
    p1 = SenateSQLDB.SenateSpeakers()
    senatornames = p1.get_speakers()
    senatorlastnames = []

    for senatorlistname in senatornames:
        # Remove "SENATOR " from string
        senatornametext = senatorlistname['speakername'].replace("SENATOR ", "").lower().title()
        senatorlastnames.append(senatornametext)

    for fileline in filelines:
        for senatorlastname in senatorlastnames:
            returnlines.append(fileline.format(senatorlastname))

    return returnlines


filename2process = ""


def isContractionLegitimate(spelledword, contractions):
    wordparts = spelledword.split("'")

    # print(wordparts)
    word = wordparts[0]
    contraction = wordparts[1]

    returnval = False

    if contraction in contractions:
        if IsWordCorrectlySpelled(word) or \
                word in counties or \
                word in cities or \
                word in firstnames or \
                word in lastnames or \
                word in senatornames or \
                word in months or \
                word in days:
            returnval = True

    return returnval


def getnewname(transcriptlinein):

    # Break the full transcript line into words
    linewords = transcriptlinein["text"].split(" ")

    # Break the pdf lines into words/pages/lines
    pdflines = pdf1.get_pdflines(transcriptlinein["id"])

    # For each pdf line, break it into words and create a dict object for each
    # word indicating the page and line that word is on
    pdflinewordslist = []

    linewordindex = 0
    ordinal = 0

    for pdfline in pdflines:

        page = pdfline['pdfpage']
        line = pdfline['pdfline']

        # Split the line by words
        pdflinewords = pdfline["pdftext"].split(" ")

        # Match linewords against pdflinewords
        for pdflineword in pdflinewords:

            if pdflineword == linewords[linewordindex]:
                pdflinewordslist.append({'pdfpage': pdfline["pdfpage"],
                                         'pdfline': pdfline["pdfline"],
                                         'ordinal': ordinal,
                                         'pdfword': pdflineword,
                                         'toggle': False})
                linewordindex += 1
                ordinal += 1


    pdflineindex = 0


    return pdflinewordslist


def getwordpositionrangesofsubstringsinstring(largerstring, substrings):

    returnlist = []

    largerstringwords = largerstring.split(" ")

    pointer = 0

    for substring in substrings:

        substringwords = substring.split(" ")

        start = pointer
        stop = len(largerstringwords) - len(substringwords)

        for x in range(start, stop):
            if largerstringwords[x:x+len(substringwords)] == substringwords:
                returnlist.append({'start': x, 'end': len(substringwords) + x})
                pointer = x
                break

    return returnlist

def markupindividualwords(markupranges, words):

    for markuprange in markupranges:

        for x in range(markuprange['start'], markuprange['end']):
            words[x]['toggle'] = True


def preprocessmarkeduplines(markeduplines):

    for markedupline in markeduplines:

        # Pull out the phrases in the text to be underlined
        phrases2underline = re.findall(r"<x>(.*?)</x>", markedupline['markeduptext'])

        # Create a temporary unmarked-up version of the line to use in finding starting positions of
        # phrases to underline
        unmarkedupline = markedupline['markeduptext'].replace("<x>","")
        unmarkedupline = unmarkedupline.replace("</x>","")
        markupranges = getwordpositionrangesofsubstringsinstring(unmarkedupline, phrases2underline)

        # Transfer markup of sentence to markup of individual words
        markupindividualwords(markupranges, markedupline['pdfindexedtext'])

        # For each individual text chunk to be underlined
        # for phrase2underline in phrases2underline:

            # Get starting position of the phrase to underline in actual line


            # # Break the chunk into words
            # phrasewords = phrase2underline.split(" ")
            #
            # # Walk through the dicts of pdf info for each word of transcriptline
            # pdflinewordindex = 0
            # toggle = False
            #
            #         if phraseword == pdflinewords[pdflinewordindex]['pdfword']:
            #             pdflinewords[pdflinewordindex]['toggle'] = True
            #             break

        # markedupline['pdfindexedtext'] = pdflinewords

def convertmarkeduplinestodirectives(markeduplines):

    pagedirectives = []
    annotatedpdftext = ""

    for markedupline in markeduplines:

        firstflag = True
        annotatedpdftext = ""

        # Loop through every word in pdfindexed text for the line
        for pdftext in markedupline['pdfindexedtext']:

            currentpdfpage = pdftext["pdfpage"]
            currentpdfline = pdftext["pdfline"]
            currentpdfword = pdftext["pdfword"]
            currenttoggle = pdftext["toggle"]

            if currentpdfpage == 3 and currentpdfline == 7:
                i = 10

            if firstflag:

                if currenttoggle:
                    annotatedpdftext = currentpdfword

                previouspdfpage = currentpdfpage
                previouspdfline = currentpdfline
                previouspdfword = currentpdfword
                previoustoggle = currenttoggle

                firstflag = False

                continue

            else:

                # If page has incremented and there is something in the accumulator, write the accumulator to
                # pagedirectives

                if currentpdfpage > previouspdfpage:
                    if len(annotatedpdftext) > 0:
                        pagedirectives.append({'pdfpage': previouspdfpage, 'pdfline': previouspdfline,
                                               'pdftext': annotatedpdftext.strip(),
                                               'highlighttype': "NoTrigramMatch"})

                    if currenttoggle:
                        annotatedpdftext = currentpdfword
                    else:
                        annotatedpdftext = ''

                    previouspdfline = currentpdfline
                    previouspdfword = currentpdfword
                    previouspdfpage = currentpdfpage
                    previoustoggle = currenttoggle

                    continue

            # If line has incremented and there is something in the accumulator, write the accumulator to
            # pagedirectives
            if currentpdfline > previouspdfline:
                if len(annotatedpdftext) > 0:
                    pagedirectives.append({'pdfpage': previouspdfpage, 'pdfline': previouspdfline,
                                           'pdftext': annotatedpdftext.strip(),
                                           'highlighttype': "NoTrigramMatch"})
                    if currenttoggle:
                        annotatedpdftext = currentpdfword
                    else:
                        annotatedpdftext = ''

                    previouspdfline = currentpdfline
                    previouspdfword = currentpdfword
                    previouspdfpage = currentpdfpage
                    previoustoggle = currenttoggle

                    continue

                if currenttoggle:
                    annotatedpdftext = annotatedpdftext + " " + currentpdfword

                previouspdfline = currentpdfline
                previouspdfword = currentpdfword
                previouspdfpage = currentpdfpage
                previoustoggle = currenttoggle


            # If toggle "true", add word to accumulator, else if there's anything in the accumulator add
            # it to the list of directives
            if currenttoggle:
                annotatedpdftext += " " + currentpdfword + " "

                previouspdfline = currentpdfline
                previouspdfword = currentpdfword
                previouspdfpage = currentpdfpage
                previoustoggle = currenttoggle

            else:
                if len(annotatedpdftext) > 0:
                    pagedirectives.append({'pdfpage': currentpdfpage, 'pdfline': currentpdfline,
                                           'pdftext': annotatedpdftext.strip(),
                                           'highlighttype': "NoTrigramMatch"})

                    annotatedpdftext = ""

                previouspdfline = currentpdfline
                previouspdfword = currentpdfword
                previouspdfpage = currentpdfpage
                previoustoggle = currenttoggle

        # Add the final chunk if it exists
        if len(annotatedpdftext) > 0:
            pagedirectives.append({'pdfpage': currentpdfpage, 'pdfline': currentpdfline,
                                   'pdftext': annotatedpdftext.strip(),
                                   'highlighttype': "NoTrigramMatch"})
            previouspdfline = currentpdfline
            previouspdfword = currentpdfword
            previouspdfpage = currentpdfpage
            previoustoggle = currenttoggle

    return pagedirectives

def convertcommonphraselinestodirectives(markeduplines):

    pagedirectives = []

    for markedupline in markeduplines:

        firstflag = True

        # Loop through every word in pdfindexed text for the line
        for pdfword in markedupline['pdfindexedtext']:

            currentpdfpage = pdfword["pdfpage"]
            currentpdfline = pdfword["pdfline"]
            currentpdfword = pdfword["pdfword"]

            if firstflag:

                annotatedpdftext = currentpdfword

                previouspdfpage = currentpdfpage
                previouspdfline = currentpdfline
                previouspdfword = currentpdfword

                firstflag = False

            else:

                # If page has incremented and there is something in the accumulator, write the accumulator to
                # pagedirectives

                if currentpdfpage > previouspdfpage:
                    if len(annotatedpdftext) > 0:
                        pagedirectives.append({'pdfpage': previouspdfpage, 'pdfline': previouspdfline,
                                               'pdftext': annotatedpdftext.strip(),
                                               'highlighttype': "CommonPhrase"})
                        annotatedpdftext = ""

                        previouspdfline = currentpdfline
                        previouspdfword = currentpdfword
                        previouspdfpage = currentpdfpage

                        continue

                # If line has incremented and there is something in the accumulator, write the accumulator to
                # pagedirectives

                if currentpdfline > previouspdfline:
                    if len(annotatedpdftext) > 0:
                        pagedirectives.append({'pdfpage': previouspdfpage, 'pdfline': previouspdfline,
                                               'pdftext': annotatedpdftext.strip(),
                                               'highlighttype': "CommonPhrase"})

                        annotatedpdftext = currentpdfword

                        previouspdfline = currentpdfline
                        previouspdfword = currentpdfword
                        previouspdfpage = currentpdfpage

                        continue

                annotatedpdftext = annotatedpdftext + " " + currentpdfword
                previouspdfline = currentpdfline
                previouspdfword = currentpdfword
                previouspdfpage = currentpdfpage

        # Add the final chunk if it exists
        if len(annotatedpdftext) > 0:
            pagedirectives.append({'pdfpage': currentpdfpage, 'pdfline': currentpdfline,
                                   'pdftext': annotatedpdftext.strip(),
                                   'highlighttype': "CommonPhrase"})

    return pagedirectives



def diagnostic():

    filename2process = "2024-05-21.pdf"
    pdfDoc = fitz.open(filename2process)  # open a document


    markeduplines = []
    commonphraselines = []

    # Pull all transcriptlines for the date
    transcriptlines = sql1.select_all("select id, speaker, page, line, text from transcriptlines "
                                      "where date = '2024-05-21' limit 50")
                                      # "where id = 2086656")

    q1 = commonphraseregexcheck.DetermineCommonPhrases()
    # commonphraselines = q1.getcommonphrasetranscriptlines(transcriptlines)

    # directives = convertcommonphraselinestodirectives(commonphraselines)

    for transcriptline in transcriptlines:

        # Diagnostic
        print(transcriptline["text"])

        if q1.iscommonphrasetranscriptlines(transcriptline['text']):
            pdfindexedtext = getnewname(transcriptline)
            commonphraselines.append({'markeduptext': transcriptline['text'], 'pdfindexedtext': pdfindexedtext})

        else:

            # Create a completely pdf-indexed version of the transcriptline
            pdfindexedtext = getnewname(transcriptline)

            # If the text of the transcriptline is a "common phrase", add to "commonphraselines"

            # Create a marked up transcriptline
            markeduptext = s1.trigramtestsentence(transcriptline, 0)

            markeduplines.append({'markeduptext': markeduptext,
                                  'pdfindexedtext': pdfindexedtext})

    preprocessmarkeduplines(markeduplines)

    # Convert into page / line directives
    directives = convertmarkeduplinestodirectives(markeduplines)

    directives1 = convertcommonphraselinestodirectives(commonphraselines)

    # Diagnostics
    writemarkeduplinestotextfile(markeduplines)
    writedirectivestotextfile(directives)


    ProcessPDFFile.AnnotatePDFFile("2024-05-21.pdf", directives, "pink")
    ProcessPDFFile.AnnotatePDFFile("2024-05-21_highlighted.pdf", directives1, "green")

    exit()

def writemarkeduplinestotextfile(markeduplines):

    f = open("markeduplines.txt", "w")

    for markedupline in markeduplines:
        f.write(markedupline["markeduptext"] + "\n")

    f.close()

def writedirectivestotextfile(directives):

    f = open("directives.txt", "w")

    for directive in directives:
        f.write("page: " + str(directive["pdfpage"]) + ", line:  " +
        str(directive["pdfline"]) + ", text: " + directive["pdftext"] + "\n")

    f.close()


# Press the green button in the gutter to run the script.
if __name__ == '__main__':

    sql1 = SenateSQLDB.SenateTranscript()
    pdf1 = SenateSQLDB.SenateTranscriptPDFLines()
    s1 = ngramlineevaluate.NGramEvaluate()
    markeduplines = []

    diagnostic()

    # Hack - Load single file to process
    filename2process = "2024-05-21.pdf"
    pdfDoc = fitz.open(filename2process)  # open a document

    # Set up a memory buffer to save the generated output PDF with highlighting
    output_buffer = BytesIO()

    # # START START START
    #
    sql1 = SenateSQLDB.SenateTranscript()
    pdf1 = SenateSQLDB.SenateTranscriptPDFLines()

    # Pull all transcriptlines for the date
    transcriptlines = sql1.select_all("select id, speaker, page, line, text from transcriptlines "
                                      "where date='2024-05-21'")

    # Scan all lines in transcript and mark any common phrases
    q1 = commonphraseregexcheck.DetermineCommonPhrases()
    commonphraselines = q1.getcommonphrasetranscriptlines(transcriptlines)

    # Create a list of pdf lines to highlight
    pdflinestohighlight = []
    for commonphraseline in commonphraselines:
        pdfresults = pdf1.get_pdflines(commonphraseline["id"])

        for pdfresult in pdfresults:
            pdflinestohighlight.append(pdfresult)

    ProcessPDFFile.CreateHighlightedPDFFile("2024-05-16.pdf", pdflinestohighlight)

    # # Reactivate this to do quick jobs for Cathy
    exit()

    # Perform ngram evaluation of transcript lines that are not common phrases
    s1 = ngramlineevaluate.NGramEvaluate()

    markeduplines = []

    for transcriptline in transcriptlines:

        # If the transcript line is not one of the commonphrase lines
        transcriptline_tocheckagainstcommonphraselines = {'id': transcriptline['id'],
                                                          'page': transcriptline['page'],
                                                          'line': transcriptline['line']}

        if transcriptline_tocheckagainstcommonphraselines not in commonphraselines:

            # Create a completely pdf-indexed version of the transcriptline
            pdfindexedtext = getnewname(transcriptline)

            # Create a marked up transcriptline
            markeduptext = s1.trigramtestsentence(transcriptline, 0)

            markeduplines.append({'markeduptext': markeduptext,
                                  'pdfindexedtext': pdfindexedtext})

            preprocessmarkeduplines(markeduplines)

            i = 10

    # Convert into page / line directives
    directives = convertmarkeduplinestodirectives(markeduplines)

    ProcessPDFFile.AnnotatePDFFile("2024-05-16.pdf", directives)

    exit()


    r1 = spellcheck.CheckSpelling()
    misspelledwords = r1.getmisspelledwords(transcriptlines)

    templine = ""
    templines = []

    for transcriptline in transcriptlines:

        # Mark common phrase lines
        matchpageline = {'page': transcriptline['page'], 'line': transcriptline['line']}

        if matchpageline in commonphraselines:
            templine = "<p>[{0}/{1}] - {2}:   ".format(transcriptline['page'],
                                                       transcriptline['line'],
                                                       transcriptline['speaker'])
            templine += "<s>{0}</s></p>".format(transcriptline['text'])

        else:
            templine = s1.trigramtestsentence(transcriptline, 0)

        templines.append(templine)

        with open('my_file.txt', 'a') as f:
            f.write(templine + '\n')

    i = 10

    exit()
    #
    # # Working here - writing the ngramlineevaluate class
    #

    # print(r1.IsWordCorrectlySpelled("I'd"))
    # #
    # regexes = q1.loadsenateregexes()

    # # END END END END END

    # Get list of senate common phrase regexes
    senateregexes = loadsenateregexes()

    # Expand list with common phrases that feature Senator names
    senatorregexes = loadsenatorregexes()
    for senatorregex in senatorregexes:
        senateregexes.append(senatorregex)

    sql1 = SenateSQLDB.SenateTranscript()
    pdf1 = SenateSQLDB.SenateTranscriptPDFLines()

    transcriptlines = sql1.select_all("select id, page, line, text from transcriptlines "
                                      "where date='2024-05-16' limit 20")

    transcriptlinecount = 0
    matchlinecount = 0

    pdflinestohighlight = []

    for transcriptline in transcriptlines:
        # print(transcriptline)
        transcriptlinecount += 1

        for senateregex in senateregexes:

            # print(senateregex)
            # if senateregex == "^The Senate will come to order\.$":
            #     i = 10

            if "Response of" in transcriptline['text']:
                if "Response of" in senateregex:
                    i = 10

            if re.match(senateregex, transcriptline['text']):

                # Set up highlighting info
                # [pdfpage, pdfline, pdftext]
                #
                #
                pdfresults = pdf1.get_pdflines(transcriptline["id"])

                for pdfresult in pdfresults:
                    pdflinestohighlight.append(pdfresult)

                print("Match: {0} : {1}".format(transcriptline, senateregex))
                print("")
                matchlinecount += 1
                break

    # highlight_pdffile(pdflinestohighlight)
    ProcessPDFFile.CreateUnderlinedPDFFile("2024-05-16.pdf", pdflinestohighlight)

    # Spellchecking

    # loadhyphenatedwords()

    misspelledwords = []

    for transcriptline in transcriptlines:
        linewords = transcriptline['text'].split()

        # Clean up all line words
        for i in range(len(linewords)):
            if "." in linewords[i]:
                linewords[i] = linewords[i].replace(".", "")
            if "," in linewords[i]:
                linewords[i] = linewords[i].replace(",", "")
            if ":" in linewords[i]:
                linewords[i] = linewords[i].replace(":", "")

        to_be_removed = {"-", "--"}
        linewords = [item for item in linewords if item not in to_be_removed]

        for lineword in linewords:

            if not IsWordCorrectlySpelled(lineword):
                # print("Misspelled word : {0} page {1} line {2}".format(lineword,
                #       str(transcriptline['page']),
                #       str(transcriptline['line'])))
                if lineword not in misspelledwords:
                    misspelledwords.append(lineword)

    #
    #     Remove proper names

    with open("senatornames.txt") as f2:
        senatornames = f2.read().splitlines()

    misspelledwords = [item for item in misspelledwords if item not in senatornames]

    with open("romannumerals.txt") as f2:
        romannumerals = f2.read().splitlines()

    misspelledwords = [item for item in misspelledwords if item not in romannumerals]

    with open("nyscounties.txt") as f2:
        counties = f2.read().splitlines()

    misspelledwords = [item for item in misspelledwords if item not in counties]

    with open("nyscities.txt") as f2:
        cities = f2.read().splitlines()

    misspelledwords = [item for item in misspelledwords if item not in cities]

    with open("daysoftheweek.txt") as f2:
        days = f2.read().splitlines()

    misspelledwords = [item for item in misspelledwords if item not in days]

    with open("monthsoftheyear.txt") as f2:
        months = f2.read().splitlines()

    misspelledwords = [item for item in misspelledwords if item not in months]

    with open("names.txt") as f2:
        firstnames = f2.read().splitlines()

    misspelledwords = [item for item in misspelledwords if item not in firstnames]

    with open("lastnames.txt") as f2:
        lastnames = f2.read().splitlines()

    misspelledwords = [item for item in misspelledwords if item not in lastnames]

    with open("acronyms.txt") as f2:
        acronyms = f2.read().splitlines()

    misspelledwords = [item for item in misspelledwords if item not in acronyms]

    with open("nationalities.txt") as f2:
        nationalities = f2.read().splitlines()

    misspelledwords = [item for item in misspelledwords if item not in nationalities]

    with open("worldcities.txt") as f2:
        worldcities = f2.read().splitlines()

    misspelledwords = [item for item in misspelledwords if item not in worldcities]

    with open("hyphenated_words.txt") as f2:
        hyphenatedwords = f2.read().splitlines()

    misspelledwords = [item for item in misspelledwords if item not in hyphenatedwords]

    with open("famouspeople.txt") as f2:
        famouspeople = f2.read().splitlines()

    misspelledwords = [item for item in misspelledwords if item not in famouspeople]

    with open("contractions.txt") as f2:
        contractions = f2.read().splitlines()

    #
    #
    #             senator
    #             for word in misspelledwords:
    #                 f.write(word + "\n")
    #
    #
    #
    # print("Total lines: {0}".format(str(transcriptlinecount)))
    # print("Matching lines: {0}".format(str(matchlinecount)))

    print("**")
    misspelledwords.sort()

    # # Remove legitimate contractions <= TODO fix with list comprehension!
    # for spelledword in misspelledwords:
    #     if "'" in spelledword:
    #         isContractionLegitimate()

    # Remove legitimate contractions
    legitimatecontractions = [word for word in misspelledwords if
                              "'" in word and isContractionLegitimate(word, contractions)]
    misspelledwords = [word for word in misspelledwords if word not in legitimatecontractions]

    # Remove currency
    misspelledwords = [word for word in misspelledwords if not re.match("^\$\d+", word)]

    # Remove Senate bills
    misspelledwords = [word for word in misspelledwords if not re.match("^S\d+", word)]

    #
    # for spelledword in misspelledwords:
    #     if re.match("^\$\d+", spelledword):
    #         misspelledwords.remove(spelledword)

    # # Remove Senate bills
    # for spelledword in misspelledwords:
    #     if re.match("^S\d+", spelledword):
    #         misspelledwords.remove(spelledword)

    print(misspelledwords)

    f = open("misspelled_words", "w")

    for word in misspelledwords:
        f.write(word + "\n")

