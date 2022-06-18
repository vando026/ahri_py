import os
import numpy as np
import multiprocessing as mp

class SetFiles:
    """
    A class for setting the root path and file paths to the AHRI datasets.

    Attributes
    ----------
    hiv_dta : str
        name of hiv .dta dataset
    epi_dta : str
        name of surviellance .dta dataset
    wgh_dta : str
        name of women's .dta general health dataset
    mgh_dta : str
        name of men's .dta general health dataset
    bst_dta : str
        name of bounded structurs .dta dataset
    hiv_pkl : str
        name of hiv .pkl dataset
    epi_pkl : str
        name of surviellance .pkl dataset
    wgh_pkl : str
        name of women's .pkl general health dataset
    mgh_pkl : str
        name of men's .pkl general health dataset
    bst_pkl : str
        name of bounded structures .pkl dataset
    pip_pkl : str
        name of pip .pkl dataset

    Methods
    -------
    set_path()
        set the root path to the ahri .dta datasets
    """

    def setpath(self, x): 
        """
        Paramaters
        ----------
        x : the name of the file to join with root folder
        """

        return os.path.join(self.root, x)

    def __init__(self, root, 
        hiv_dta = "RD05-99 ACDIS HIV All.dta",
        epi_dta = "SurveillanceEpisodes.dta",
        wgh_dta = "RD03-99 ACDIS WGH ALL.dta",
        mgh_dta = "RD04-99 ACDIS MGH ALL.dta", 
        bst_dta = "RD01-03 ACDIS BoundedStructures.dta",
        hiv_pkl = "ACDIS_HIV_All.pkl", 
        epi_pkl = "SurveillanceEpisodes.pkl",
        wgh_pkl = "ACDIS_WGH_ALL.pkl", 
        mgh_pkl = "ACDIS_MGH_ALL.pkl", 
        bst_pkl = "ACDIS_BoundedStructures.pkl",
        pip_pkl = "ACDIS_PIP.pkl"):
        """
        Paramaters
        ----------
        root : the name of the root path to the AHRI datasets
        hiv_dta : name of hiv .dta dataset
        epi_dta : name of surviellance .dta dataset
        wgh_dta : name of women's .dta general health dataset
        mgh_dta : name of men's .dta general health dataset
        bst_dta : name of bounded structurs .dta dataset
        hiv_pkl : name of hiv .pkl dataset
        epi_pkl : name of surveillance .pkl dataset
        wgh_pkl : name of women's .pkl general health dataset
        mgh_pkl : name of men's .pkl general health dataset
        bst_pkl : name of bounded structurs .pkl dataset
        pip_pkl : name of pip .pkl dataset
        """

        self.root = root
        self.hiv_dta = self.setpath(hiv_dta)
        self.epi_dta = self.setpath(epi_dta)
        self.wgh_dta = self.setpath(wgh_dta)
        self.mgh_dta = self.setpath(mgh_dta)
        self.bst_dta = self.setpath(bst_dta)
        self.hiv_pkl = self.setpath(hiv_pkl)
        self.epi_pkl = self.setpath(epi_pkl)
        self.wgh_pkl = self.setpath(wgh_pkl)
        self.mgh_pkl = self.setpath(mgh_pkl)
        self.bst_pkl = self.setpath(bst_pkl)
        self.pip_pkl = self.setpath(pip_pkl)

    def show_dta(self): 
        """
        Print out the file paths to the ahri .dta datasets
        """

        print(self.hiv_dta, self.epi_dta, self.bst_dta,
                self.mgh_dta, self.wgh_dta, sep = "\n")

    def show_pkl(self): 
        """
        Print out the file paths to the ahri .pkl datasets
        """

        print(self.hiv_pkl, self.epi_pkl, self.bst_pkl,
                self.mgh_pkl, self.wgh_pkl, sep = "\n")


class SetArgs:
    """
    A class for setting and storing user supplied parameters


    Attributes
    ----------
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
    hiv_dta : str
        name of hiv .dta dataset
    epi_dta : str
        name of surviellance .dta dataset
    wgh_dta : str
        name of women's .dta general health dataset
    mgh_dta : str
        name of men's .dta general health dataset
    bst_dta : str
        name of bounded structurs .dta dataset
    hiv_pkl : str
        name of hiv .pkl dataset
    epi_pkl : str
        name of surviellance .pkl dataset
    wgh_pkl : str
        name of women's .pkl general health dataset
    mgh_pkl : str
        name of men's .pkl general health dataset
    bst_pkl : str
        name of bounded structurs .pkl dataset
    pip_pkl : str
        name of pip .pkl dataset
    """

    def __init__(self, paths, 
        years = np.arange(2005, 2020),
        age = {"Fem": [15, 49], "Mal": [15, 54]}, 
        ageby = 5,
        drop_tasp = True, verbose = True,
        nsim = 1, imp_method = None,
        mcores = mp.cpu_count()):
        """Parameters
        -------------
        paths : object  
            an instance from SetFiles
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

        """

        self.agecat = np.arange(np.min(list(age.values())),
          np.max(list(age.values())) + ageby, ageby)
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
        self.hiv_dta = paths.hiv_dta
        self.epi_dta = paths.epi_dta        
        self.wgh_dta = paths.wgh_dta
        self.mgh_dta = paths.mgh_dta
        self.bst_dta = paths.bst_dta
        self.hiv_pkl = paths.hiv_pkl
        self.epi_pkl = paths.epi_pkl
        self.wgh_pkl = paths.wgh_pkl
        self.mgh_pkl = paths.mgh_pkl
        self.bst_pkl = paths.bst_pkl
        self.pip_pkl = paths.pip_pkl
