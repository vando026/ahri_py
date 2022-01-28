## Description: function to set Args
## Project: ahri_py
## Author: AV / Created: 17Jan2022 
import os
import numpy as np
import multiprocessing as mp

class SetFiles:

    def setpath(self, x): 
        return os.path.join(self.root, x)

    def __init__(self, root="~"):
        self.root = root
        self.hivfile = self.setpath("RD05-99 ACDIS HIV All.dta")
        self.epifile = self.setpath("SurveillanceEpisodes.dta")
        self.wghfile = self.setpath("RD03-99 ACDIS WGH ALL.dta")
        self.mghfile = self.setpath("RD04-99 ACDIS MGH ALL.dta") 
        self.bsifile = self.setpath("RD01-03 ACDIS BoundedStructures.dta")
        self.hiv_pkl = self.setpath("python/ACDIS_HIV_All.pkl") 
        self.epi_pkl = self.setpath("python/SurveillanceEpisodes.pkl")
        self.wgh_pkl = self.setpath("python/ACDIS_WGH_ALL.pkl") 
        self.mgh_pkl = self.setpath("python/ACDIS_MGH_ALL.pkl") 
        self.bsc_pkl = self.setpath("python/ACDIS_BoundedStructures.pkl")
        self.pip_pkl = self.setpath("python/ACDIS_PIP.pkl")

    def show_read(self): 
        print(self.hivfile, self.epifile, self.bsifile, sep = "\n")

    def show_pkl(self): 
        print(self.hiv_pkl, self.epi_pkl, self.pip_pkl, sep = "\n")



class SetArgs:
    def __init__(self, root = "~",
        years = np.arange(2005, 2020),
        age = {"Fem": [15, 49], "Mal": [15, 54]}, 
        agecat = None, ageby = 5,
        nsim = 1, imputeMethod = None,
        aname = 'filename',
        mcores = mp.cpu_count(),
        # setFun = identity,
        # addVars = identity,
        more_args = None):
        # set age cat
        if (agecat is None):
            self.agecat = np.arange(np.min(list(age.values())),
              np.max(list(age.values())) + ageby, ageby)
        # codes for sex
        sdict = {"Fem": 1, "Mal": 0}
        self.sex = {s:sdict[s] for s in age.keys()}
        self.years = years
        self.age = age
        self.ageby = ageby
        self.nsim = nsim
        self.imputeMethod = imputeMethod
        self.aname = aname
        self.mcores = mcores
        self.root = root


if __name__ == "main":
    d2020 = SetFiles('/home/alain/Seafile/AHRI_Data/2020')
    fem = SetArgs(root = d2020, age = {"Fem": [15, 49]})
    print(fem.root.hivfile)
