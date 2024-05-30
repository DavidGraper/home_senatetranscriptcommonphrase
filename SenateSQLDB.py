from SQLBase import SqlBase


class SenateTranscript(SqlBase):
    def __init__(self):
        SqlBase.__init__(self, "localhost", "dgraper", "R3ind33r", "senate")

    def insert(self, page, line, speaker, text, date):
        query = "INSERT INTO transcriptlines (page, line, speaker, text, date) VALUES ({0},{1},'{2}','{3}','{4}')".format(page, line, speaker, text, date)
        # query = "INSERT INTO transcriptlines (page, line, speaker, text, date) VALUES (1, 1, 'Speaker Dave','Text One Two Three', '3/3/23')"
        # return self.execute(query, [page, line, speaker, text, date])
        return self.execute(query)

    def get(self, username):
        query = "SELECT id, username, email FROM users WHERE username=%s"
        return self.select_one(query, [username])

    def get_all(self):
        query = "SELECT id, username, email FROM users"
        return self.select_all(query)

    def update(self, username, email):
        query = "UPDATE users SET email=%s WHERE username=%s"
        return self.execute(query, [email, username])

    def delete(self, username):
        query = "DELETE FROM users WHERE username=%s"
        return self.execute(query, [username])


class SenateTranscriptRawText(SqlBase):
    def __init__(self):
        SqlBase.__init__(self, "localhost", "dgraper", "R3ind33r", "senate")

    def insert(self, filename, pagenumber, linenumber, text):

        query = "INSERT INTO pdftext (filename, pagenumber, linenumber, text) values ('{0}', {1}, {2}, '{3}')".format(filename, pagenumber, linenumber, text)

        return self.execute(query)


class SenateTranscriptPDFLines(SqlBase):
    def __init__(self):
        SqlBase.__init__(self, "localhost", "dgraper", "R3ind33r", "senate")

    def get_pdflines(self, transcriptlineid):
        query = "SELECT pdfpage, pdfline, pdftext FROM transcriptlinepdfbreaks WHERE transcriptlineid={0}".format(transcriptlineid)
        return self.select_all(query)


class SenateSpeakers(SqlBase):
    def __init__(self):
        SqlBase.__init__(self, "localhost", "dgraper", "R3ind33r", "senate")

    def get_speakers(self):
        query = "SELECT * from code_speakernames where active=1 and speakername like 'SENATOR%%'"
        return self.select_all(query, [])


class SenateWords(SqlBase):
    def __init__(self):
        SqlBase.__init__(self, "localhost", "dgraper", "R3ind33r", "senate")

    def get_words(self):
        query = "SELECT * from temp_uniquecorpuswords"
        return self.select_all(query, [])


class SenateRegexes(SqlBase):
    def __init__(self):
        SqlBase.__init__(self, "localhost", "dgraper", "R3ind33r", "senate")

    def get_regexes(self):
        query = "SELECT regex from data_regexes_senate"
        return self.select_all(query, [])

class SenatorRegexes(SqlBase):
    def __init__(self):
        SqlBase.__init__(self, "localhost", "dgraper", "R3ind33r", "senate")

    def get_regexes(self):
        query = "SELECT regex from data_regexes_senators"
        return self.select_all(query, [])

class GetSpelledWordsFromDatabase(SqlBase):
    def __init__(self):
        SqlBase.__init__(self, "localhost", "dgraper", "R3ind33r", "senate")

    def get_customwordsindb(self):
        query = "select word from data_legitwords"
        return self.select_all(query, [])

class GetLegitimateContractionsFromDatabase(SqlBase):
    def __init__(self):
        SqlBase.__init__(self, "localhost", "dgraper", "R3ind33r", "senate")

    def get_legitcontractions(self):
        query = "select contraction from data_legitcontractions"
        return self.select_all(query, [])

class SenateTrigrams(SqlBase):

    def __init__(self):
        SqlBase.__init__(self, "localhost", "dgraper", "R3ind33r", "senate")

    def gettrigraminfo(self, gram1to3):
        query = "select nextword, frequency from data_ngrams where token='{0}'".format(gram1to3)
        return self.select_all(query)


class GetPDFFileInfoForTranscriptLine(SqlBase):

    def __init__(self):
        SqlBase.__init__(self, "localhost", "dgraper", "R3ind33r", "senate")

    def getpdffileinfo(self, transcriptlineid):
        query = "select pdfpage, pdfline, pdftext from transcriptlinepdfbreaks where transcriptlineid='{0}'".format(transcriptlineid)
        return self.select_all(query)