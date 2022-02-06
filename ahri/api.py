from ahri.dataproc import DataProc

class API:
    def __init__(self, args):
        self.args = args
        self.data_proc = DataProc(self.args)


