from datetime import datetime
from ahri.dataproc import DataProc
from ahri.utils import *
from ahri.pyx.ptime import split_long
import statsmodels.api as sm
import multiprocessing as mp
import scipy
import sys

def prep_for_imp(rtdat, origin = datetime(1970, 1, 1)):
    """Prepare rtdat for imputation"""
    ndat = rtdat[-pd.isna(rtdat['early_pos'])]
    ndat = ndat[["IIntID", "late_neg", "early_pos"]]
    ndat['late_neg_'] = (ndat['late_neg'] - origin).dt.days
    ndat['early_pos_'] = (ndat['early_pos'] - origin).dt.days
    ndat = ndat[["IIntID", "late_neg_", "early_pos_"]]
    return(ndat.to_numpy())

def imp_random(rtdat):
    """Impute random dates in censored interval"""
    idates = np.random.randint(rtdat[:, 1] + 1,  rtdat[:, 2])
    ndat = pd.DataFrame({"IIntID": rtdat[:, 0], "serodate": idates})
    return(ndat)

def imp_midpoint(rtdat):
    """Impute mid-point dates in censored interval"""
    idates = np.floor((rtdat[:, 1] +  rtdat[:, 2]) / 2)
    ndat = pd.DataFrame({"IIntID": rtdat[:, 0], "serodate": idates})
    return(ndat)


def prep_for_split(rtdat, imdat):
    """Prepare a dataset for splitting into episodes"""
    imdat['serodate'] = pd.to_datetime(imdat['serodate'], unit='d')
    dat = pd.merge(rtdat, imdat, how = 'left', on = 'IIntID')
    dat['obs_end'] = np.where(dat["sero_event"]==1, 
            dat['serodate'], dat['late_neg'])
    idat = np.array([
        dat["obs_start"].dt.day_of_year,
        dat["obs_end"].dt.day_of_year,
        dat["obs_start"].dt.year,
        dat["obs_end"].dt.year,
        dat["sero_event"],
        dat["Age"]])
    return(idat.T)

# def split_long(di):
#     """Get the person-time contributions"""
#     ylen = (di[3] - di[2]) + 1
#     index = np.arange(ylen) 
#     yi = di[2] + index
#     ag = di[5] + index
#     ei = np.zeros(ylen, dtype = int)
#     ei[ylen - 1] = di[4]
#     if (ylen == 1):
#         ptime = np.array(di[1] - di[0])
#     else:
#         ptime = np.array([365 - di[0], di[1]], dtype = int)
#         if (ylen > 2):
#             ptime = np.insert(ptime, 1, np.repeat(365, ylen - 2))
#     out = np.c_[yi, ptime, ei, ag]
#     return(out)

# def split_long(di, tab):
#     """Get the person-time contributions"""
#     dt = tab[(tab[:, 0] >= di[2]) & (tab[:, 0] <= di[3])]
#     age = np.arange(dt.shape[0]) + di[5]
#     dt[-1, 2] = di[4]
#     dt[-1, 1] = di[1]
#     dt[0, 1] = dt[0, 1] - di[0]
#     return(np.c_[dt, age])

def split_data(predat, args):
    """Split repeat-tester data into episodes""" 
    edat = [split_long(predat[di]) 
            for di in range(predat.shape[0])]
    dat = pd.DataFrame(np.vstack(edat), 
            columns = ["Year", "Days", "Event", "Age"])
    dat["PYears"] = dat["Days"] / 365
    dat["AgeCat"] = pd.cut(dat["Age"], 
            bins = args.agecat, include_lowest=True)
    dat = dat.groupby(["Year", "AgeCat"]).agg(
            Events = pd.NamedAgg("Event", sum),
            PYears = pd.NamedAgg("PYears", sum)
            ).reset_index()
    return(dat)


def age_adjust(count, pop, stpop):
    """Use gamma distribution and direct method for incidence rates"""
    if (all(x > 0 for x in pop) is not True):
        return([0, 0])
    rate = count / pop
    stdwt = stpop / np.sum(stpop)
    dsr = np.sum(stdwt * rate)
    dsr_var = sum((stdwt**2) * (count/pop**2))
    res = [dsr, dsr_var]
    return(res)

def calc_gamma(dat, pop_dat):
    years = np.unique(dat.Year.values)
    out = [age_adjust(
        dat.loc[dat.Year == year, "Events"],
        dat.loc[dat.Year == year, "PYears"],
        pop_dat.loc[dat.Year == year, "N"])
            for year in years]
    out = np.c_[years, out]
    return(out)


def calc_rubin(rates, variances, year = 0):
    m = len(rates)
    # mean est
    cbar = np.mean(rates)
    # var within
    vbar = np.mean(variances)
    if (m == 1):
        df = 1.96
    else:
        # var between
        evar = np.sum((rates - cbar)**2) / (m - 1)
        variances = vbar + evar * (m + 1)/ m
        r = (1 + 1/m) * evar/vbar
        df = (m - 1) * (1 + 1/r)**2
    se = np.sqrt(variances)
    # Calc 95\% CI
    crit = scipy.stats.t.ppf(1 - 0.05/2, df)
    lci = cbar - (crit * se)
    uci = cbar + (crit * se)
    if (m ==1): 
        lci = lci[0]; uci = uci[0]; se = se[0]
    res = [year, cbar, se, lci, uci]
    return(res)

def est_combine(est):
    sp_est = [est[est[:, 0] == k] 
            for k in np.unique(est[:, 0])]
    res = [calc_rubin(x[:, 1], x[:, 2], x[0, 0]) 
            for x in sp_est]
    out = pd.DataFrame(res, 
            columns = ["Year", "Rate",  "SE", "LCI", "UCI"])
    out["Year"] = out["Year"].astype(int)
    return(out)


class CalcInc(DataProc):
    def __init__(self, args):
        DataProc.__init__(self, args)
        self.hdat = self.set_hiv()
        self.edat = self.set_epi()
        self.bdat = get_birth_date(self.edat)
        self.rtdat = self.get_repeat_testers(self.hdat)
        self.rtdat = add_year_test(self.rtdat, self.bdat)
        self.pidat = prep_for_imp(self.rtdat)
        self.pop_n = get_pop_n(self.edat, self.args)


    def inc_midpoint(self, age_adjust = True):
        imdat = imp_midpoint(self.pidat) 
        sdat = prep_for_split(self.rtdat, imdat)
        mdat = split_data(sdat, self.args)
        if (age_adjust is not True):
            self.pop_n["N"] = 1
        res = calc_gamma(mdat, self.pop_n)
        res = est_combine(res)
        return(res)


    def do_rand_imp(self, i):
        # you have to reset random seed for each process
        timer(i, self.args.nsim)
        np.random.seed()
        imdat = imp_random(self.pidat) 
        sdat = prep_for_split(self.rtdat, imdat)
        mdat = split_data(sdat, self.args)
        res = calc_gamma(mdat, self.pop_n)
        return(res)

    def inc_randpoint(self, age_adjust = True):
        if (age_adjust is not True):
            self.pop_n["N"] = 1
        # use parallel processing
        pool = mp.Pool(self.args.mcores) 
        res = pool.map_async(self.do_rand_imp,
                [i for i in range(self.args.nsim)])
        results = np.vstack(res.get())
        pool.close(); pool.join()
        res = est_combine(results)
        print('\n')
        return(res)


if __name__ == '__main__':
    import time
    import ahri
    import numpy as np
    from  ahri.args import SetArgs
    from ahri.pyx.ptime import split_long
    from ahri.calc import *
    from ahri.utils import get_birth_date, add_year_test

    data2020 = '/home/alain/Seafile/AHRI_Data/2020'
    dfem = SetArgs(root = data2020, nsim = 1, years = np.arange(2005, 2020),
        age = {"Fem": [15, 49]})

    xx = CalcInc(dfem)
    # print(xx.inc_midpoint(age_adjust  = False))
    # print(xx.inc_randpoint(age_adjust = False))
    t1 = time.time()
    print(xx.inc_randpoint(age_adjust = True))
    t2 = time.time()
    print(t2 - t1)

    hdat = xx.set_hiv()
    edat = xx.set_epi()
    bdat = get_birth_date(edat)
    rtdat = xx.get_repeat_testers(hdat)
    rtdat = add_year_test(rtdat, bdat)
    pidat = prep_for_imp(rtdat)
    pop_n = get_pop_n(edat, dfem)
    imdat = imp_midpoint(pidat) 
    sdat = prep_for_split(rtdat, imdat)


    t1 = time.time()
    edat = [split_long(sdat[di]) for di in range(sdat.shape[0])]
    dat = pd.DataFrame(np.vstack(edat), 
            columns = ["Year", "Days", "Event", "Age"])
    dat["PYears"] = dat["Days"] / 365
    dat["AgeCat"] = pd.cut(dat["Age"], 
            bins = dfem.agecat, include_lowest=True)
    dat = dat.groupby(["Year", "AgeCat"]).agg(
            Events = pd.NamedAgg("Event", sum),
            PYears = pd.NamedAgg("PYears", sum)
            ).reset_index()
    t2 = time.time()
    print(t2 - t1)



    # s1 = np.array([17, 153, 254, 2005, 2014, 1, 37])
    t1 = time.time()
    mdat = split_data(sdat, dfem)
    t2 = time.time()
    print(t2 - t1)

#     t1 = time.time()
#     xx.inc_randpoint()
#     t2 = time.time()
#     print(t2 - t1)
