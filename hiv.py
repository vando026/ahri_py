from ahri.args import *
from ahri.utils import *


class CalcInc:
    def __init__(self, args):
        self.args = args
        self.sdat = set_hiv(self.args)
        self.rtdat = get_repeat_testers(self.sdat)

        self.inc = do_inc(self.rtdat, self.args)
