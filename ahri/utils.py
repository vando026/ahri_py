import pandas as pd
import numpy as np
# from ahri.cyfiles import agg_incx

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
    dat['YoB'] = dat["DoB"].dt.year
    return(dat)


def pred_dat_year(args):
    """Make a year, tscale dataset for statsmodels predict"""
    return(pd.DataFrame(
        {"Year": np.arange(np.min(args.years), np.max(args.years)),
        "tscale": 1}))

def pred_dat_age_year(dat):
    """Make dataset of average age by year for statsmodels predict"""
    dat = dat.groupby(["Year"]). \
        agg(Age = pd.NamedAgg("Age", "mean")) 
    dat.reset_index(inplace = True)
    dat["tscale"] = 1
    return(dat)


def get_pop_n(edat, args):
    """Get # of all participants by year and age group"""
    edat['AgeCat'] = pd.cut(edat['Age'], 
            bins = args.agecat, include_lowest=True)
    gdat = edat.groupby(["Year", "AgeCat"]).agg(
            N = pd.NamedAgg("IIntID", len)).reset_index()
    return(gdat)

