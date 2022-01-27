"""
## Description: Functions for processing AHRI datasets
## Project: ahri_py
## Author: AV / Created: 24Jan2022 
"""

import pandas as pd
import numpy as np
from datetime import datetime
from functools import reduce
import multiprocessing as mp
from ahri.ahri.ptime import agg_incx
from time import sleep
import sys

def drop_tasp(file, dat):
  """Function to drop individuals who tested in TasP areas"""
  pipdat = pd.read_pickle(file)
  dat = pd.merge(dat, pipdat, on="BSIntID", how='left')
  dat = dat[dat['PIPSA'].isin(["Southern PIPSA", np.nan])]
  dat = dat.drop(['PIPSA'], axis=1)
  return dat


def get_hiv(args):
    """Read the pickled HIV dataset"""
    dat = pd.read_pickle(args.root.hiv_pkl)
    return(dat)


def set_age(dat, args):
    """Function to set age by arguments"""
    for s in args.age.keys():
        dat = dat[~((dat.Female == args.sex[s]) & (dat.Age < args.age[s][0]))] 
        dat = dat[~((dat.Female == args.sex[s]) & (dat.Age > args.age[s][1]))]
    return(dat)


def set_data(dat, args):
    """Function to set age, sex, and year by arguments"""
    dat = set_age(dat, args)
    dat = dat[dat.Female.isin(list(args.sex.values())) & \
            dat.Year.isin(args.years)]
    return(dat)


def set_hiv(args, dat = None):
    """Set the HIV data according to arguments"""
    if (dat is None):
        dat = get_hiv(args)
    dat = set_data(dat, args)
    return(dat)


def get_dates(f):
  """ Function to get earliest/latest test dates. """
  def action(dat, var, name):
    dat = dat[['IIntID', var]].dropna(subset=[var])
    dat = dat.groupby(['IIntID'], as_index=False)[var].agg(f)
    dat.columns = ['IIntID', name]
    return dat
  return action

get_dates_min = get_dates(min)
get_dates_max = get_dates(max)


def get_repeat_testers(dat, onlyRT = True):
  """Get repeat tester data from an HIV test dataset"""
  obs_start = get_dates_min(dat, "HIVNegative", "obs_start")
  early_pos = get_dates_min(dat, "HIVPositive", "early_pos")
  late_neg = get_dates_max(dat, "HIVNegative", "late_neg")
  late_pos = get_dates_max(dat, "HIVPositive", "late_pos")
  dat = dat[['IIntID', 'Female']].drop_duplicates()
  dfs = [dat, obs_start, late_neg, early_pos, late_pos]
  dt = reduce(lambda left,right: \
    pd.merge(left,right,on='IIntID', how='left'), dfs)
  dt['late_neg_after'] = (dt.late_neg > dt.early_pos) & \
    pd.notna(dt.late_neg) & pd.notna(dt.early_pos)
  rt = dt[dt.late_neg_after==False]. \
    drop(['late_neg_after', 'late_pos'], axis=1)
  if (onlyRT):
    rt = rt[-(pd.isna(rt.obs_start) & pd.isna(rt.late_neg))] 
    rt = rt[-((rt.obs_start == rt.late_neg) & pd.isna(rt.early_pos))]
  rt['sero_event'] = pd.notna(rt.early_pos).astype(int)
  return(rt)


def pre_imp_set(rtdat, origin = datetime(1970, 1, 1)):
    ndat = rtdat[-pd.isna(rtdat['early_pos'])]
    ndat = ndat[["IIntID", "late_neg", "early_pos"]]
    ndat['late_neg_'] = (ndat['late_neg'] - origin).dt.days
    ndat['early_pos_'] = (ndat['early_pos'] - origin).dt.days
    ndat = ndat[["IIntID", "late_neg_", "early_pos_"]]
    return(ndat.to_numpy())

def imp_random(rtdat):
    """Impute random dates in censored interval"""
    np.random.seed()
    idates = np.random.randint(rtdat[:, 1] + 1,  rtdat[:, 2])
    ndat = pd.DataFrame({"IIntID": rtdat[:, 0], "serodate": idates})
    ndat['serodate'] = pd.to_datetime(ndat['serodate'], unit='d')
    return(ndat)

def set_inc_data(rtdat, imdat):
    """Create a dataset for calculating HIV incidence"""
    dat = pd.merge(rtdat, imdat, how = 'left', on = 'IIntID')
    dat['obs_end'] = np.where(dat["sero_event"]==1, 
            dat['serodate'], dat['late_neg'])
    ndat = pd.DataFrame()
    ndat['IIntID'] = dat.IIntID
    ndat["startday"] = dat["obs_start"].dt.day_of_year
    ndat["endday"] = dat['obs_end'].dt.day_of_year
    ndat["startyear"] = dat["obs_start"].dt.year
    ndat["endyear"] = dat['obs_end'].dt.year
    ndat["event"] = dat["sero_event"]
    return(ndat.to_numpy())


def agg_inc(di):
    """Get the person-time contributions"""
    syear = di[3]
    eyear = di[4]
    sday = di[1]
    eday = di[2]
    sero = di[5]
    events[eyear] += sero
    if (eyear - syear == 0):
        ptimes[eyear] += eday - sday
    else:
        ptimes[syear] += 365 - sday
        ptimes[eyear] += eday
        if (eyear - syear > 2):
            for y in range(syear + 1, eyear): 
                ptimes[y] += 365


def get_inc(rtdat, predat):
    """Calculate inc rate by person years"""
    imdat = imp_random(predat) 
    sdat = set_inc_data(rtdat, imdat)
    for i in range(sdat.shape[0]):
        agg_inc(sdat[i]) 
    inc = [(events[x] / (ptimes[x] / 365)) * 100 
            for x in events.keys()]
    return(inc)

def time_inc(rtdat, predat, i, n):
    if (i is not None): 
        j = (i + 1) / n
        sys.stdout.write('\r')
        sys.stdout.write("[%-20s] %d%%" % ('='*int(20*j), 100 * j))
        sys.stdout.flush()
        sleep(0.0005)
    # you have to reset random seed for each process
    np.random.seed()
    inc = get_inc(rtdat, predat)
    return(inc)


def do_inc(rtdat, predat, args):
    global ptimes 
    ptimes = {x:0 for x in range(np.min(args.years), np.max(args.years) + 1)}
    global events 
    events = ptimes.copy()
    pool = mp.Pool(args.mcores) 
    out = [pool.apply_async(time_inc,
        args = (rtdat, predat, i, args.nsim)) 
        for i in range(args.nsim)]
    # out = [time_inc(rtdat, predat, i, args.nsim) for i in range(args.nsim)]
    inc = np.array([r.get() for r in out]).T
    pool.close()
    pool.join()
    est = [np.mean(inc[i]) for i in range(inc.shape[0])]
    est = pd.DataFrame({'Year': list(events.keys()), 'Rate': est})
    return(est)
