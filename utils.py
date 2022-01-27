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
from ahri.ahri.ptime import get_ptimex
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

def imp_random(rtdat, origin = datetime(1970, 1, 1)):
    """Impute random dates in censored interval"""
    ndat = rtdat.copy()
    ndat = ndat[-pd.isna(ndat['early_pos'])]
    ndat = ndat[["IIntID", "late_neg", "early_pos"]]
    ndat['late_neg_'] = (ndat['late_neg'] - origin).dt.days
    ndat['early_pos_'] = (ndat['early_pos'] - origin).dt.days
    def imp_rand(left, right): 
        impdate = np.random.randint(left, right + 1)
        return impdate
    ndat['sero_date'] = ndat.apply(lambda row: 
            imp_rand(row['late_neg_'], row['early_pos_']), axis=1)
    ndat = ndat[["IIntID", "sero_date"]] 
    ndat['sero_date'] = pd.to_datetime(ndat['sero_date'], unit='d')
    tdat = pd.merge(rtdat, ndat, how='left', on='IIntID')
    return(tdat[["IIntID", "obs_start",  
        "late_neg",  "early_pos", "sero_date", "sero_event"]])

def set_inc_data(dat, right_date='sero_date'):
    """Create a dataset for calculating HIV incidence"""
    dat['obs_end'] = np.where(dat["sero_event"]==1, 
            dat[right_date], dat['late_neg'])
    ndat = pd.DataFrame()
    ndat['IIntID'] = dat.IIntID
    ndat["startday"] = dat["obs_start"].dt.day_of_year
    ndat["endday"] = dat['obs_end'].dt.day_of_year
    ndat["startyear"] = dat["obs_start"].dt.year
    ndat["endyear"] = dat['obs_end'].dt.year
    ndat["event"] = dat["sero_event"]
    return ndat


def get_ptime(di):
    """Get the person-time contributions"""
    yi = np.arange(di[3], di[4] + 1, dtype = int)
    ylen = len(yi)
    if (ylen == 1):
        ptime = di[2] - di[1]
    else:
        ptime = np.array([365 - di[1], di[2]], dtype = int)
        if (ylen > 2):
            ptime = np.insert(ptime, 1, np.repeat(365, ylen - 2))
    return(np.c_[yi, ptime])


def agg_ptime(dat):
    ndat = dat.to_numpy()
    # ptime = [get_ptime(ndat[i]) for i in range(ndat.shape[0])]
    ptime = [get_ptimex(ndat[i]) for i in range(ndat.shape[0])]
    ptime = pd.DataFrame(np.concatenate(ptime, axis=0), 
            columns = ['Year', 'Days'])
    agg_ptime = (ptime.groupby(ptime.Year). \
            agg(Ptime = pd.NamedAgg('Days', sum)) / 365).round(1)
    return(agg_ptime)

def agg_event(dat):
    events = dat.groupby(dat.endyear). \
        agg(Events = pd.NamedAgg('event',  'sum'))
    return(events)
   
def calc_inc(events, ptimes, pyears = 100):
    inc = ( events.Events / ptimes.Ptime ) * pyears
    return(inc)

def get_inc(rtdat):
    imdat = imp_random(rtdat) 
    sdat = set_inc_data(imdat)
    ptimes = agg_ptime(sdat)
    events = agg_event(sdat)
    inc = calc_inc(events, ptimes)
    return(inc)

def time_inc(rtdat, i = None, n = None):
    if (i is not None): 
        j = (i + 1) / n
        sys.stdout.write('\r')
        sys.stdout.write("[%-20s] %d%%" % ('='*int(20*j), 100 * j))
        sys.stdout.flush()
        sleep(0.0005)
    inc = get_inc(rtdat)
    return(inc)


def do_inc(rtdat, args):
    pool = mp.Pool(args.mcores) 
    out = [pool.apply_async(time_inc, args = (rtdat, i, args.nsim)) 
            for i in range(args.nsim)]
    inc = [r.get() for r in out]
    pool.close()
    inc = pd.concat(inc, axis = 1)
    inc = inc.agg(np.mean, axis = 1)
    return(inc)
