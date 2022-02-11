from datetime import datetime
from ahri.dataproc import DataProc
from ahri.utils import *
from ahri.cyth import split_datax, age_adjustx, pre_splitx
import multiprocessing as mp
import scipy
import sys

def prep_for_imp(dat, origin = datetime(2000, 1, 1)):
    """Prepare repeat-tester data for imputation"""
    # get testdate in days since 2000-1-1
    dat['obs_start_'] = (dat['obs_start'] - origin).dt.days
    dat['late_neg_'] = (dat['late_neg'] - origin).dt.days
    dat['early_pos_'] = (dat['early_pos'] - origin).dt.days
    dat = dat[["IIntID", "obs_start_", "late_neg_", 
        "early_pos_", "sero_event", "Age"]]
    dat = dat.to_numpy()
    # split data by seroevent
    dat0 = dat[ np.isnan(dat[:, 3]), :]
    dat1 = dat[~np.isnan(dat[:, 3]), :]
    return([dat0, dat1])

def imp_random(dat1):
    """Impute random dates in censored interval"""
    idates = np.random.randint(dat1[:, 2] + 1,  dat1[:, 3])
    return(np.c_[dat1, idates])

def imp_midpoint(dat1):
    """Impute mid-point dates in censored interval"""
    idates = np.floor((dat1[:, 2] +  dat1[:, 3]) / 2)
    return(np.c_[dat1, idates])

def split_data(dat, args):
    """Split repeat-tester data into episodes""" 
    ndat0 = dat[0][:, [0, 1, 2,  4, 5]]
    # replace early_pos with imp date at 6
    ndat1 = dat[1][:, [0, 1, 6,  4, 5]]
    ndat = np.concatenate([ndat0, ndat1],
            dtype = np.intc, casting = 'unsafe')
    pdat = pre_splitx(ndat) 
    edat = split_datax(pdat)
    # aggregate the data by agecat and year
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


def calc_gamma(dat, pop_dat):
    years = np.unique(dat.Year.values)
    dat = dat.iloc[:, [0, 2, 3]].to_numpy()
    pop_dat = pop_dat.iloc[:, [0, 2]].to_numpy()
    out = [age_adjustx(
        dat[dat[:, 0] == year, 1],
        dat[dat[:, 0] == year, 2],
        pop_dat[pop_dat[:, 0] == year, 1])
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
        self.idat = prep_for_imp(self.rtdat)
        self.pop_n = get_pop_n(self.edat, self.args)


    def inc_midpoint(self, age_adjust = True):
        self.idat[1] = imp_midpoint(self.idat[1]) 
        sdat = split_data(self.idat, self.args)
        if (age_adjust is not True):
            self.pop_n["N"] = 1
        res = calc_gamma(sdat, self.pop_n)
        res = est_combine(res)
        return(res)

    def do_rand_imp(self, i):
        # you have to reset random seed for each process
        if self.args.verbose:
            timer(i, self.args.nsim)
        np.random.seed()
        self.idat[1] = imp_random(self.idat[1]) 
        sdat = split_data(self.idat, self.args)
        res = calc_gamma(sdat, self.pop_n)
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
        return(res)


