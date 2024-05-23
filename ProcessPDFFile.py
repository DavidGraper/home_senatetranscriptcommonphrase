import re
import SenateSQLDB
import fitz
from io import BytesIO

def CreateHighlightedPDFFile(filename, pdffilelinestohighlight):

    # The database stores all transcripts in two tables:
    #
    # 1) "transcriptlines" is a straightforward collection of transcript sentences which
    # stores a speaker, a complete transcript sentence, the page it starts on, and the
    # line is starts on;
    # 2) "transcriptlinepdfbreaks" is a collection of lines in transcript pdf files that stores
    # the individual lines in the transcript's pdf file.  This includes the key id to the
    # corresponding record in "transcriptlines", the pdf page number, the pdf line number,
    # and the exact text of the pdf line.  Keep in mind that this exact text is more often than
    # not an incomplete part of a transcript sentence
    #
    # The first table is used for NLP, the second table is used for marking up a PDF file

    pdfDoc = fitz.open(filename)  # open a document

    # Set up a memory buffer to save the generated output PDF with highlighting
    output_buffer = BytesIO()

    # For each pdfline we want highlighted
    for pdflinetohighlight in pdffilelinestohighlight:

        # Get the page, line, and text of that pdfline
        page2update = int(pdflinetohighlight["pdfpage"]) - 1
        line2update = int(pdflinetohighlight["pdfline"]) - 1
        text2update = pdflinetohighlight["pdftext"]

        # Cache the relevant pdf page
        page = pdfDoc[page2update]

        # Split the pdf page's text into individual lines of text
        page_lines = page.get_text("text").split('\n')

        # Get the text of this pdfline to highlight
        # Get the individual text of that specific line and call it the "needle"
        needle = page_lines[line2update]

        # Scan the pdf page looking for the page rectangle that holds that needle
        cliprect = page.search_for(needle)

        # Within that needle, look for the text
        try:
            the_rect = page.search_for(text2update, clip=cliprect[0])
        except:
            print("Fail on page.search_for '{0}'".format(text2update))

        # Update the highlighting on the page
        highlight = page.add_highlight_annot(the_rect)
        highlight.update()

    # Write the highlighted pdf original out to a buffer and close the original
    pdfDoc.save(output_buffer)
    pdfDoc.close()

    # Save the output buffer to an output file as a new PDF file
    newfilename = filename.replace(".pdf", "_highlighted.pdf")
    with open(newfilename, mode='wb') as f:
        f.write(output_buffer.getbuffer())

def CreateUnderlinedPDFFile(filename, markeduplines):

    pdfDoc = fitz.open(filename)  # open a document

    # Set up a memory buffer to save the generated output PDF with highlighting
    output_buffer = BytesIO()

    # for markedupline in markeduplines:

        # Loop through markeduplines by pdf page

        #
        # # Pull out the phrases in the text to be underlined
        # phrases2underline = re.findall(r"<x>(.*?)</x>", markedupline[0])
        #
        # # Get dicts of pdf page/line info for each word of transcript line
        # pdflinewords = markedupline[1]
        #
        # # For each individual text chunk to be undderlined
        # for phrase2underline in phrases2underline:
        #
        #     # Break the chunk into words
        #     phrasewords = phrase2underline.split(" ")
        #
        #     # Walk through the dicts of pdf info for each word of transcriptline
        #     pdflinewordindex = 0
        #     toggle = False
        #
        #     for phraseword in phrasewords:
        #         for pdflinewordindex in range(len(pdflinewords)):
        #             if phraseword == pdflinewords[pdflinewordindex]['pdfword']:
        #                 pdflinewords[pdflinewordindex]['toggle'] = True
        #                 break



            # Walk through pdflinewords collection, one page at a time


        # Seek phrases2underline strings in the pdflinewords list to get

            # working here, need to iterate through each phrase to underline,
            # then each word in that phrase to see if it's chunked across lines and
            # then the lines for each chunk.
            # a phrase could be spread across multiple pdf lines
            # with the line and the chunk you can then find the rectangle to be
            # underlined




    # # For each pdfline we want highlighted
    # for pdflinetounderline in pdffilelinestounderline:
    #
    #     # Get the page, line, and text of that pdfline
    #     transcriptlineid = int(pdflinetounderline["id"])
    #     page2update = int(pdflinetounderline["page"]) - 1
    #     line2update = int(pdflinetounderline["line"]) - 1
    #     text2update = pdflinetounderline["text"]
    #
    #     # Break the marked up text to underline into chunks
    #     phrases2underline = re.findall(r"<x>(.*?)</x>", text2update)
    #
    #
    #     for phrase2underline in phrases2underline:
    #         pdflines2underline = getpdflinestounderline(phrase2underline, transcriptlineid)
    #
    #     # Cache the relevant pdf page
    #     page = pdfDoc[page2update]
    #
    #     # Breakdown the sentence (new)
    #
    #
    #
    #
    #
    #     # Split the pdf page's text into individual lines of text
    #     page_lines = page.get_text("text").split('\n')
    #
    #     # Get the text of this pdfline to highlight Get the individual text of
    #     # that specific line and call it the "needle"
    #     needle = page_lines[line2update]
    #
    #     # Scan the pdf page looking for the page rectangles that holds the text
    #     # chunks to underline
    #     cliprects = []
    #     for wordchunk in words2underline:
    #         cliprects.append(page.search_for(needle))
    #
    #
    #
    #     # Within that needle, look for the text
    #     try:
    #         the_rect = page.search_for(text2update, clip=cliprect[0])
    #     except:
    #         print("Fail on page.search_for '{0}'".format(text2update))
    #
    #     # Update the highlighting on the page
    #     highlight = page.add_highlight_annot(the_rect)
    #     highlight.update()

    # Write the highlighted pdf original out to a buffer and close the original
    pdfDoc.save(output_buffer)
    pdfDoc.close()

    # Save the output buffer to an output file as a new PDF file
    newfilename = filename.replace(".pdf", "_highlighted.pdf")
    with open(newfilename, mode='wb') as f:
        f.write(output_buffer.getbuffer())

def AnnotatePDFFile(filename, linedirectives):

    # The database stores all transcripts in two tables:
    #
    # 1) "transcriptlines" is a straightforward collection of transcript sentences which
    # stores a speaker, a complete transcript sentence, the page it starts on, and the
    # line is starts on;
    # 2) "transcriptlinepdfbreaks" is a collection of lines in transcript pdf files that stores
    # the individual lines in the transcript's pdf file.  This includes the key id to the
    # corresponding record in "transcriptlines", the pdf page number, the pdf line number,
    # and the exact text of the pdf line.  Keep in mind that this exact text is more often than
    # not an incomplete part of a transcript sentence
    #
    # The first table is used for NLP, the second table is used for marking up a PDF file

    pdfDoc = fitz.open(filename)  # open a document

    # Set up a memory buffer to save the generated output PDF with highlighting
    output_buffer = BytesIO()

    for linedirective in linedirectives:

        # Get the page, line, and text of that pdfline
        page2update = int(pdflinetohighlight["pdfpage"]) - 1
        line2update = int(pdflinetohighlight["pdfline"]) - 1
        text2update = pdflinetohighlight["pdftext"]

        # Cache the relevant pdf page
        page = pdfDoc[page2update]

        # Split the pdf page's text into individual lines of text
        page_lines = page.get_text("text").split('\n')

        # # DIAGNOSTIC
        # content = page.get_text("dict")
        #
        # f = open("dictfile.txt", "a")
        # f.write(content)
        # f.close()

        # Get the text of this pdfline to highlight
        # Get the individual text of that specific line and call it the "needle"
        needle = page_lines[line2update]

        # Scan the pdf page looking for the page rectangle that holds that needle
        cliprect = page.search_for(needle)

        # Within that needle, look for the text
        try:
            the_rect = page.search_for(text2update, clip=cliprect[0])
        except:
            print("Fail on page.search_for '{0}'".format(text2update))

        # Update the highlighting on the page
        highlight = page.add_highlight_annot(the_rect)
        highlight.update()

    # Write the highlighted pdf original out to a buffer and close the original
    pdfDoc.save(output_buffer)
    pdfDoc.close()

    # Save the output buffer to an output file as a new PDF file
    newfilename = filename.replace(".pdf", "_highlighted.pdf")
    with open(newfilename, mode='wb') as f:
        f.write(output_buffer.getbuffer())


def getpdflinestounderline(phrase2underline, transcriptlineid):

    pdf1 = SenateSQLDB.SenateTranscriptPDFLines()

    # Get pdf lines for transcript line
    pdfpagelines = pdf1.get_pdflines(transcriptlineid)

    linetexts = []
    for pdfpageline in pdfpagelines:
        linetexts.append(pdfpageline['pdftext'])

    # If the phrase2underline is one of the pdf file lines
    if phrase2underline in linetexts:

        listindex = linetexts.index(phrase2underline)
        pdfpage1 = pdfpagelines[listindex]
        return1 = {'pdfpage': pdfpage1['pdfpage'],
                   'pdfline': pdfpage1['pdfline'],
                   'pdforiginaltext': pdfpage1['pdftext'],
                   'phrase2underline': phrase2underline}

        # return return1

    else:

        #     Split the phrase2underline into words
        words2underline = phrase2underline.split(" ")

    #     Loop through words creating subsentences until one matches
        index = 0
        substring1 = getsubstringsfromlist(words2underline, index)

        while substring1["word1"] != "":
            index += 1
            substring1 = getsubstringsfromlist(words2underline, index)















    # # Start by seeing if the entire phrase is present in any of the lines
    # for pdfpagetextline in pdfpagetextlines:
    #     if phrase2underline in pdfpagetextline:
    #
    #         # Return the page, line, and text of the line

    i = 10

def getsubstringsfromlist(listin, breakpoint):

    substring1words = listin[breakpoint:]
    substring2words = listin[:breakpoint]

    substring1word = ""
    substring2word = ""

    for word in substring1words:
        substring1word += word + " "

    for word in substring2words:
        substring2word += word + " "

    splitstring = {'word1': substring1word,
                   'word2': substring2word}

    return splitstring
