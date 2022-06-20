import unittest
import sys
from ahri import utils
from ahri import args
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

class EpiData(CreateVars):
    def __init__(self, data = pd.read_pickle(args.epi_pkl)):
        self.data = data
        # self.args = args
        super().__init__(data)

    def __repr__(self):
        return f"{self.data}" 

    def get_epi(self):
        return self.data

class SetData(pd.DataFrame):
    def __init__(self, *args):
        pd.DataFrame.__init__(self, *args)
        self.data = self
        self

    def set_data(self, *args):
        data = self.data
        data = self[self.Female.isin(args.sex.values())]
        self.data = data
        return self

yy = SetData(hdat).set_data(args)


class HIVData(SetData):
    def __init__(self):
        super().__init__(self)

    def __repr__(self):
        return f"{self}" 

    def get_hiv(self):
        return self

    def get_age_cat(self, name = "AgeCat"):
        if "Age" not in self.columns:
            print(f"ahri: Warning! Dataset needs an Age column to create Age categories")
        self[name] = pd.cut(self["Age"], 
                [15, 25, 50, 105], include_lowest = True)
        return HIVData(self)
    

HIVData(hdat)

    # def get_repeat_testers(self):
    #     """
    #     Get the repeat tester data from an HIV test dataset. Repeat-testers
    #     have a minimum of two valid HIV test dates of which the first test is
    #     an HIV-negative test result. 
        
    #     Parameters
    #     ----------
    #     dat : pandas dataframe
    #         a dataframe from self.set_hiv()
    #     """
        
    #     dat = self.data
    #     if (dat is None): dat = self.set_hiv()
    #     obs_start = utils.get_dates_min(dat, "HIVNegative", "obs_start")
    #     early_pos = utils.get_dates_min(dat, "HIVPositive", "early_pos")
    #     late_neg = utils.get_dates_max(dat, "HIVNegative", "late_neg")
    #     late_pos = utils.get_dates_max(dat, "HIVPositive", "late_pos")
    #     dat = dat[['IIntID', 'Female']].drop_duplicates()
    #     dfs = [dat, obs_start, late_neg, early_pos, late_pos]
    #     dt = reduce(lambda left,right: \
    #     pd.merge(left,right,on='IIntID', how='left'), dfs)
    #     # drop if late neg after early pos
    #     dt['late_neg_after'] = (dt.late_neg > dt.early_pos) & \
    #     pd.notna(dt.late_neg) & pd.notna(dt.early_pos)
    #     rt = dt[dt.late_neg_after==False]. \
    #     drop(['late_neg_after', 'late_pos'], axis=1)
    #     # drop if no neg test
    #     rt = rt[-(pd.isna(rt.obs_start) & pd.isna(rt.late_neg))] 
    #     # drop if only 1 neg test and no pos test
    #     rt = rt[-((rt.obs_start == rt.late_neg) & pd.isna(rt.early_pos))]
    #     rt['sero_event'] = pd.notna(rt.early_pos).astype(int)
    #     self.data = rt
    #     return HIVData(self.args, self.data)

tt = HIVData(args)
tt.get_hiv().shape
tt.set_data()
tt.set_data().shape
tt.set_data().get_age_cat()

class RepeatTesters(CreateVars):
    def __init__(self, args, data = None):
        if data is None:
            self.data = pd.read_pickle(args.hiv_pkl)
        else:
            self.data = data
        super().__init__(self.data, args)
        self.args = args

    def __repr__(self):
        return f"{self.data}" 


tt = HIVData(args)


class SetData(DataProc):
    def __init__(self, args):
        self.data = data
        self.args = args
        super().__init__(self.data, args)

    def __repr__(self):
        return f"{self.data}" 

    def set_data(self):
        """
        Method to standardize the datasets by age, sex,  year, and area. The values
        for standardization are handled by the SetArgs class.

        Parameters
        ----------
        dat : pandas dataframe
            a pandas dataframe
        """
        dat = self.data
        dat = dat[dat.Female.isin(list(self.args.sex.values()))]
        for s in self.args.age.keys():
            dat = dat[
                ~((dat.Female == self.args.sex[s]) &
                    (dat.Age < self.args.age[s][0])) &  
                ~((dat.Female == self.args.sex[s]) &
                    (dat.Age > self.args.age[s][1])) & 
                dat.Year.isin(self.args.years)]
        # if (self.args.drop_tasp): 
          # dat = utils.drop_tasp(dat, self.bst_dta(write_pkl = False)) 
        self.data = dat
        return SetData(self.data, self.args)

class CreateVars:
    def __init__(self, data, args):
        self.data = data
        self.args = args

    def get_age_cat(self, name = "AgeCat"):
        if "Age" not in self.data.columns:
            print(f"ahri: Warning! Dataset needs an Age column to create Age categories")
        self.data[name] = pd.cut(self.data["Age"], 
                self.args.agecat, include_lowest = True)
        return CreateVars(self.data, self.args)

HIVData(args).get_age_cat().data

# HIVData(args).get_data()
# HIVData(args).get_hiv().set_data()
# HIVData(args).get_data().set_data()
# HIVData(args).get_hiv().set_data()
# HIVData(args).get_hiv().set_data().calc_age_cat()
# HIVData(args).get_hiv().get_repeat_testers().calc_age_cat()

class DataProc2:
    def __init__(self, args):
        self.args = args
        self.hiv = HIVData(self.args)
        self.epi = EpiData(self.args)

hiv_dta = root + "/ACDIS_HIV_All.pkl"
hdat = pd.read_pickle(hiv_dta)

class HIVData(SetArgs):
    def __init__(self, data):
        # self.data = pd.read_pickle(root + "/" + hiv_dta)
        self.data = data

    def __repr__(self):
        return f"{self.data}"

    def get_hiv(self):
        return self.data

    def calc_age_cat(self, name = "AgeCat"):
        if "Age" not in self.data.columns:
            print(f"ahri: Warning! Dataset needs an Age column to create Age categories")
        self.data[name] = pd.cut(self.data["Age"], [15, 25, 50, 105], include_lowest = True)
        return HIVData(self.data)

tt = HIVData(hdat)
yy = tt.get_hiv()
tt.calc_age_cat()



class DataProc3(SetArgs):
    def __init__(self, args):
        super().__init__(
            


                )
        self.args = args
        print(super())

tt = DataProc3(args)




epi = EpiData(args)
tt = epi.get_epi().get_age_cat()
tt.shape
epi.get_age_cat().data
tt = DataProc2(args)
tt.epi
tt.hiv
tt.get_hiv().set_data().calc_age_cat()
tt.get_repeat_testers()


pp = DataProc(args)
pp.epi_dta()
tt = HIVData(args).set_data()
tt= HIVData(args).set_data().calc_age_cat()
tt.calc_age_cat()

class MyTest(HIVData):

    def __init__(self, args):
        self.args = args 
        super().__init__(self.args)

    # def __repr__(self):
    #     return f"{self.__obj}"
    

    # def get_epi(self):
    #     self.__epi = pd.read_pickle(self.args.epi_pkl)
    #     return self.__epi


tt = MyTest(args = args)
# tt.get_epi()
tt.get_hiv().set_data()
tt.set_data()
tt.set_age()
tt.set_data().set_age
tt.AgeSet()

if __name__ == '__main__':
    unittest.main()

