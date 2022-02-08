import unittest
import sys
from ahri import utils
from ahri.args import SetFiles, SetArgs
from ahri.dataproc import DataProc
import numpy as np
import os

# in ipython run
# %run test_data.py "/home/alain/Seafile/AHRI_Data/2020"

class TestAHRI(unittest.TestCase):

    root = os.path.dirname(os.path.realpath(__file__)) 
    root = '/home/alain/Seafile/Programs/Python/library/ahri_dev/tests'
    args = SetArgs(root = root, years = np.arange(2005, 2020),
            drop_tasp = False)
    args.hiv_pkl = os.path.join(root, 'python/hiv.pkl')
    args.epi_pkl = os.path.join(root, 'python/epi.pkl')
    dtest = DataProc(args)

    hdat = dtest.get_hiv()
    sdat = dtest.set_hiv()
    rtdat = dtest.get_repeat_testers(sdat)
    edat = dtest.get_epi()
    esdat = dtest.set_epi()

    def test_hiv_nrows(self):
        nrows = self.hdat.shape[0]
        self.assertEqual(nrows, 500)

    def test_hivpos_n(self):
        hiv_vals = self.hdat.HIVPositive.count()
        self.assertEqual(hiv_vals, 150)

    def test_fem_n(self):
        fem_n = self.hdat.Female[self.hdat.Female == 1].count()
        self.assertEqual(fem_n, 344)

    def test_hiv_nrows2(self):
        nrows = self.sdat.shape[0]
        self.assertEqual(nrows, 305)

    def test_hiv_fem_n2(self):
        fem_n = self.sdat.Female[self.sdat.Female == 1].count()
        self.assertEqual(fem_n, 192)

    def test_hiv_year(self):
        year = np.mean(self.sdat.Year).round(3)
        self.assertEqual(year, 2011.157)

    def test_rt_nrow(self):
        nrow = self.rtdat.shape[0]
        self.assertEqual(nrow, 50)
        nval = self.rtdat.sero_event.sum()
        self.assertEqual(nval, 8)

    def test_epi_nrow(self):
        nrow = self.edat.shape[0]
        self.assertEqual(nrow, 500)
        nrow = self.edat.Female.value_counts()
        self.assertEqual(nrow[0], 197)

    def test_sepi_nrow(self):
        nrow = self.esdat.shape[0]
        self.assertEqual(nrow, 179)
        nrow = self.esdat.Female.value_counts()
        self.assertEqual(nrow[0], 93)
        nsum = self.esdat.Age.sum()
        self.assertEqual(nsum, 7037)

if __name__ == '__main__':
    unittest.main()
