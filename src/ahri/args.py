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

    Methods
    -------
    set_path : set the root path to the ahri .dta datasets
    path_hiv_dta : str : change path name of hiv .dta dataset
    path_epi_dta : str : change path name of surviellance .dta dataset
    path_wgh_dta : str : change path name of women's .dta general health dataset
    path_mgh_dta : str : change path name of men's .dta general health dataset
    path_bst_dta : str : change path name of bounded structurs .dta dataset
    path_hiv_pkl : str : change path name of hiv .pkl dataset
    path_epi_pkl : str : change path name of surveillance .pkl dataset
    path_wgh_pkl : str : change path name of women's .pkl general health dataset
    path_mgh_pkl : str : change path name of men's .pkl general health dataset
    path_bst_pkl : str : change path name of bounded structurs .pkl dataset
    path_pip_pkl : str : change path name of pip .pkl dataset
    """

    def setpath(self, x): 
        """
        Paramaters
        ----------
        x : the name of the file to join with root folder
        """

        return os.path.join(self.root, x)

    def __init__(self, root):
        """
        Paramaters
        ----------
        root : the name of the root path to the AHRI datasets

        Attributes
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
        self.hiv_dta = self.setpath("RD05-99 ACDIS HIV All.dta")
        self.epi_dta = self.setpath("SurveillanceEpisodes.dta")
        self.wgh_dta = self.setpath("RD03-99 ACDIS WGH ALL.dta")
        self.mgh_dta = self.setpath("RD04-99 ACDIS MGH ALL.dta")
        self.bst_dta = self.setpath("RD01-03 ACDIS BoundedStructures.dta")
        self.hiv_pkl = self.setpath("ACDIS_HIV_All.pkl") 
        self.epi_pkl = self.setpath("SurveillanceEpisodes.pkl")
        self.wgh_pkl = self.setpath("ACDIS_WGH_ALL.pkl") 
        self.mgh_pkl = self.setpath("ACDIS_MGH_ALL.pkl") 
        self.bst_pkl = self.setpath("ACDIS_BoundedStructures.pkl")

    def path_hiv_dta(self, file = "RD05-99 ACDIS HIV All.dta"):
        self.hiv_dta = self.setpath(file)
        return self.hiv_dta

    def path_epi_dta(self, file = "SurveillanceEpisodes.dta"):
        self.epi_dta = self.setpath(file)
        return self.epi_dta

    def path_wgh_dta(self, file = "RD03-99 ACDIS WGH ALL.dta"):
        self.wgh_dta = self.setpath(file)
        return self.wgh_dta

    def path_mgh_dta(self, file = "RD04-99 ACDIS MGH ALL.dta"):
        self.mgh_dta = self.setpath(file)
        return self.mgh_dta

    def path_bst_dta(self, file = "RD01-03 ACDIS BoundedStructures.dta"):
        self.bst_dta = self.setpath(file)
        return self.bst_dta

    def path_hiv_pkl(self, file = "ACDIS_HIV_All.pkl"):
        self.hiv_pkl = self.setpath(file)
        return self.hiv_pkl

    def path_epi_pkl(self, file = "SurveillanceEpisodes.pkl"):
        return self.setpath(file)

    def path_wgh_pkl(self, file = "ACDIS_WGH_ALL.pkl"):
        self.epi_pkl = self.setpath(file)
        return self.epi_pkl

    def path_mgh_pkl(self, file = "ACDIS_MGH_ALL.pkl"):
        self.mgh_pkl = self.setpath(file)
        return self.mgh_pkl

    def path_bst_pkl(self, file = "ACDIS_BoundedStructures.pkl"):
        self.bst_pkl = self.setpath(file)
        return self.mgh_pkl

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


class SetArgs(SetFiles):
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
    """

    def __init__(self, root, 
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
        super().__init__(root)
        self.agecat = np.arange(np.min(list(age.values())),
          np.max(list(age.values())) + ageby, ageby)
        self.sdict = {"Fem": 1, "Mal": 0}
        self.sex = {s:self.sdict[s] for s in age.keys()}
        self.years = years
        self.age = age
        self.ageby = ageby
        self.nsim = nsim
        self.imp_method = imp_method
        self.mcores = mcores
        self.verbose = verbose
        self.drop_tasp = drop_tasp

    def update_years(self, years):
        self.years = years
        return self.years

    def update_age(self, age):
        """
        Update the age ranges for males ("Mal") and females ("Fem")

        Parameters
        ----------
        age : dict 
        """
        self.age = age
        self.sex = {s:self.sdict[s] for s in age.keys()}
        return self.age

    def update_ageby(self, ageby):
        self.ageby = ageby
        return self.ageby

    def update_impute_method(self, method):
        self.imp_method = method
        return self.imp_method

    def update_drop_tasp(self, drop):
        self.drop_tasp = drop
        return self.drop_tasp

    def update_nsim(self, nsim):
        self.nsim = nsim
        return self.nsim
