import os
import numpy as np
# TODO: does mp need to be here
import multiprocessing as mp

class SetFiles:

    def setpath(self, x): 
        return os.path.join(self.root, x)

    def __init__(self, root = "~"):
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
        # Check if folder exists
        # TODO: allow user to change its name
        if (os.path.exists(os.path.join(root, 'python'))):
            pass
        else:
            print(f"ahri: Warning! check if directory {root}/python exists")


    def show_read(self): 
        print(self.hivfile, self.epifile, self.bsifile, sep = "\n")

    def show_pkl(self): 
        print(self.hiv_pkl, self.epi_pkl, self.pip_pkl, sep = "\n")




class SetArgs(SetFiles):
    def __init__(self, 
        root = "/home/alain/",
        years = np.arange(2005, 2020),
        age = {"Fem": [15, 49], "Mal": [15, 54]}, 
        agecat = None, ageby = 5,
        drop_tasp = True, verbose = True,
        nsim = 1, imp_method = None,
        mcores = mp.cpu_count()):
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
        self.imp_method = imp_method
        self.mcores = mcores
        self.verbose = verbose
        self.drop_tasp = drop_tasp
        SetFiles.__init__(self, root)
