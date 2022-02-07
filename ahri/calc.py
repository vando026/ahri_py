from ahri.dataproc import DataProc
from ahri.utils import *
import statsmodels.api as sm
import scipy

def prep_for_split(rtdat, imdat):
    """Prepare a dataset for splitting into episodes"""
    dat = pd.merge(rtdat, imdat, how = 'left', on = 'IIntID')
    dat['obs_end'] = np.where(dat["sero_event"]==1, 
            dat['serodate'], dat['late_neg'])
    idat = np.array([dat.IIntID, 
        dat["obs_start"].dt.day_of_year,
        dat['obs_end'].dt.day_of_year,
        dat["obs_start"].dt.year,
        dat['obs_end'].dt.year,
        dat["sero_event"]])
    return(idat.T)


# This algorithm is implemented as a cython function 
# def agg_inc(di, events, ptimes):
#     """Get the person-time contributions"""
#     syear = di[3]
#     eyear = di[4]
#     sday = di[1]
#     eday = di[2]
#     sero = di[5]
#     events[eyear] += sero
#     if (eyear - syear == 0):
#         ptimes[eyear] += eday - sday
#     else:
#         ptimes[syear] += 365 - sday
#         ptimes[eyear] += eday
#         if (eyear - syear > 2):
#             for y in range(syear + 1, eyear): 
#                 ptimes[y] += 365


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
    ndat['serodate'] = pd.to_datetime(ndat['serodate'], unit='d')
    return(ndat)

def imp_midpoint(rtdat):
    """Impute mid-point dates in censored interval"""
    mdates = np.floor((rtdat[:, 1] +  rtdat[:, 2]) / 2)
    ndat = pd.DataFrame({"IIntID": rtdat[:, 0], "serodate": mdates})
    ndat['serodate'] = pd.to_datetime(ndat['serodate'], unit='d')
    return(ndat)


def get_ptime_long(di):
    """Get the person-time contributions"""
    yi = np.arange(di[3], di[4] + 1, dtype = int)
    ylen = len(yi)
    ei = np.zeros(ylen)
    ei[ylen - 1] = di[5]
    if (ylen == 1):
        ptime = di[2] - di[1]
    else:
        ptime = np.array([365 - di[1], di[2]], dtype = int)
        if (ylen > 2):
            ptime = np.insert(ptime, 1, np.repeat(365, ylen - 2))
    out = np.array([np.repeat(di[0], ylen), yi, ptime, ei], dtype = int)
    return(out.T)

def split_data(predat, bdat, args):
    """Split repeat-tester data into episodes""" 
    edat = [get_ptime_long(predat[di]) for di in range(predat.shape[0])]
    dat = pd.DataFrame(np.vstack(edat), 
            columns = ["IIntID", "Year", "Days", "Event"])
    dat["PYears"] = dat["Days"] / 365
    dat = dat[dat['PYears'] != 0]
    dat["tscale"] = np.log(dat["PYears"])
    dat = pd.merge(dat, bdat, how = "inner", on = "IIntID")
    dat["Age"] = dat["Year"] - dat["YoB"]
    dat["AgeCat"] = pd.cut(dat["Age"], 
            bins = args.agecat, include_lowest=True)
    dat = dat.groupby(["Year", "AgeCat"]).agg(
            Events = pd.NamedAgg("Event", sum),
            PYears = pd.NamedAgg("PYears", sum)
            ).reset_index()
    return(dat)



def calc_pois(dat, ndat, formula = "Event ~ -1"):
    """Calc incidence using Poisson model"""
    model = sm.GLM.from_formula(formula, 
            offset = dat["tscale"], data = dat, 
            family = sm.families.Poisson(sm.families.links.log())).fit()
    res = model.get_prediction(ndat)
    return(res.summary_frame())

def age_adjust(count, pop, stpop):
    """Use gamma distribution and direct method for incidence rates"""
    if (all(x > 0 for x in pop) is not True):
        return([0, 0])
    rate = count / pop
    stdwt = stpop / np.sum(stpop)
    dsr = np.sum(stdwt * rate)
    dsr_var = sum((stdwt**2) * (count/pop**2))
    # wm = np.max(stdwt / pop)
    # alpha = 1 - conf_level
    # gamma_lci = scipy.stats.gamma.ppf(alpha/2,
    #         a = (dsr**2)/dsr_var, scale = dsr_var/dsr)
    # gamma_uci = scipy.stats.gamma.ppf(1 - alpha/2, 
    #         a = ((dsr + wm)**2) / 
    #         (dsr_var + wm**2), scale = (dsr_var + wm**2)/(dsr + wm))
    # res = {"rate": dsr, "crude": cruderate, "var": dsr_var, 
            # "lci": gamma_lci, "uci": gamma_uci }
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


def calc_nubin(rates, variances, m):
    breakpoint()
    # mean est
    cbar = np.mean(rates)
    # var within
    vbar = np.mean(variances)
    if (m == 1):
        df = 1.96
    else:
        r = (1 + 1/m) * evar/vbar
        df = (m - 1) * (1 + 1/r)**2
        # var between
        evar = np.sum((rates - cbar)**2) / (m - 1)
        variances = vbar + evar * (m + 1)/ m
    se = np.sqrt(variances)
    # Calc 95\% CI
    crit = scipy.stats.t.ppf(1 - 0.05/2, df)
    lci = cbar - (crit * se)
    uci = cbar + (crit * se)
    res = np.c_[cbar, lci, uci]
    return(res)

# calcRubin <- function(est, se, fun=exp) {
#   doCalc <- function(est, se, func=fun) {
#     m <- length(est)
#     mn <- mean(est)
#     if (m > 1) {
#       var_with <- mean(se^2)
#       var_betw <- sum((est - mn)^2)/(m-1)
#       se <- sqrt(var_with + var_betw*(1 + (1/m)))
#       rdf <- (m - 1) * (1 + (var_with/((1+ (1/m)) * var_betw)))^2
#       tdf <- qt(1 - (0.05/2), rdf)
#     } else {
#       tdf <- 1.96 
#     }
#     ci <- func(mn + c(-1, 1) * (tdf * se))
#     c(rate=func(mn), lci=ci[1], uci=ci[2])
#   }


class CalcInc(DataProc):
    def __init__(self, args):
        DataProc.__init__(self, args)
        self.hdat = self.set_hiv()
        self.edat = self.set_epi()
        self.bdat = get_birth_date(self.edat)
        self.rtdat = self.get_repeat_testers(self.hdat)
        self.pidat = prep_for_imp(self.rtdat)
        self.pdat_yr = pred_dat_year(self.args)
        self.pdat_yr_age = pred_dat_age_year(self.edat)
        self.pop_n = get_pop_n(self.edat, self.args)

    def gamma_mid(self, age_adjust = True):
        """Gamma HIV incidence using mid-point imputation"""
        imdat = imp_midpoint(self.pre_imp_dat) 
        sdat = prep_for_split(self.rtdat, imdat)
        mdat = split_data(sdat, self.bdat, self.args)
        if (age_adjust == False):
            self.pop_n["N"] = 1 
        res = calc_gamma(mdat, self.pop_n, out, i = 1)
        return(res[0, 0])

    def time_inc(self, i):
        """Add timer to the calculate inc rate function"""
        if (self.args.verbose):
            j = (i + 1) / self.args.nsim
            sys.stdout.write('\r')
            sys.stdout.write("[%-20s] %d%%" % ('='*int(20*j), 100 * j))
            sys.stdout.flush()
            # sleep(0.0005)
        # you have to reset random seed for each process
        np.random.seed()
        imdat = imp_random(self.pidat) 
        sdat = prep_for_split(self.rtdat, imdat)
        mdat = split_data(sdat, self.bdat, self.args)
        res = calc_gamma(mdat, self.pop_n)
        return(res)

    def iter_inc(self):
        pool = mp.Pool(self.args.mcores) 
        res = pool.map_async(self.time_inc,
                [i for i in range(self.args.nsim)])
        est = res.get()
        pool.close(); pool.join()
        print('\n')
        return(est)






if __name__ == '__main__':
    import ahri
    from  ahri.args import SetArgs
    from ahri.calc import CalcInc
    data2020 = '/home/alain/Seafile/AHRI_Data/2020'
    dfem = SetArgs(root = data2020, nsim = 5, years = np.arange(2005, 2021),
        age = {"Fem": [15, 24]})
    xx = CalcInc(dfem)
    # print(xx.gamma_mid())
    # print(xx.pois_mid())
    # tt = xx.gamma_rand()
