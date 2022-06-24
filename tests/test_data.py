import unittest
import sys
from ahri import utils
from ahri import args
from ahri.args import SetFiles, SetArgs
from ahri.dataproc import DataProc, SetData, SetAtInit
import numpy as np
import pandas as pd
import os
# import package_resources

# in ipython run
# %run test_data.py "/home/alain/Seafile/AHRI_Data/2020"

class TestAHRI(unittest.TestCase):

    # root = os.path.dirname(os.path.realpath(__file__)) 
    root = '/home/alain/Seafile/Programs/Python/library/ahri_dev/src/ahri/data'
    targs = SetArgs(root = root, verbose = False)
    targs.path_hiv_dta("RD05-99_ACDIS_HIV_Sample.dta")
    targs.path_bst_dta("RD01-03_ACDIS_BS_Sample.dta")
    targs.path_epi_dta("SurveillanceEpisodes_Sample.dta")
    targs.path_hiv_pkl("RD05-99_ACDIS_HIV_Sample.pkl")
    targs.path_bst_pkl("RD01-03_ACDIS_BS_Sample.pkl")
    targs.path_epi_pkl("SurveillanceEpisodes_Sample.pkl")

    dread = DataProc(targs)
    bdat = dread.proc_bst_dta(write_pkl = True)
    hdat = dread.proc_hiv_dta(write_pkl = True)
    edat = dread.proc_epi_dta(write_pkl = True)

    def test_bst_dta(self):
      self.assertEqual(self.bdat.shape[0], 7)
      self.assertEqual(self.bdat.shape[1], 3)
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
      hdat2 = SetAtInit(self.targs).drop_tasp(self.hdat, self.bdat)
      self.assertEqual(np.sort(np.unique((
          hdat2.loc[~np.isnan(hdat2.BSIntID), \
              "BSIntID"])).astype(int)).tolist(), \
          [6496, 9305, 15588, 17843])
      self.assertEqual(hdat2.shape[1], 9)
      self.assertEqual(len(np.unique(hdat2.loc[hdat2.Female == 1,
          "IIntID"])), 3)
      self.assertEqual(np.sum(hdat2.Age), 343)

    def test_read_epi(self):
      self.assertEqual(len(np.unique(self.edat.IIntID)), 5) 
      self.assertEqual(len(np.unique(self.edat.BSIntID)), 7) 
      self.assertEqual(len(np.unique(self.edat.loc[self.edat.Female==1, "IIntID"])), 3) 
      self.assertEqual(self.edat.shape[1], 8) 
      self.assertEqual(np.sort(np.unique(self.edat.BSIntID)).tolist(), \
              [ 616, 3455, 6496, 9305, 15588, 16563, 17843 ])

    def test_read_epi2(self):
      edat2 = SetAtInit(self.targs).drop_tasp(self.edat, self.bdat)
      self.assertEqual(len(np.unique(edat2.IIntID)), 5) 
      self.assertEqual(len(np.unique(edat2.BSIntID)), 6) 
      self.assertEqual(len(np.unique(edat2.loc[edat2.Female==1, \
          "IIntID"])), 3) 
      self.assertEqual(edat2.shape[1], 8) 
      self.assertEqual(np.sort(np.unique(edat2.BSIntID)).tolist(), \
              [3455, 6496, 9305, 15588, 16563, 17843])


    def test_get_hiv1(self):
        self.targs.update_years(np.arange(2007, 2015))
        self.targs.update_age({"Fem": [40, 80]})
        dtest = SetData(self.targs)
        hiv1 = dtest.hiv_data
        self.assertEqual(np.unique(hiv1.Female).tolist(), [1]) 
        self.assertEqual(hiv1.Year.tolist(), [2007])
        self.assertEqual(hiv1.Age.tolist(), [72])
        self.assertEqual(hiv1.IIntID.tolist(), [740])

    def test_get_hiv0(self):
        self.targs.update_years(np.arange(2005, 2011))
        self.targs.update_age({"Mal": [20, 25]})
        self.targs.update_drop_tasp(drop = False)
        dtest = SetData(self.targs)
        hiv = dtest.hiv_data
        hiv = dtest.calc_age_cat(hiv)
        self.assertEqual(np.unique(hiv.Female).tolist(), [0]) 
        self.assertEqual(hiv.Year.tolist(), [2005])
        self.assertEqual(hiv.Age.tolist(), [21])
        self.assertEqual(hiv.IIntID.tolist(), [1356])
        self.assertEqual(len(hiv.loc[hiv.AgeCat.astype(str) == "[20, 25)", "IIntID"]), 1)

    def test_age_cat(self):
        self.targs.update_years(np.arange(2001, 2018))
        self.targs.update_age({"Fem": [15, 54], "Mal": [15, 54]})
        dtest = SetData(self.targs)
        hiv = dtest.hiv_data
        hiv = dtest.calc_age_cat(hiv)
        self.assertEqual(np.sort(np.unique(hiv.IIntID)).tolist(), \
              [795, 800, 1356, 1436])
        self.assertTrue(np.min(hiv.Year) >= 2001)
        self.assertTrue(np.max(hiv.Year) <= 2018)
        self.assertTrue(np.min(hiv.Age) >= 15)
        self.assertTrue(np.min(hiv.Age) <= 54)
        self.assertEqual(len(hiv.loc[hiv.AgeCat.astype(str) == "[20, 25)", "IIntID"]), 2)
        self.assertEqual(len(hiv.loc[hiv.AgeCat.astype(str) == "[25, 30)", "IIntID"]), 1)
        self.assertEqual(len(hiv.loc[hiv.AgeCat.astype(str) == "[30, 35)", "IIntID"]), 2)
        self.assertEqual(len(hiv.loc[hiv.AgeCat.astype(str) == "[70, 75)", "IIntID"]), 0)
    
if __name__ == '__main__':
    unittest.main()

