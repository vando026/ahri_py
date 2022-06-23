import pandas as pd
import numpy as np
from ahri.args import SetArgs
from ahri import utils
from functools import reduce



class DataProc:
    """
    A class that provides methods to read in the standard AHRI .dta files
    (Stata files) and write them to .pkl format.

    Attributes
    ----------

    Methods
    -------

    proc_hiv_dta(self)
        read/write the HIV .dta dataset

    proc_epi_dta(self, addvars = None)
        read/write the Surviellance .dta dataset

    proc_bst_dta(self)
        read in the Bounded Structures .dta dataset
    """

    def __init__(self, args):
        """ 
        Parameters
        ----------
        args : object 
            a SetArgs object
        """
        self.args = args

    def proc_bst_dta(self, write_pkl = True):
        """ Read in the Bounded Structures .dta dataset, harmonize variable
        names. 

        Parameters
        ----------
        write_pk : bool :
            write the file to .pkl
        """
        # Pandas throws an error for Isigodi
        dcols = ["BSIntId", "PIPSA", "IsUrbanOrRural"]
        dat = pd.read_stata(self.args.bst_dta, columns = dcols) 
        dat = dat.rename(columns = {'BSIntId': 'BSIntID'})
        if write_pkl:
            dat.to_pickle(self.args.bst_pkl)
            print(f"File saved to {self.args.bst_pkl}\n")
        return(dat)

    def proc_hiv_dta(self, write_pkl = True):
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

    def proc_epi_dta(self, addvars = None, write_pkl = True):     
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

class SetAtInit:
    """
    A class that provides methods to standardize data transformations 
    across the datatsets.

    Methods
    -------

    set_data(self, dat)
        method to standardize transformation of the datasets

    get_repeat_testers(self, dat = None)
        method to create dataset of HIV repeat-testers

    calc_age(self, dat, name, ref_time)
        calculate the age in years

    """

    def __init__(self, args):
        """ 
        Parameters
        ----------
        args : object 
            a SetArgs object
        """
        self.args = args 

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
          dat = utils.drop_tasp(dat, pd.read_pickle(self.args.bst_pkl))
        return(dat)

    def get_repeat_testers(self, dat):
        """
        Get the repeat tester data from an HIV test dataset. Repeat-testers
        have a minimum of two valid HIV test dates of which the first test is
        an HIV-negative test result. 
        
        Parameters
        ----------
        dat : pandas dataframe
            a dataframe from from self.hiv_data
        """

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
        ref_time : obj : 
            a datetime object from which the year can be extracted
        name : str
            name of the new age variable
        """
        bdat = self.get_birth_year()
        dat = pd.merge(dat,  bdat, on = "IIntID", how = "left")
        dat[name] = (pd.DatetimeIndex(
            dat[ref_time]).year - dat["BirthYear"])
        return dat


class SetData(SetAtInit):
    """
    A class that provides methods to read in the standard AHRI .dta files
    (Stata files), write them to .pkl format, and standardize data
    transformations across the datatsets.

    Attributes
    ----------
    hiv_data 
       the hiv dataset that has been transformed using the SetArgs attributes 

    epi_data 
       the surveillance episodes dataset that has been transformed using 
       the SetArgs attributes 

    bst_data 
       the bounded structures dataset, needed to drop PIP areas

    Methods
    -------
    get_birth_year(self)
        get the year of birth from the HIV and Surveillance .pkl datasets

    calc_age_cat(self, dat, name)
        calculate age categories 

    get_pop_n(self)
        get number of all participants under surveillance by year and age group
    """

    def __init__(self, args):
        super().__init__(args)
        self.args = args
        self.hiv_data = self.set_data(pd.read_pickle(self.args.hiv_pkl))
        self.epi_data = self.set_data(pd.read_pickle(self.args.epi_pkl))
        self.bst_data = pd.read_pickle(self.args.bst_pkl) 
        rtdat  = self.get_repeat_testers(self.hiv_data)
        self.repeat_tester_data = self.calc_age(rtdat, ref_time = "late_neg")

    def get_birth_year(self):
        """
        Get birthdates from the combined HIV and Surveillance .pkl datasets

        Parameters
        ----------
        None
        """

        edat = self.epi_data
        edat["BirthYear"] = pd.DatetimeIndex(edat["DoB"]).year
        edat = edat[["IIntID", "BirthYear"]]
        hdat = self.hiv_data
        hdat["BirthYear"] = pd.DatetimeIndex(hdat.VisitDate).year - hdat.Age
        hdat = hdat[["IIntID", "BirthYear"]]
        dat = pd.concat([edat, hdat], axis = 0)
        dat = dat.sort_values(["IIntID", "BirthYear"])
        dat = dat.groupby(["IIntID"]).first()
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

    def get_pop_n(self):
        """
        Get number of all participants under surveillance by year and age group

        Parameters
        ----------
        None
        """
        edat = self.calc_age_cat(self.epi_data)
        dat = edat.groupby(["Year", "AgeCat"]) \
            .agg(N = pd.NamedAgg("IIntID", len)) \
            .reset_index()
        return dat
