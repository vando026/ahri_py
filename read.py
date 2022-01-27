"""
## Description: Functions for reading data
## Project: ahri_py
## Author: AV / Created: 25Jan2022 
"""

import pandas as pd
import numpy as np
from ahri.args import SetFiles
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
        print(dat.head())

    def hiv_dta(self, drop15less = True, drop_tasp=True):
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
        hiv = hiv[hiv.Female.isin(['Female', 'Male'])]
        if (drop_tasp): 
          hiv = drop_tasp(self.paths.pip_pkl, hiv) 
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
        print(hiv.head())

    # def epi_dta(self, drop_tasp = True, addvars = None):     
    #     dat = pd.read_stata(self.paths.epifile)
    #     breakpoint()

    #     if ("CalendarYear" in dat.columns): 
    #         print("ahri: Renaming CalendarYear to Year")
    #         dat = dat.rename(columns = {'CalendarYear': 'Year'})
    #     if ("ARTStartedDate" in dat.columns):
    #         print("ahri: Renaming ARTStartedDate to EarliestARTInitDate")
    #         dat = dat.rename(columns = {'ARTStartedDate': 'EarliestARTInitDate'})
    #     dat = dat.rename(columns = {
    #         'IIntID':'IndividualId', 'BSIntID':'LocationId', 
    #         'Female':'Sex', 'ExpDays':'Days', 
    #         'ObservationStart':'StartDate',
    #         'ObservationEnd':'EndDate',
    #         'AssetIndex':'ModerntAssetIdx'})
    #     dcols = ['IIntID', 'BSIntID', 'Female', 'ExpDays',
    #             'ObservationStart', 'ObservationEnd', 'Year',
    #             'AssetIndex', 'Age', 'DoB', 'DoD', 
    #             'InMigration', 'OutMigration', 'Resident', 
    #             'OnART', 'EarliestARTInitDate']
    #     if (addvars is not None)
    #     dcols = np.array(dcols.append(addvars))
    #     dcols = dcols.flatten()
    #     dat = dat[dcols]
    #     return(dat)



#readEpisodes <- function(
#  inFile=NULL, outFile=NULL, 
#  dropTasP=TRUE, addVars=" ",
#  write_rda=TRUE, nstart = 0, nrow=Inf) {
#  #
#  if (is.null(inFile)) {
#    check_getFiles()
#    inFile=getFiles()$epifile
#  }
#  if(is.null(outFile)) {
#    check_getFiles()
#    outFile=getFiles()$epi_rda
#  }
#  message(sprintf("ahri: Reading %s, this may take a while...", inFile))
#  dat <- haven::read_dta(inFile, skip = nstart, n_max = nrow) 
#  # Variable names changed from releases
#  if ("CalendarYear" %in% names(dat)) {
#    message("ahri: Renaming CalendarYear to Year")
#    names(dat)[names(dat) == "CalendarYear"] <- "Year"
#  } 
#  if ("ARTStartedDate" %in% names(dat)) { 
#    message("ahri: Renaming ARTStartedDate to EarliestARTInitDate")
#    names(dat)[names(dat)=="ARTStartedDate"] <- "EarliestARTInitDate"
#  }
#  dat <- select(dat,
#    IIntID=IndividualId, BSIntID=LocationId, 
#    Female=Sex, Age, DoB, DoD,
#    Year, ExpDays=Days,
#    ObservationStart=StartDate,
#    ObservationEnd=EndDate,
#    InMigration, OutMigration,
#    Resident, AssetIndex=ModerntAssetIdx,
#    OnART, EarliestARTInitDate, matches(addVars))
#  dat <- filter(dat, Female %in% c(1,2))
#  dat <- mutate(dat,
#    IIntID=as.integer(IIntID),
#    BSIntID=as.integer(BSIntID),
#    Year=as.integer(Year),
#    Female=as.integer(ifelse(Female==2, 1, 0)))
#  if (dropTasP==TRUE) dat <- dropTasPData(dat)
#  dat <- arrange(dat, IIntID, ObservationStart)
#  if (write_rda) saveRDS(dat, outFile)
#  dat
#}
    




if __name__ == "__main__":
    from ahri.args import SetFiles, SetArgs
    getfiles = SetFiles('/home/alain/Seafile/AHRI_Data/2020')
    dall = SetArgs(root = p2020)
    dat = ahri.read.Pickle(getfiles)
    hiv1 = get_hiv(dall)

