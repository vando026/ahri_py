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

    args = SetArgs(paths = fpaths)
    dtest = DataProc(args)

    bdat = dtest.bst_dta(write_pkl = False)
    hdat = dtest.hiv_dta(write_pkl = False)
    edat = dtest.epi_dta(write_pkl = False)

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
      hdat2 = utils.drop_tasp(self.hdat, self.bdat)
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
      edat2 = utils.drop_tasp(self.edat, self.bdat)
      self.assertEqual(len(np.unique(edat2.IIntID)), 5) 
      self.assertEqual(len(np.unique(edat2.BSIntID)), 6) 
      self.assertEqual(len(np.unique(edat2.loc[edat2.Female==1, \
          "IIntID"])), 3) 
      self.assertEqual(edat2.shape[1], 8) 
      self.assertEqual(np.sort(np.unique(edat2.BSIntID)).tolist(), \
              [3455, 6496, 9305, 15588, 16563, 17843])


    def test_get_hiv1(self):
        args = SetArgs(file_paths = self.fpaths,
            years = np.arange(2007, 2015), 
            age = {"Fem": [40, 80]})
        dtest = DataProc(args)
        hdat = dtest.get_hiv()
        hiv1 = dtest.set_data(hdat)
        self.assertEqual(np.unique(hiv1.Female).tolist(), [1]) 
        self.assertEqual(hiv1.Year.tolist(), [2007])
        self.assertEqual(hiv1.Age.tolist(), [72])
        self.assertEqual(hiv1.IIntID.tolist(), [740])

    def test_get_hiv0(self):
        args = SetArgs(file_paths = self.fpaths,
            years = np.arange(2005, 2011), 
            age = {"Mal": [20, 25]},
            drop_tasp = False)
        dtest = DataProc(args)
        hdat = dtest.get_hiv()
        hiv = dtest.set_data(hdat)
        hiv = dtest.calc_age_cat(hiv)
        self.assertEqual(np.unique(hiv.Female).tolist(), [0]) 
        self.assertEqual(hiv.Year.tolist(), [2005])
        self.assertEqual(hiv.Age.tolist(), [21])
        self.assertEqual(hiv.IIntID.tolist(), [1356])
        self.assertEqual(len(hiv.loc[hiv.AgeCat.astype(str) == "[20, 25)", "IIntID"]), 1)

    def test_age_cat(self):
        args = SetArgs(file_paths = self.fpaths,
          years = np.arange(2001, 2018),
          age = {"Fem": [15, 54], "Mal": [15, 54]})
        dtest = DataProc(args)
        hdat = dtest.get_hiv()
        hiv = dtest.set_data(hdat)
        hiv = dtest.calc_age_cat(hiv)
        print(hiv)
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
    
    def test_hiv_equal(self):
        args = SetArgs(file_paths = self.fpaths,
          years = np.arange(2005, 2017),
          age = {"Fem": [15, 54], "Mal": [15, 54]})
        dtest = DataProc(args)
        hdat = dtest.get_hiv()
        hiv = dtest.set_data(hdat)
        hiv1 = dtest.set_hiv()
        self.assertTrue(all(hiv1.IIntID ==  hiv.IIntID))
        self.assertTrue(all(hiv1.Age ==  hiv.Age))
        self.assertTrue(all(hiv1.Year ==  hiv.Year))
        self.assertTrue(all(hiv1 == hiv))

    def test_epi_equal(self):
        args = SetArgs(file_paths = self.fpaths,
            years = np.arange(2010, 2020), 
            age = {"Fem": [16, 60], "Mal": [16, 60]})
        dtest = DataProc(args)
        edat = dtest.epi_dta(write_pkl = False)
        edat = dtest.set_data(edat)
        edat1 = dtest.set_epi()
        self.assertTrue(all(edat == edat1))

class SetData:
    def __init__(self, data, args):
        self.args = args
        self.__obj = data

    def set_data(self, args):
        return SetData(data =
            self.__obj[self.__obj.Female.isin(self.args.sex.values())], args = args)


class MyTest(SetData):

    def __init__(self, args):
        self.data = pd.read_pickle(self.args.hiv_pkl)
        self.args = args 

    def __repr__(self):
        return f"{self.__obj}"
    
    def getData(self):
        return self.__obj

    SetData.__init__()

tt = MyTest(args = args)
tt.set_data()
tt.set_age()
tt.set_data().set_age
tt.AgeSet()

if __name__ == '__main__':
    unittest.main()

