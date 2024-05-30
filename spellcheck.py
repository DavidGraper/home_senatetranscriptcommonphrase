import SenateSQLDB
from spellchecker import SpellChecker
import re

spell = SpellChecker()

class CheckSpelling:

    def __init__(self):

        # Update the spellcheck object with custom words from the database
        self.updateSpellCheckFromDatabase()

        # Load legitimate contractions from database
        self.loadLegitContractionsFromDatabase()

    def cleanwordsinsentence(self, sentence):

        linewords = sentence.split()

        for i in range(len(linewords)):
            if "." in linewords[i]:
                linewords[i] = linewords[i].replace(".", "")
            if "," in linewords[i]:
                linewords[i] = linewords[i].replace(",", "")
            if ":" in linewords[i]:
                linewords[i] = linewords[i].replace(":", "")

        # Additional illegal 'word'-like objects to be removed
        to_be_removed = {"-", "--"}
        linewords = [item for item in linewords if item not in to_be_removed]

        return linewords

    def getmisspelledwords(self, transcriptlines):

        misspelledwords = []

        for transcriptline in transcriptlines:

            linewords = self.cleanwordsinsentence(transcriptline['text'])

            for lineword in linewords:

                if not self.IsWordCorrectlySpelled(lineword):
                    if lineword not in misspelledwords:
                        misspelledwords.append({'transcriptlineid': transcriptline['id'],
                                               'text': lineword})

        return misspelledwords

    def updateSpellCheckFromDatabase(self):

        # Get custom words from database and add to Spellcheck object
        p1 = SenateSQLDB.GetSpelledWordsFromDatabase()
        customwords = p1.get_customwordsindb()

        customwordlist = [customword['word'] for customword in customwords]

        spell.word_frequency.load_words(customwordlist)

    def loadLegitContractionsFromDatabase(self):

        # Get custom words from database and add to Spellcheck object
        p1 = SenateSQLDB.GetLegitimateContractionsFromDatabase()
        self.legitcontractions = [x['contraction'] for x in p1.get_legitcontractions()]

    def IsWordCorrectlySpelled(self, word):

        # Pre-process the word string
        word = re.sub(r'[^\w\'\-]', '', word)

        # Pre-test for specific conditions, return True and exit if match found
        if self.islegittime(word):
            return True

        if self.islegitordinal(word):
            return True

        if self.islegitdigit(word):
            return True

        if self.iscurrency(word):
            return True

        if self.issenatebill(word):
            return True

        if "'" in word:
            if self.islegitcontraction(word):
                return True

        return spell[word]

    def islegittime(self, word):

        if re.match("[p|a]\.m\.,?", word):
            return True
        else:
            return False

    def islegitordinal(self, word):

        if re.match("\d{1,5}[st|nd|rd|th],?", word):
            return True
        else:
            return False

    def islegitdigit(self, word):

        if re.match("\d", word):
            word = re.sub(r'[^\w\d]', '', word)
            if word.isnumeric():
                return True
            else:
                return False
        else:
            return False

    def iscurrency(self, word):

        if re.match("^\$\d+", word):
            return True
        else:
            return False

    def issenatebill(self, word):

        if re.match("^\$\d+", word):
            return True
        else:
            return False

    def islegitcontraction(self, word):

        wordparts = word.split("'")

        if spell[wordparts[0]] and wordparts[1] in self.legitcontractions:
            return True
        else:
            return False
