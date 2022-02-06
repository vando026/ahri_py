from ahri.dataproc import DataProc
from ahri.utils import *
import statsmodels.api as sm

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

def split_data(predat, bdat):
    """Split repeat-tester data into episodes""" 
    edat = [get_ptime_long(predat[di]) for di in range(predat.shape[0])]
    mdat = pd.DataFrame(np.vstack(edat), 
            columns = ["IIntID", "Year", "Days", "Event"])
    mdat['tscale'] = mdat["Days"] / 365
    mdat = mdat[mdat['tscale'] != 0]
    mdat['tscale'] = np.log(mdat['tscale'])
    mdat = pd.merge(mdat, bdat, how = 'inner', on = "IIntID")
    mdat['Age'] = mdat['Year'] - mdat["YoB"]
    return(mdat[["IIntID", "Year",  "Event", "tscale", "Age"]])

def set_post_imp(im):
    """Prepare dataset after imputation for models""" 

def get_inc(rtdat, predat, events, ptimes):
    """Calculate inc rate by person years"""
    imdat = imp_random(predat) 
    sdat = set_inc_data(rtdat, imdat)
    # use cython version for agg_inc
    for i in range(sdat.shape[0]):
        agg_incx(sdat[i], events, ptimes) 
    inc = [(events[x] / (ptimes[x] / 365)) * 100 
            for x in events.keys()]
    return(inc)

def time_inc(rtdat, predat, events, ptimes, i, args):
    """Add timer to the calculate inc rate function"""
    if (args.verbose):
        j = (i + 1) / args.nsim
        sys.stdout.write('\r')
        sys.stdout.write("[%-20s] %d%%" % ('='*int(20*j), 100 * j))
        sys.stdout.flush()
        # sleep(0.0005)
    # you have to reset random seed for each process
    np.random.seed()
    inc = get_inc(rtdat, predat, events, ptimes)
    return(inc)


def iter_inc(rtdat, predat, args):
    ptimes = {x:0 for x in range(np.min(args.years), np.max(args.years) + 1)}
    events = ptimes.copy()
    pool = mp.Pool(args.mcores) 
    out = [pool.apply_async(time_inc, 
        args = (rtdat, predat, events, ptimes, i, args)) 
            for i in range(args.nsim)]
    inc = np.array([r.get() for r in out]).T
    pool.close(); pool.join()
    print('\n')
    return(est)

def get_mean(est):
    est = [np.mean(inc[i]) for i in range(inc.shape[0])]
    # est = pd.DataFrame({'Year': list(events.keys()), 'Rate': est})
    return(est)


def get_se(est, n):
    se = [np.std(inc[i]) / np.sqrt(n)
            for i in range(inc.shape[0])]
    # est = pd.DataFrame({'Year': list(events.keys()), 'Rate': est})
    return(se)


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
#   est <- split(est, rownames(est))
#   se <- split(se, rownames(se))
#   out <- Map(doCalc, est, se)
#   out <- data.frame(do.call(rbind, out))
#   out[] <- lapply(out[], `*`, 100)
#   out
# }

def calc_pois(dat, ndat, formula = "Event ~ -1"):
    """Calc incidence using Poisson model"""
    model = sm.GLM.from_formula(formula, 
            offset = dat["tscale"], data = dat, 
            family = sm.families.Poisson(sm.families.links.log())).fit()
    res = model.get_prediction(ndat)
    return(res.summary_frame())


class CalcInc(DataProc):
    def __init__(self, args):
        DataProc.__init__(self, args)
        self.hdat = self.set_hiv()
        self.edat = self.set_epi()
        self.bdat = get_birth_date(self.edat)
        self.rtdat = self.get_repeat_testers(self.hdat)
        self.pdat_yr = pred_dat_year(self.args)
        self.pdat_yr_age = pred_dat_age_year(self.edat)
        self.adjust_form = "Event ~ -1 + C(Year) + Age + C(Year):Age"
        self.unadjust_form = "Event ~ -1 + C(Year)"

    def calc_inc_mid(self, age_adjust = True):
        """Calculate HIV incidence using mid-point imputation"""
        pdat = prep_for_imp(self.rtdat)
        imdat = imp_midpoint(pdat) 
        sdat = prep_for_split(self.rtdat, imdat)
        mdat = split_data(sdat, self.bdat)
        if (age_adjusted):
            ndat = self.pdat_yr_age 
            f1 = self.adjust_form
        else:
            ndat = self.pdat_yr
            f1 = self.unadjust_form
        res = calc_pois(mdat, ndat, f1)
        return(res)
