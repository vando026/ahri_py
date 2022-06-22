import pandas as pd
import numpy as np
import sys

def drop_tasp(dat, bdat = None):
  """Function to drop individuals who tested in TasP areas"""
  bdat = bdat[["BSIntID", "PIPSA"]]
  dat = pd.merge(dat, bdat, on="BSIntID", how="left")
  dat = dat[dat["PIPSA"].isin(["Southern PIPSA", np.nan])]
  dat = dat.drop(["PIPSA"], axis=1)
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


def add_year_test(dat, bdat, var = "obs_start"):
    dat = pd.merge(dat, bdat, how = "left", on = "IIntID")
    dat["Age"] = dat[var].dt.year - dat["DoB"].dt.year
    return(dat)


def timer(i, n):
    """A progress bar"""
    if i % 2 == 0: 
        j = (i + 1) / n
        sys.stdout.write('\r')
        sys.stdout.write("[%-20s] %d%%" % ('='*int(20*j), 100 * j))
        sys.stdout.flush()
