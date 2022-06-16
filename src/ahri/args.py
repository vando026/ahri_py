import os
import numpy as np
# TODO: does mp need to be here
import multiprocessing as mp

class SetFiles:
    """
    A class for setting the root path and file paths to the AHRI datasets.

    Attributes
    ----------
    hivfile : str
        name of hiv .dta dataset
    epifile : str
        name of surviellance .dta dataset
    wghfile : str
        name of women's .dta general health dataset
    mghfile : str
        name of men's .dta general health dataset
    bsifile : str
        name of bounded structurs .dta dataset
    hiv_pkl : str
        name of hiv .pkl dataset
    epi_pkl : str
        name of surviellance .pkl dataset
    wgh_pkl : str
        name of women's .pkl general health dataset
    mgh_pkl : str
        name of men's .pkl general health dataset
    bsc_pkl : str
        name of bounded structurs .pkl dataset
    pip_pkl : str
        name of pip .pkl dataset

    Methods
    -------
    set_path()
        set the root path to the ahri .dta datasets
    show_read()
        shows the read paths to the .dta datasets
    show_pkl()
        shows the write paths to the .pkl files
    """

    def setpath(self, x): 
        """
        Paramaters
        ----------
        x : the name of the file to join with root folder
        """

        return os.path.join(self.root, x)

    def __init__(self, root = "~"):
        """
        Paramaters
        ----------
        root : the name of the root path to the AHRI datasets
        """

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
        """
        Print out the file paths to the ahri .dta datasets
        """

        print(self.hivfile, self.epifile, self.bsifile, sep = "\n")

    def show_pkl(self): 
        """
        Print out the file paths to the ahri .pkl datasets
        """

        print(self.hiv_pkl, self.epi_pkl, self.pip_pkl, sep = "\n")




class SetArgs(SetFiles):
    """
    A class for setting and storing user supplied parameters


    Attributes
    ----------
    See the parameters values documented below
    """

    def __init__(self, 
        root = "/home/alain/",
        years = np.arange(2005, 2020),
        age = {"Fem": [15, 49], "Mal": [15, 54]}, 
        agecat = None, ageby = 5,
        drop_tasp = True, verbose = True,
        nsim = 1, imp_method = None,
        mcores = mp.cpu_count()):
        """Parameters
        -------------
        root : str  
            the path to the release year folder with the AHRI datasets
        years : list 
            keep only observations from the specified years
        age : dict 
            set the age ranges for males ("Mal") and females ("Fem")
        agecat: list 
            a list of age intervals to great age groups
        ageby : int  
            if agecat is None, age categories are created using the 
            age min/max and ageby values
        nsim : int  
            number of imputations for the HIV seroconversion dates
        drop_tasp : bool 
            drop observations from the Northern (TasP) areas
        impute_method: str 
            type of imputation: random-point or midpoint
        mcores : int 
            number of cores to use for incidence rate estimation, 
            uses the multiprocessing library to select cores
        verbose : bool 
            show the progress bar
        """

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
