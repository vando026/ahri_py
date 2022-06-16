import pandas as pd
import numpy as np
from ahri.args import SetArgs
from ahri import utils
from functools import reduce

class DataProc(SetArgs):
    """
    A class that provides methods to read in the standard AHRI .dta files
    (Stata files), write them to .pkl format, and standardize data
    transformations accross the datatsets.

    Attributes
    ----------

    Methods
    -------

    hiv_dta()
        read in the HIV .dta dataset

    epi_dta(addvars = None)
        read in the Surviellance .dta dataset

    pip_dta()
        read in the PIP data to identify ACIDS from TASP areas

    get_hiv()
        load the HIV .pkl file into memory

    get_epi()
        load the Surveillance .pkl file into memory

    get_pip()
        load the PIP .pkl file into memory

    set_hiv(dat = None)
        set the HIV .pkl file according to user supplied arguments in the
        SetArgs class

    set_epi(dat = None)
        set the Surveillance .pkl file according to user supplied arguments in the
        SetArgs class

    set_data(dat)
        method to standardize transformation of the datasets

    get_repeat_testers(dat = None)
        method to create dataset of HIV repeat-testers
    """

    def __init__(self, args):
        """ 
        Parameters
        ----------
        args : object 
            a SetArgs object
        """

        self.args = args

    def pip_dta(self):
        """ read in PIP data to identify ACIDS from TASP areas
        Parameters
        ----------
        None
        """

        dat = pd.read_stata(self.args.bsifile, 
                columns = ['BSIntId', 'PIPSA'])
        dat = dat.rename(columns = {'BSIntId': 'BSIntID'})
        dat.to_pickle(self.args.pip_pkl)
        print(f"File saved to {self.args.pip_pkl}\n")
        return(dat)

    def hiv_dta(self):
        """ 
        Read in the HIV .dta dataset, keep subset of HIV test variables,
        harmonize variable names, drop irregular values for Men/Women,
        keep only valid HIV test results, write the .pkl file

        Parameters
        ----------
        None
        """

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
        """ 
        Read in the Surveillance .dta dataset, keep subset of variables,
        harmonize variable names, drop irregular values for Men/Women,
        write the .pkl file

        Parameters
        ----------
        addvars: list 
            add variables to the subset of variables selected from the .dta dataset
        """

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
        """
        Read the pickled HIV dataset into memory

        Parameters
        ----------
        None
        """

        dat = pd.read_pickle(self.args.hiv_pkl)
        return(dat)

    def get_epi(self):
        """
        Read the pickled Surveillance dataset into memory

        Parameters
        ----------
        None
        """

        dat = pd.read_pickle(self.args.epi_pkl)
        return(dat)

    def get_pip(self):
        """Read the pickled PIP dataset into memory

        Parameters
        ----------
        None
        """

        dat = pd.read_pickle(self.args.pip_pkl)
        return(dat)

    def set_data(self, dat):
        """
        Method to standardize the datasets by age, sex, and year. The values
        for standardization are handled by the SetArgs class.

        Parameters
        ----------
        dat : pandas dataframe
            a pandas dataframe
        """

        dat = dat[dat.Female.isin(list(self.args.sex.values()))]
        for s in self.args.age.keys():
            dat = dat[
                ~((dat.Female == self.args.sex[s]) &
                    (dat.Age < self.args.age[s][0])) &  
                ~((dat.Female == self.args.sex[s]) &
                    (dat.Age > self.args.age[s][1])) & 
                dat.Year.isin(self.args.years)]
        if (self.args.drop_tasp): 
          dat = utils.drop_tasp(dat, self.get_pip()) 
        return(dat)

    def set_hiv(self):
        """
        Set the HIV data according to parameters supplied to the SetArgs object

        Parameters
        ----------
        None
        """
        dat = self.set_data(self.get_hiv())
        return(dat)


    def set_epi(self):
        """
        Set the Surveillence data according to parameters supplied to the
        SetArgs object

        Parameters
        ----------
        None
        """
        dat = self.set_data(self.get_epi())
        return(dat)

    def get_repeat_testers(self, dat = None):
        """
        Get the repeat tester data from an HIV test dataset. Repeat-testers
        have a minimum of two valid HIV test dates of which the first test is
        an HIV-negative test result. 
        
        Parameters
        ----------
        dat : pandas dataframe
            a dataframe from self.set_hiv()
        """

        if (dat is None): dat = self.set_hiv()
        obs_start = utils.get_dates_min(dat, "HIVNegative", "obs_start")
        early_pos = utils.get_dates_min(dat, "HIVPositive", "early_pos")
        late_neg = utils.get_dates_max(dat, "HIVNegative", "late_neg")
        late_pos = utils.get_dates_max(dat, "HIVPositive", "late_pos")
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


