import unittest
import sys
from ahri import utils
from ahri.args import SetFiles, SetArgs
from ahri.dataproc import DataProc
from ahri.api import API
import numpy as np

# in ipython run
# %run test_data.py "/home/alain/Seafile/AHRI_Data/2020"

class TestAHRI(unittest.TestCase):

    root = '/home/alain/Seafile/AHRI_Data/2020'
    args = SetArgs(root = root,
        years = np.arange(2005, 2020))
    testy = DataProc(args)
    hdat = testy.get_hiv()
    sdat = testy.set_hiv()
    rtdat = testy.get_repeat_testers(sdat)
    edat = testy.get_epi()

    def test_hiv_nrows(self):
        nrows = self.hdat.shape[0]
        self.assertEqual(nrows, 185243)

    def test_hivpos_n(self):
        hiv_vals = self.hdat.HIVPositive.count()
        self.assertEqual(hiv_vals, 47861)

    def test_fem_n(self):
        fem_n = self.hdat.Female[self.hdat.Female == 1].count()
        self.assertEqual(fem_n, 125836)

    def test_hiv_nrows2(self):
        nrows = self.sdat.shape[0]
        self.assertEqual(nrows, 115141)

    def test_hiv_fem_n2(self):
        fem_n = self.sdat.Female[self.sdat.Female == 1].count()
        self.assertEqual(fem_n, 72892)

    def test_hiv_year(self):
        year = np.mean(self.sdat.Year).round(3)
        self.assertEqual(year, 2011.937)

    def test_hiv_year(self):
        year = np.mean(self.sdat.Year).round(3)
        self.assertEqual(year, 2011.937)

    def test_rt_nrow(self):
        nrow = self.rtdat.shape[0]
        self.assertEqual(nrow, 20994)

    def test_rt_sero(self):
        nval = self.rtdat.sero_event.sum()
        self.assertEqual(nval, 3176)

    def test_epi_nrow(self):
        nrow = self.edat.shape[0]
        self.assertEqual(nval, 3176)

if __name__ == '__main__':
    if len(sys.argv) > 1:
        TestAHRI.root = sys.argv.pop()
    unittest.main()
