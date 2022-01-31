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
from ahri.args import SetFiles
from time import sleep
import sys

def drop_tasp(file, dat):
  """Function to drop individuals who tested in TasP areas"""
  pipdat = pd.read_pickle(file)
  dat = pd.merge(dat, pipdat, on="BSIntID", how='left')
  dat = dat[dat['PIPSA'].isin(["Southern PIPSA", np.nan])]
  dat = dat.drop(['PIPSA'], axis=1)
  return(dat)

def get_hiv(path = SetFiles().hiv_pkl):
    """Read the pickled HIV dataset"""
    dat = pd.read_pickle(path)
    return(dat)

def get_epi(path = SetFiles().epi_pkl):
    """Read the pickled Surveillance dataset"""
    dat = pd.read_pickle(path)
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
    dat = dat[dat.Female.isin(list(args.sex.values()))]
    dat = dat[dat.Year.isin(args.years)]
    return(dat)

def set_hiv(args, dat = None):
    """Set the HIV data according to arguments"""
    if (dat is None):
        dat = get_hiv(args.paths.hiv_pkl)
    dat = set_data(dat, args)
    return(dat)

def set_epi(args, dat = None):
    """Set the Surveillence data according to arguments"""
    if (dat is None):
        dat = get_epi(args.paths.epi_pkl)
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


def get_repeat_testers(dat):
    """Get repeat tester data from an HIV test dataset"""
    obs_start = get_dates_min(dat, "HIVNegative", "obs_start")
    early_pos = get_dates_min(dat, "HIVPositive", "early_pos")
    late_neg = get_dates_max(dat, "HIVNegative", "late_neg")
    late_pos = get_dates_max(dat, "HIVPositive", "late_pos")
    dat = dat[['IIntID', 'Female']].drop_duplicates()
    dfs = [dat, obs_start, late_neg, early_pos, late_pos]
    dt = reduce(lambda left,right: \
    pd.merge(left,right,on='IIntID', how='left'), dfs)
    # drop if late neg after early pos
    dt['late_neg_after'] = (dt.late_neg > dt.early_pos) & \
    pd.notna(dt.late_neg) & pd.notna(dt.early_pos)
    rt = dt[dt.late_neg_after==False]. \
    drop(['late_neg_after', 'late_pos'], axis=1)
    # drop if no neg test
    rt = rt[-(pd.isna(rt.obs_start) & pd.isna(rt.late_neg))] 
    # drop if only 1 neg test and no pos test
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

