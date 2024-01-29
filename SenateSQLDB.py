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
