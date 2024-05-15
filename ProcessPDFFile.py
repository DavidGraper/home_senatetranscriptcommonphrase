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

        # Get the text of this pdfline to highlight Get the individual text of
        # that specific line and call it the "needle"
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
