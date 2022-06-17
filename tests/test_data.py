import unittest
import sys
from ahri import utils
from ahri.args import SetFiles, SetArgs
from ahri.dataproc import DataProc
import numpy as np
import pandas as pd
import os
# import package_resources

# in ipython run
# %run test_data.py "/home/alain/Seafile/AHRI_Data/2020"

class TestAHRI(unittest.TestCase):

    # root = os.path.dirname(os.path.realpath(__file__)) 
    root = '/home/alain/Seafile/Programs/Python/library/ahri_dev/src/ahri/data'
    fpaths = SetFiles(root, 
        hiv_dta = "RD05-99_ACDIS_HIV_Sample.dta",
        bst_dta = "RD01-03_ACDIS_BS_Sample.dta",
        epi_dta = "SurveillanceEpisodes_Sample.dta",
        wgh_dta = "RD03-99_ACDIS_WGH_Sample.dta",
        mgh_dta = "RD04-99_ACDIS_MGH_Sample.dta")
    args = SetArgs(file_paths = fpaths)
    dtest = DataProc(args)

    bdat = dtest.bst_dta(write_pkl = False)
    hdat = dtest.hiv_dta(write_pkl = False)
    hdat2 = utils.drop_tasp(hdat, bdat)
    edat = dtest.epi_dta(write_pkl = False)
    edat2 = utils.drop_tasp(edat, bdat)

    def test_bst_dta(self):
      self.assertEqual(self.bdat.shape[0], 7)
      self.assertEqual(self.bdat.shape[1], 18)
      self.assertEqual(len(np.unique(self.bdat.BSIntID)), 7)
      self.assertEqual(self.bdat[self.bdat["PIPSA"]. \
          isin(["Southern PIPSA"])].shape[0], 6)

    def test_read_hiv1(self):
      self.assertEqual(len(np.unique(self.hdat.IIntID)), 5)
      self.assertEqual(self.hdat.shape[0], 14)
      self.assertEqual(self.hdat.shape[1], 9)
      self.assertEqual(len(np.unique(self.hdat.loc[self.hdat.Female == 1,
          "IIntID"])), 3)
      self.assertEqual(np.sum(self.hdat.Age), 427)

    def test_read_hiv2(self):
      self.assertEqual(np.sort(np.unique((
          self.hdat2.loc[~np.isnan(self.hdat2.BSIntID), \
              "BSIntID"])).astype(int)).tolist(), \
          [6496, 9305, 15588, 17843])
      self.assertEqual(self.hdat2.shape[1], 9)
      self.assertEqual(len(np.unique(self.hdat2.loc[self.hdat2.Female == 1,
          "IIntID"])), 3)
      self.assertEqual(np.sum(self.hdat2.Age), 343)

    def test_read_epi(self):
      self.assertEqual(len(np.unique(self.edat.IIntID)), 5) 
      self.assertEqual(len(np.unique(self.edat.BSIntID)), 7) 
      self.assertEqual(len(np.unique(self.edat.loc[self.edat.Female==1, "IIntID"])), 3) 
      self.assertEqual(self.edat.shape[1], 8) 
      self.assertEqual(np.sort(np.unique(self.edat.BSIntID)).tolist(), \
              [ 616, 3455, 6496, 9305, 15588, 16563, 17843 ])

    def test_read_epi2(self):
      self.assertEqual(len(np.unique(self.edat2.IIntID)), 5) 
      self.assertEqual(len(np.unique(self.edat2.BSIntID)), 6) 
      self.assertEqual(len(np.unique(self.edat2.loc[self.edat2.Female==1, \
          "IIntID"])), 3) 
      self.assertEqual(self.edat2.shape[1], 8) 
      self.assertEqual(np.sort(np.unique(self.edat2.BSIntID)).tolist(), \
              [3455, 6496, 9305, 15588, 16563, 17843])


if __name__ == '__main__':
    unittest.main()
