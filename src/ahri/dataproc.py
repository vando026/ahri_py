import pandas as pd
import numpy as np
from ahri.args import SetArgs
from ahri import utils
from functools import reduce

class DataProc:
    """
    A class that provides methods to read in the standard AHRI .dta files
    (Stata files), write them to .pkl format, and standardize data
    transformations across the datatsets.

    Attributes
    ----------

    Methods
    -------

    hiv_dta(self)
        read in the HIV .dta dataset

    epi_dta(self, addvars = None)
        read in the Surviellance .dta dataset

    bst_dta(self)
        read in the Bounded Structures .dta dataset

    get_hiv(self)
        load the HIV .pkl file into memory

    get_epi(self)
        load the Surveillance .pkl file into memory

    get_bst(self, write_pkl = True)
        load the Bounded Structures .pkl file into memory

    set_hiv(self, dat = None)
        set the HIV .pkl file according to user supplied arguments in the
        SetArgs class

    set_epi(self, dat = None)
        set the Surveillance .pkl file according to user supplied arguments in the
        SetArgs class

    set_data(self, dat)
        method to standardize transformation of the datasets

    get_repeat_testers(self, dat = None)
        method to create dataset of HIV repeat-testers

    get_birth_year(self)
        get birthdates from the Surveillance .pkl dataset

    calc_age(self, dat, name, ref_time)
        calculate age in years

    calc_age_cat(self, dat, name)
        calculate age categories 
    """

    def __init__(self, args):
        """ 
        Parameters
        ----------
        args : object 
            a SetArgs object
        """

        self.args = args

    def bst_dta(self, write_pkl = True):
        """ Read in the Bounded Structures .dta dataset, harmonize variable
        names. 

        Parameters
        ----------
        write_pk : bool :
            write the file to .pkl
        """

        dat = pd.read_stata(self.args.bst_dta) 
        dat = dat.rename(columns = {'BSIntId': 'BSIntID'})
        if write_pkl:
            dat.to_pickle(self.args.bst_pkl)
            print(f"File saved to {self.args.bst_pkl}\n")
        return(dat)

    def hiv_dta(self, write_pkl = True):
        """ 
        Read in the HIV .dta dataset, keep subset of HIV test variables,
        harmonize variable names, drop irregular values for Men/Women,
        keep only valid HIV test results, write the .pkl file

        Parameters
        ----------
        write_pk : bool :
            write the file to .pkl
        """

        dcols = ["IIntId", "ResidencyBSIntId", "VisitDate",
              "HIVResult", "Sex", "AgeAtVisit"]
        # if (addvars is not None):
            # dcols = dcols.append(addvars)
        hiv = pd.read_stata(self.args.hiv_dta, columns = dcols)
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
        if write_pkl:
            hiv.to_pickle(self.args.hiv_pkl)
            print(f"File saved to {self.args.hiv_pkl}\n")
        return(hiv)

    def epi_dta(self, addvars = None, write_pkl = True):     
        """ 
        Read in the Surveillance .dta dataset, keep subset of variables,
        harmonize variable names, drop irregular values for Men/Women,
        write the .pkl file

        Parameters
        ----------
        addvars: list 
            add variables to the subset of variables selected from the .dta dataset
        write_pk : bool :
            write the file to .pkl
        """

        if self.args.verbose:
            print("Reading data, this may take time...")
        dat = pd.read_stata(self.args.epi_dta)
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
        if write_pkl:
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
        Load the pickled Surveillance dataset into memory

        Parameters
        ----------
        None
        """

        dat = pd.read_pickle(self.args.epi_pkl)
        return(dat)

    def get_bst(self):
        """Load the pickled Bounded Structures dataset into memory

        Parameters
        ----------
        None
        """

        dat = pd.read_pickle(self.args.bst_pkl)
        return(dat)

    def set_data(self, dat):
        """
        Method to standardize the datasets by age, sex,  year, and area. The values
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
          dat = utils.drop_tasp(dat, self.bst_dta(write_pkl = False)) 
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


    def calc_age(self, dat, ref_time, name = "Age"):
        """
        Calculate the age in years with respect to a reference time. 
        
        Parameters
        ----------
        dat : pandas dataframe
            a dataframe from self.set_hiv()
        ref_time : obj : 
            a datetime object from which the year can be extracted
        name : str
            name of the new age variable
        """
        bdat = self.get_birth_year(edat, hdat)
        dat = pd.merge(dat,  bdat, on = "IIntID", how = "left")
        dat[name] = (pd.DatetimeIndex(dat[ref_time]).year -
                dat["BirthYear"])
        return dat

    def calc_age_cat(self, dat, name = "AgeCat"):
        """
        Calculate the age categories using values from args.agecat
        
        Parameters
        ----------
        dat : pandas dataframe
            a dataframe from self.set_hiv()
        name : str
            name of the new age variable
        """
        if "Age" not in dat.columns:
            print(f"ahri: Warning! Dataset needs an Age column to create Age categories")
        dat[name] = pd.cut(dat["Age"], self.args.agecat, 
                right = False, include_lowest = True)
        return dat

    def get_birth_year(self):
        """
        Get birthdates from the combined HIV and Surveillance .pkl datasets

        Parameters
        ----------
        None
        """

        hdat = pd.read_pickle(self.args.hiv_pkl)
        edat = pd.read_pickle(self.args.epi_pkl)
        edat["BirthYear"] = pd.DatetimeIndex(edat["DoB"]).year
        edat = edat[["IIntID", "BirthYear"]]
        hdat["BirthYear"] = pd.DatetimeIndex(hdat.VisitDate).year - hdat.Age
        hdat = hdat[["IIntID", "BirthYear"]]
        edat = pd.concat([edat, hdat], axis = 0)
        edat = edat.sort_values(["IIntID", "BirthYear"])
        edat = edat.groupby(["IIntID"]).first()
        return edat
