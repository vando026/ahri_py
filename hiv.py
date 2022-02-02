from ahri.args import *
from ahri.utils import *


def set_inc_data(rtdat, imdat):
    """Create a dataset for calculating HIV incidence"""
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


def get_inc_mid(rtdat, predat, events, ptimes):
    imdat = imp_midpoint(predat) 


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


class CalcInc:
    def __init__(self, args):
        self.args = args
        self.sdat = set_hiv(self.args)
        self.rtdat = get_repeat_testers(self.sdat)
        predat = pre_imp_set(self.rtdat)
        self.inc = do_inc(self.rtdat, predat, self.args)
