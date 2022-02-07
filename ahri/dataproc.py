import pandas as pd
import numpy as np
from ahri.args import SetArgs
from ahri.utils import *
from functools import reduce

class DataProc(SetArgs):
    def __init__(self, args):
        self.args = args

    def pip_dta(self):
        """ Read in PIP data to identify ACIDS from TASP areas"""
        dat = pd.read_stata(self.args.bsifile, 
                columns = ['BSIntId', 'PIPSA'])
        dat = dat.rename(columns = {'BSIntId': 'BSIntID'})
        dat.to_pickle(self.args.pip_pkl)
        print(f"File saved to {self.args.pip_pkl}\n")
        return(dat)

    def hiv_dta(self):
        """ Read in HIV data with arguments for setting data"""
        dcols = ["IIntId", "ResidencyBSIntId", "VisitDate",
              "HIVResult", "Sex", "AgeAtVisit"]
        # if (addvars is not None):
            # dcols = dcols.append(addvars)
        hiv = pd.read_stata(self.args.hivfile, columns = dcols)
        hiv = hiv.rename(columns = {
          'IIntId':'IIntID',
          'ResidencyBSIntId':'BSIntID',
          'AgeAtVisit':'Age',
          'Sex':'Female'})
        hiv = hiv[hiv.Female.isin(['Female', 'Male'])]
        hiv = hiv.assign(Female = (hiv.Female=='Female').astype(int))
        hiv = hiv.sort_values(['IIntID', 'VisitDate'])
        hiv = hiv[hiv.HIVResult.isin(['Negative', 'Positive'])]
        hiv['HIVNegative'] = hiv.VisitDate[hiv.HIVResult == 'Negative']
        hiv['HIVPositive'] = hiv.VisitDate[hiv.HIVResult == 'Positive']
        hiv['Year'] = pd.DatetimeIndex(hiv.VisitDate).year
        hiv.to_pickle(self.args.hiv_pkl)
        print(f"File saved to {self.args.hiv_pkl}\n")
        return(hiv)

    def epi_dta(self, addvars = None):     
        print("Reading data, this may take time...")
        dat = pd.read_stata(self.args.epifile)
        dat = dat.rename(columns = {
            'IndividualId':'IIntID', 'LocationId':'BSIntID', 
            'CalendarYear': 'Year', 'Sex':'Female', 'Days':'ExpDays', 
            'StartDate':'ObservationStart', 'EndDate':'ObservationEnd'})
        dcols = ['IIntID', 'BSIntID', 'Female', 'ObservationStart',
                'ObservationEnd', 'Year', 'Age', 'DoB'] 
        if (addvars is not None):
            dcols = [dcols, addvars]
            dcols = [col for slist in dcols for col in slist]
        dat = dat[dcols]
        dat = dat[dat.Female.isin(['Female', 'Male'])]
        dat = dat.assign(Female = (dat.Female=='Female').astype(int))
        dat.to_pickle(self.args.epi_pkl)
        print(f"File saved to {self.args.epi_pkl}\n")
        return(dat)

    def get_hiv(self):
        """Read the pickled HIV dataset"""
        dat = pd.read_pickle(self.args.hiv_pkl)
        return(dat)

    def get_epi(self):
        """Read the pickled Surveillance dataset"""
        dat = pd.read_pickle(self.args.epi_pkl)
        return(dat)

    def get_pip(self):
        """Read the pickled PIP areas dataset"""
        dat = pd.read_pickle(self.args.pip_pkl)
        return(dat)

    def set_data(self, dat):
        """Function to set age, sex, and year by arguments"""
        dat = dat[dat.Year.isin(self.args.years)]
        dat = dat[dat.Female.isin(list(self.args.sex.values()))]
        if (self.args.drop_tasp): 
          dat = drop_tasp(dat, self.get_pip()) 
        for s in self.args.age.keys():
            dat = dat[~((dat.Female == self.args.sex[s]) &
                    (dat.Age < self.args.age[s][0]))] 
            dat = dat[~((dat.Female == self.args.sex[s]) &
                    (dat.Age > self.args.age[s][1]))]
        return(dat)

    def set_hiv(self):
        """Set the HIV data according to arguments"""
        dat = self.set_data(self.get_hiv())
        return(dat)


    def set_epi(self):
        """Set the Surveillence data according to arguments"""
        dat = self.set_data(self.get_epi())
        return(dat)

    def get_repeat_testers(self, dat = None):
        if (dat is None): dat = self.set_hiv()
        """Get repeat tester data from an HIV test dataset"""
        obs_start = get_dates_min(dat, "HIVNegative", "obs_start")
        early_pos = get_dates_min(dat, "HIVPositive", "early_pos")
        late_neg = get_dates_max(dat, "HIVNegative", "late_neg")
        late_pos = get_dates_max(dat, "HIVPositive", "late_pos")
        dat = dat[['IIntID', 'Female']].drop_duplicates()
        dfs = [dat, obs_start, late_neg, early_pos, late_pos]
        dt = reduce(lambda left,right: \
        pd.merge(left,right,on='IIntID', how='left'), dfs)
        # drop if late neg after early pos
        dt['late_neg_after'] = (dt.late_neg > dt.early_pos) & \
        pd.notna(dt.late_neg) & pd.notna(dt.early_pos)
        rt = dt[dt.late_neg_after==False]. \
        drop(['late_neg_after', 'late_pos'], axis=1)
        # drop if no neg test
        rt = rt[-(pd.isna(rt.obs_start) & pd.isna(rt.late_neg))] 
        # drop if only 1 neg test and no pos test
        rt = rt[-((rt.obs_start == rt.late_neg) & pd.isna(rt.early_pos))]
        rt['sero_event'] = pd.notna(rt.early_pos).astype(int)
        return(rt)


