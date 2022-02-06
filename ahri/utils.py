import pandas as pd
import numpy as np
from datetime import datetime
from functools import reduce
import multiprocessing as mp
# from ahri.cyfiles import agg_incx
from ahri.args import SetFiles
# from ahri.hiv import *
from time import sleep
import sys

def drop_tasp(dat, pipdat = None):
  """Function to drop individuals who tested in TasP areas"""
  if (pipdat is None): pipdat = pd.read_pickle(file)
  dat = pd.merge(dat, pipdat, on="BSIntID", how='left')
  dat = dat[dat['PIPSA'].isin(["Southern PIPSA", np.nan])]
  dat = dat.drop(['PIPSA'], axis=1)
  return(dat)

# def set_age(dat, args):
#     """Function to set age by arguments"""
#     for s in args.age.keys():
#         dat = dat[~((dat.Female == args.sex[s]) & (dat.Age < args.age[s][0]))] 
#         dat = dat[~((dat.Female == args.sex[s]) & (dat.Age > args.age[s][1]))]
#     return(dat)

def set_data(dat, args):
    """Function to set age, sex, and year by arguments"""
    for s in args.age.keys():
        dat = dat[~((dat.Female == args.sex[s]) & (dat.Age < args.age[s][0]))] 
        dat = dat[~((dat.Female == args.sex[s]) & (dat.Age > args.age[s][1]))]
    dat = dat[dat.Female.isin(list(args.sex.values()))]
    dat = dat[dat.Year.isin(args.years)]
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

def get_birth_date(dat):
    """Get birthdate and birthyear"""
    dat = dat[["IIntID", "DoB"]]
    dat = dat.drop_duplicates(["IIntID"])
    dat['YoB'] = dat["DoB"].dt.year
    return(dat)

def pre_imp_set(rtdat, origin = datetime(1970, 1, 1)):
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

