import sys
import unittest
from datetime import datetime
from ahri import dataproc
from ahri.calc import CalcInc
from ahri import calc
from ahri import cypy
from ahri.args import SetArgs
import numpy as np
import pandas as pd
import os 

# in ipython run, cd to file and 
# %run test_calc.py

class TestAHRI(unittest.TestCase):

    # root = os.path.dirname(os.path.realpath(__file__)) 
    root = '/home/alain/Seafile/Programs/Python/library/ahri_dev/src/ahri/data'
    targs = SetArgs(root = root, verbose = False)
    targs.path_hiv_dta("RD05-99_ACDIS_HIV_Sample.dta")
    targs.path_bst_dta("RD01-03_ACDIS_BS_Sample.dta")
    targs.path_epi_dta("SurveillanceEpisodes_Sample.dta")
    targs.path_hiv_pkl("RD05-99_ACDIS_HIV_Sample.pkl")
    targs.path_bst_pkl("RD01-03_ACDIS_BS_Sample.pkl")
    targs.path_epi_pkl("SurveillanceEpisodes_Sample.pkl")

    dtest = CalcInc(targs)
    rtdat = pd.read_pickle(os.path.join(root, 'rtdat.pkl'))
    dtest.repeat_tester_data = rtdat
    sdat = calc.prep_for_imp(rtdat)
    sdat[1] = calc.imp_midpoint(sdat[1])

    # %timeit -n 10000 -r 7 sdat10 = cypy.pre_split(ndat)

    def test_pre_split(self):
        ndat0 = self.sdat[0][:, [0, 1, 2,  4, 5]]
        ndat1 = self.sdat[1][:, [0, 1, 6,  4, 5]]
        ndat = np.vstack([ndat0, ndat1])
        ndat = np.array(ndat, dtype = np.intc)
        sdat10 = cypy.pre_split(ndat)
        self.assertEqual(sdat10[0, 0], 294)
        self.assertEqual(sdat10[0, 1], 219)
        self.assertEqual(sdat10[0, 2], 2005)
        self.assertEqual(sdat10[0, 3], 2018)
        self.assertEqual(sdat10[0, 4], 0)
        self.assertEqual(sdat10[0, 5], 29)
        self.assertEqual(sdat10[2, 0], 260)
        self.assertEqual(sdat10[2, 1], 305)
        self.assertEqual(sdat10[2, 2], 2008)
        self.assertEqual(sdat10[2, 3], 2015)
        self.assertEqual(sdat10[2, 4], 0)
        self.assertEqual(sdat10[2, 5], 17)


    def test_dates(self):
        sdatx = self.dtest.agg_data(self.sdat)
        self.assertEqual(sdatx.iloc[0, 2], 2)
        self.assertEqual(sdatx.iloc[1, 2], 1)
        self.assertEqual(sdatx.iloc[2, 2], 0)
        self.assertEqual(sdatx.iloc[10, 2], 2)
        self.assertEqual(np.round(sdatx.iloc[0, 3], 4), 14.8685)
        self.assertEqual(np.round(sdatx.iloc[1, 3], 4), 7.6603)
        self.assertEqual(np.round(sdatx.iloc[2, 3], 4), 2.0767)
        self.assertEqual(np.round(sdatx.iloc[10, 3], 4), 2.8658)


    def test_adjust(self):
        count = np.array([107, 141, 60, 40, 39, 25], dtype = np.intc)
        pop = np.array([230061, 329449, 114920, 39487, 14208, 3052], dtype =
            np.intc)
        stpop =  np.array([63986.6, 186263.6, 157302.2, 97647.0, 47572.6, 12262.6],
            dtype = np.double)
        res = cypy.age_adjust(count, pop, stpop)
        self.assertEqual(np.round(res[0], 8), 0.00092305)
        self.assertEqual(np.round(res[1] * 1e6, 7), 0.003919)

    def test_rubin(self):
        betas = np.array([-1.128465, -1.096334, -1.123843, -1.114631, -1.096334])
        variances = [0.004627717, 0.004553212, 0.004616816, 0.004595274, 0.004553212]
        res = calc.calc_rubin(betas, variances)
        self.assertEqual(np.round(res[1], 6), -1.111921)
        self.assertEqual(np.round(res[2], 6),  0.069728)
        self.assertEqual(np.round(res[3], 6), -1.248716)
        self.assertEqual(np.round(res[4], 6), -0.975127)

    def test_split(self):
        s1 = np.array([153, 254, 2005, 2014, 1, 37], dtype = np.intc)
        res = cypy.split_long(s1)
        self.assertEqual(res.shape[0], 10)
        self.assertEqual(res.shape[1], 4)
        self.assertEqual(res[:, 1].sum(), 3386)
        self.assertEqual(res[-1, 2], 1)
        self.assertEqual(res[:, 3].sum(), 415)
        self.assertEqual(res[0, 1], 365 - s1[0])

    def test_split2(self):
        s2 = np.array([153, 254, 2005, 2005, 0, 20], dtype = np.intc)
        res = cypy.split_long(s2)
        self.assertEqual(res.shape[0], 1)
        self.assertEqual(res.shape[1], 4)
        self.assertEqual(res[:, 1].sum(), 101)
        self.assertEqual(res[-1, 2], 0)
        self.assertEqual(res[:, 3].sum(), 20)
        self.assertEqual(res[0, 1], s2[1] - s2[0])

    def test_split3(self):
        s3 = np.array([153, 254, 2005, 2006, 1, 20], dtype = np.intc)
        res = cypy.split_long(s3)
        self.assertEqual(res.shape[0], 2)
        self.assertEqual(res.shape[1], 4)
        self.assertEqual(res[:, 1].sum(), 466)
        self.assertEqual(res[-1, 2], 1)
        self.assertEqual(res[:, 3].sum(), 41)
        self.assertEqual(res[0, 1], 365 - s3[0])
        self.assertEqual(res[1, 1], s3[1])



if __name__ == '__main__':
    unittest.main()

