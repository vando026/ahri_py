import unittest
import sys
from ahri.utils import *
from ahri.args import SetFiles, SetArgs
import numpy as np

class TestAHRI(unittest.TestCase):

    root = '/home/alain/Seafile/AHRI_Data/2020'
    paths = SetFiles(root)
    args = SetArgs(paths = paths,
        years = np.arange(2005, 2020))
    hdat = get_hiv(paths.hiv_pkl)
    sdat = set_hiv(args)

    def test_hiv_nrows(self):
        nrows = self.hdat.shape[0]
        self.assertEqual(nrows, 168196)

    def test_hivpos_n(self):
        hiv_vals = self.hdat.HIVPositive.count()
        self.assertEqual(hiv_vals, 42507)

    def test_fem_n(self):
        fem_n = self.hdat.Female[self.hdat.Female == 1].count()
        self.assertEqual(fem_n, 112973)

    def test_hiv_nrows2(self):
        nrows = self.sdat.shape[0]
        self.assertEqual(nrows, 115141)

    def test_hiv_fem_n2(self):
        fem_n = self.sdat.Female[self.sdat.Female == 1].count()
        self.assertEqual(fem_n, 72892)

    def test_hiv_year(self):
        year = np.mean(self.sdat.Year).round(3)
        self.assertEqual(year, 2011.937)

if __name__ == '__main__':
    if len(sys.argv) > 1:
        TestAHRI.root = sys.argv.pop()
    unittest.main()
