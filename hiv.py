from ahri.args import *
from ahri.utils import *


class CalcInc:
    def __init__(self, args):
        self.args = args
        self.sdat = set_hiv(self.args)
        self.rtdat = get_repeat_testers(self.sdat)
        predat = pre_imp_set(self.rtdat)
        self.inc = do_inc(self.rtdat, predat, self.args)
