import re

import SenateSQLDB

def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.


def loadsenateregexes():

    lines = []
    with open('senate_regexes.txt') as file:
            for line in file:
                line = line.strip()
                lines.append(line)

    return lines

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print_hi('PyCharm')

    # Get list of senate common phrase regexes
    senateregexes = loadsenateregexes()

    sql1 = SenateSQLDB.SenateTranscript()

    transcriptlines = sql1.select_all("select id, text from transcriptlines where date='2023-05-02'")

    transcriptlinecount = 0
    matchlinecount = 0

    for transcriptline in transcriptlines:
        # print(transcriptline)
        transcriptlinecount += 1


        for senateregex in senateregexes:

            # print(senateregex)

            if re.match(senateregex, transcriptline['text']):
                print("Match: {0} : {1}".format(transcriptline, senateregex))
                matchlinecount += 1
                break

    print("Total lines: {0}".format(str(transcriptlinecount)))
    print("Matching lines: {0}".format(str(matchlinecount)))
