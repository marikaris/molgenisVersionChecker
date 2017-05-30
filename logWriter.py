
class LogWriter():
    def __init__(self, filepath):
        self.logfile = open(filepath, 'a')
        self.filepath = filepath

    def write_row(self, text):
        self.logfile.write(text+'\n')

    def reset(self, header):
        self.logfile.close()
        self.logfile = open(self.filepath, 'w')
        self.logfile.write(header+'\n')

    def close_logs(self):
        self.logfile.close()