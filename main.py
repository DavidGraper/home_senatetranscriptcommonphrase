import re
import SenateSQLDB
import fitz
from io import BytesIO


def highlight_pdffile(pdffilelines):

    for info in pdffilelines:
        page2update = int(info["pdfpage"])
        line2update = int(info["pdfline"]) - 1
        text2update = info["pdftext"]

        # Search for text
        page = pdfDoc[page2update]

        # Get page lines
        page_lines = page.get_text("text").split('\n')

        # Get rectangles for each line
        line_rects = []

        # Substring search
        needle = page_lines[line2update]

        cliprect = page.search_for(needle)

        # the_rect = page.search_for(text2update)
        the_rect = page.search_for(text2update, clip=cliprect[0])


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
    with open("2023-05-02_highlighted.pdf", mode='wb') as f:
        f.write(output_buffer.getbuffer())


def loadsenateregexes():

    lines = []
    with open('senate_regexes.txt') as file:
            for line in file:
                line = line.strip()
                lines.append(line)

    return lines

# Press the green button in the gutter to run the script.
if __name__ == '__main__':

    pdfDoc = fitz.open("2023-05-02.pdf")  # open a document

    # Save the generated PDF to memory buffer
    output_buffer = BytesIO()

    # Get list of senate common phrase regexes
    senateregexes = loadsenateregexes()

    sql1 = SenateSQLDB.SenateTranscript()
    pdf1 = SenateSQLDB.SenateTranscriptPDFLines()

    transcriptlines = sql1.select_all("select id, text from transcriptlines where date='2023-05-02'")

    transcriptlinecount = 0
    matchlinecount = 0

    pdflinestohighlight = []

    for transcriptline in transcriptlines:
        # print(transcriptline)
        transcriptlinecount += 1

        for senateregex in senateregexes:

            # print(senateregex)

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

    highlight_pdffile(pdflinestohighlight)

    print("Total lines: {0}".format(str(transcriptlinecount)))
    print("Matching lines: {0}".format(str(matchlinecount)))
