import SenateSQLDB

import nltk
from nltk import ngrams
from collections import defaultdict
from collections import Counter
from nltk.tokenize import WhitespaceTokenizer
import re

class NGramEvaluate:

    def __init__(self):

        self.sdb = SenateSQLDB.SenateTrigrams()

    def remove_punctuation(self, input_string):

        # Make a translation table that maps all punctuation characters to None
        translator = str.maketrans(",$!?.-", "      ")

        # Apply the translation table to the input string
        result = input_string.translate(translator)

        return result

    def breakintotrigrams(self, words, N):

        # Preprocess the words (convert to lowercase, remove punctuation)
        words = [word.lower() for word in words if word.isalnum()]

        # Create N-grams from the tokenized words
        ngrams_list = list(
            ngrams(words, N, pad_left=True, pad_right=True, left_pad_symbol='<s>', right_pad_symbol='</s>'))

        return ngrams_list

    def trigramtestsentence(self, transline, percentcutoff):

        sentence = transline['text']
        page = transline['page']
        line = transline['line']
        speaker = transline['speaker']

        returnsentence = ""
        badngrams = []

        # First cache a punctuated version of sentence
        sentencep = sentence
        sentencepwords = WhitespaceTokenizer().tokenize(sentencep)

        # Then preprocess the sentence

        # Remove punctuation
        sentence = self.remove_punctuation(sentence)

        # Tokenize the sentence
        sentencewords = nltk.word_tokenize(sentence)

        # Break the sentence into a series of ngrams
        sentencengrams = self.breakintotrigrams(sentencewords, 4)

        # Hack - creating 2 offset for first ngram
        ngramcounter = 2

        # Hack - Remove first two ngram entries
        sentencengrams.pop(0)
        sentencengrams.pop(0)

        # Hack - Remove the last two ngram entries
        sentencengrams.pop()
        sentencengrams.pop()

        # Hack
        badngramcount = 0

        #
        for sentencengram in sentencengrams:

            ngramcounter += 1

            sentencetrigramtext = "{0} {1} {2}".format(sentencengram[0], sentencengram[1], sentencengram[2])
            sentencenextword = sentencengram[3]

            # print("***")
            # print("Seeking trigram: '{0}'".format(sentencetrigramtext))
            # print("with nextword: '{0}'".format(sentencenextword))

            ngramdistribution = self.sdb.gettrigraminfo(sentencetrigramtext)

            # calculate probability of nextword given token
            totalfrequency = 0
            nextwordfrequency = 0
            probability = 0
            for ngramcount in ngramdistribution:
                if ngramcount['nextword'] == sentencenextword:
                    nextwordfrequency = ngramcount['frequency']
                    totalfrequency += nextwordfrequency
                else:
                    totalfrequency += ngramcount["frequency"]

            # Hack
            if totalfrequency == 0:
                probability = 0
            else:
                probability = (nextwordfrequency / totalfrequency) * 100

            # print("Probability = {0}".format(probability))
            # print("BadNGramCount = {0}".format(badngramcount))
            # print("*****")

            # Hack

            if not probability > percentcutoff:
                badngramcount += 1
                badngrams.append(ngramcounter)

        # Assemble formatted string
        k = 1
        return1 = ""
        # return1 = "<p>[{0}/{1}] - {2}:   ".format(page, line, speaker)
        for pword in sentencepwords:
            if k in badngrams:
                return1 += "<x>" + pword + "</x> "
            else:
                return1 += pword + " "
            k += 1

        # return1 += "</p>"

        # with open('my_file.txt', 'a') as f:
        #     f.write(return1 + '\n')

        i = 10

        # Clean up the marked up string to include only one start and one end marker
        return1 = re.sub(r"</x> <x>", " ", return1)

        return return1

        #
        # print(sentencewords)
        #
        # badranges = []
        #
        # currentlowerinterval = 0
        # currentupperinterval = 0
        #
        # for badngram in badngrams:
        #
        #     lowerinterval = badngram
        #     upperinterval = badngram + 3
        #
        #     # initialize first interval
        #     if currentlowerinterval == 0 and currentupperinterval == 0:
        #         currentlowerinterval = lowerinterval
        #         currentupperinterval = upperinterval
        #         currentinterval = [currentlowerinterval, currentupperinterval]
        #         continue
        #
        #     # extend current interval
        #     if lowerinterval <= currentupperinterval:
        #         currentupperinterval = upperinterval
        #         currentinterval = [currentlowerinterval, currentupperinterval]
        #
        #     # start new interval
        #     elif lowerinterval > currentupperinterval:
        #         badranges.append(currentinterval)
        #         currentlowerinterval = lowerinterval
        #         currentupperinterval = upperinterval
        #         currentinterval = [currentlowerinterval, currentupperinterval]
        #
        # # Write final interval if it exists
        # if 'currentinterval' in locals():
        #     badranges.append(currentinterval)
        #
        # for badrange in badranges:
        #     start = badrange[0] - 1
        #     end = badrange[1] - 1
        #
        #     # Hack
        #     if end > len(sentencewords):
        #         end = len(sentencewords)
        #
        #     sentencewords[start] = "<i><b>" + sentencewords[start]
        #     sentencewords[end] = sentencewords[end] + r"</i></b>"
        #
        # i=10

