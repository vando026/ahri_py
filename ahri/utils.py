import pandas as pd
import numpy as np
import sys

def drop_tasp(dat, pipdat = None):
  """Function to drop individuals who tested in TasP areas"""
  if (pipdat is None): pipdat = pd.read_pickle(file)
  dat = pd.merge(dat, pipdat, on="BSIntID", how='left')
  dat = dat[dat['PIPSA'].isin(["Southern PIPSA", np.nan])]
  dat = dat.drop(['PIPSA'], axis=1)
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
    return(dat)

def add_year_test(dat, bdat, var = "obs_start"):
    dat = pd.merge(dat, bdat, how = "left", on = "IIntID")
    dat["Age"] = dat[var].dt.year - dat["DoB"].dt.year
    return(dat)

def get_pop_n(edat, args):
    """Get # of all participants by year and age group"""
    edat['AgeCat'] = pd.cut(edat['Age'], 
            bins = args.agecat, include_lowest=True)
    gdat = edat.groupby(["Year", "AgeCat"]).agg(
            N = pd.NamedAgg("IIntID", len)).reset_index()
    return(gdat)

def timer(i, n):
    """A progress bar"""
    if i % 2 == 0: 
        j = (i + 1) / n
        sys.stdout.write('\r')
        sys.stdout.write("[%-20s] %d%%" % ('='*int(20*j), 100 * j))
        sys.stdout.flush()

def mk_epi_tab():
    yrs = np.arange(2004, 2025)
    days = np.repeat(365, len(yrs))
    zeros = np.zeros(len(yrs), dtype = int)
    tab = np.c_[yrs, days, zeros]
    return(tab)
