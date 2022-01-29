"""
## Description: Functions for reading data
## Project: ahri_py
## Author: AV / Created: 25Jan2022 
"""

import pandas as pd
import numpy as np
from ahri.args import SetFiles
from ahri import utils
import os


class Pickle:
    def __init__(self, paths):
        if (os.path.exists(os.path.join(paths.root, 'python'))):
            pass
        else:
            raise Exception(print(f"Create directory {paths.root}/python"))
        self.paths = paths

    def pip_dta(self):
        """ Read in PIP data to identify ACIDS from TASP areas"""
        dat = pd.read_stata(self.paths.bsifile, columns = ['BSIntId', 'PIPSA'])
        dat = dat.rename(columns = {'BSIntId': 'BSIntID'})
        dat.to_pickle(self.paths.pip_pkl)
        print(f"File saved to {self.paths.pip_pkl}\n")
        return(dat)

    def hiv_dta(self, drop15less = True, drop_tasp = True):
        """ Read in HIV data with arguments for setting data"""
        dcols = ["IIntId", "ResidencyBSIntId", "VisitDate",
              "HIVResult", "Sex", "AgeAtVisit"]
        # if (addvars is not None):
            # dcols = dcols.append(addvars)
        hiv = pd.read_stata(self.paths.hivfile, columns = dcols)
        hiv = hiv.rename(columns = {
          'IIntId':'IIntID',
          'ResidencyBSIntId':'BSIntID',
          'AgeAtVisit':'Age',
          'Sex':'Female'})
        if (drop_tasp): 
          hiv = utils.drop_tasp(self.paths.pip_pkl, hiv) 
        hiv = hiv[hiv.Female.isin(['Female', 'Male'])]
        hiv = hiv.assign(Female = (hiv.Female=='Female').astype(int))
        hiv = hiv.sort_values(['IIntID', 'VisitDate'])
        if (drop15less):
          hiv = hiv[hiv.Age.between(15, 100, inclusive=True)]
        hiv = hiv[hiv.HIVResult.isin(['Negative', 'Positive'])]
        hiv['HIVNegative'] = hiv.VisitDate[hiv.HIVResult == 'Negative']
        hiv['HIVPositive'] = hiv.VisitDate[hiv.HIVResult == 'Positive']
        hiv['Year'] = pd.DatetimeIndex(hiv.VisitDate).year
        hiv.to_pickle(self.paths.hiv_pkl)
        print(f"File saved to {self.paths.hiv_pkl}\n")
        return(hiv)

    def epi_dta(self, drop_tasp = True, addvars = None, read  ;):     
        print("Reading data, this may take time...")
        dat = pd.read_stata(self.paths.epifile)
        if ("CalendarYear" in dat.columns): 
            dat = dat.rename(columns = {'CalendarYear': 'Year'})
        if ("ARTStartedDate" in dat.columns):
            dat = dat.rename(columns = {'ARTStartedDate': 'EarliestARTInitDate'})
        dat = dat.rename(columns = {
            'IndividualId':'IIntID', 'LocationId':'BSIntID', 
            'Sex':'Female', 'Days':'ExpDays', 
            'StartDate':'ObservationStart',
            'EndDate':'ObservationEnd',
            'ModerntAssetIdx':'AssetIndex'})
        dcols = ['IIntID', 'BSIntID', 'Female', 'ExpDays',
                'ObservationStart', 'ObservationEnd', 'Year',
                'AssetIndex', 'Age', 'DoB', 'DoD', 
                'InMigration', 'OutMigration', 'Resident', 
                'OnART', 'EarliestARTInitDate']
        if (addvars is not None):
            dcols = [dcols, addvars]
            dcols = [col for slist in dcols for col in slist]
        dat = dat[dcols]
        dat = dat[dat.Female.isin(['Female', 'Male'])]
        dat = dat.assign(Female = (dat.Female=='Female').astype(int))
        # dat = dat.sort_values(['IIntID', 'ObservationStart'])
        if (drop_tasp): 
          dat = utils.drop_tasp(self.paths.pip_pkl, dat) 
        dat.to_pickle(self.paths.epi_pk)
        print(f"File saved to {self.paths.epi_pkl}\n")
        return(dat)
    

if __name__ == "__main__":
    from ahri.args import *
    from ahri.read import Pickle
    getfiles = SetFiles('/home/alain/Seafile/AHRI_Data/2020')
    dall = SetArgs(root = p2020)
    dat = Pickle(getfiles)
    dat.hiv_dta()
    dat.epi_dta()
