import SenateSQLDB
import re

class DetermineCommonPhrases:

    def __init__(self):

        # Load regexes containing Senator names
        self.senateregexes = self.loadsenateregexes()

        # Load regexes containing common Senate expressions
        self.senatorregexes = self.loadsenatorregexes()

    def getcommonphrasetranscriptlines(self, transcriptlines):

        # Iterate through all transcript lines looking for regex matches, get the page/line number of matches
        commonphrases = []
        for transcriptline in transcriptlines:
            print(transcriptline)
            for senateregex in self.senateregexes:
                if re.match(senateregex, transcriptline['text']):
                    commonphrases.append({"page": transcriptline['page'],
                                          "line": transcriptline['line']})
            for senatorregex in self.senatorregexes:
                if re.match(senatorregex, transcriptline['text']):
                    commonphrases.append({"page": transcriptline['page'],
                                          "line": transcriptline['line']})

        return commonphrases

    def loadsenatorregexes(self):

        returnlines = []

        p1 = SenateSQLDB.SenatorRegexes()
        regextemplatelines = p1.get_regexes()

        p2 = SenateSQLDB.SenateSpeakers()
        senatornames = p2.get_speakers()

        # Create a series of regexes for that name
        senatorlastnames = []

        for senatorname in senatornames:

            # Remove "SENATOR " from string
            senatorlastname = senatorname['speakername'].replace("SENATOR ", "").lower().title()

            for regexttemplateline in regextemplatelines:
                returnlines.append(regexttemplateline['regex'].format(senatorlastname))

        return returnlines

    def loadsenateregexes(self):

        returnlines = []

        p1 = SenateSQLDB.SenateRegexes()
        regexlines = p1.get_regexes()

        for regexline in regexlines:
            returnlines.append(regexline['regex'])
        return returnlines
