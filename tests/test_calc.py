import unittest
import sys
from ahri import utils
from ahri.calc import calc_rubin, age_adjust, split_long2
import numpy as np

# in ipython run, cd to file and 
# %run test_calc.py

class TestAHRI(unittest.TestCase):

    tab = utils.mk_epi_tab()

    betas = np.array([-1.128465, -1.096334, -1.123843, -1.114631, -1.096334])
    variances = [0.004627717, 0.004553212, 0.004616816, 0.004595274, 0.004553212]

    count = np.array([107, 141, 60, 40, 39, 25])
    pop = np.array([230061, 329449, 114920, 39487, 14208, 3052])
    stpop =  np.array([63986.6, 186263.6, 157302.2, 97647.0, 47572.6, 12262.6])


    s1 = np.array([153, 254, 2005, 2014, 1, 37])
    s2 = np.array([153, 254, 2005, 2005, 0, 20])
    s3 = np.array([153, 254, 2005, 2006, 1, 20])

    def test_adjust(self):
        res = age_adjust(self.count, self.pop, self.stpop)
        self.assertEqual(np.round(res[0], 8), 0.00092305)
        self.assertEqual(np.round(res[1] * 1e6, 7), 0.003919)

    def test_rubin(self):
        res = calc_rubin(self.betas, self.variances)
        self.assertEqual(np.round(res[1], 6), -1.111921)
        self.assertEqual(np.round(res[2], 6),  0.069728)
        self.assertEqual(np.round(res[3], 6), -1.248716)
        self.assertEqual(np.round(res[4], 6), -0.975127)

    def test_split(self):
        res = split_long2(self.s1, self.tab)
        self.assertEqual(res.shape[0], 10)
        self.assertEqual(res.shape[1], 4)
        self.assertEqual(res[:, 1].sum(), 3386)
        self.assertEqual(res[-1, 2], 1)
        self.assertEqual(res[:, 3].sum(), 415)
        self.assertEqual(res[0, 1], 365 - self.s1[0])

    def test_split2(self):
        res = split_long2(self.s2, self.tab)
        self.assertEqual(res.shape[0], 1)
        self.assertEqual(res.shape[1], 4)
        self.assertEqual(res[:, 1].sum(), 101)
        self.assertEqual(res[-1, 2], 0)
        self.assertEqual(res[:, 3].sum(), 20)
        self.assertEqual(res[0, 1], self.s2[1] - self.s2[0])


    def test_split3(self):
        res = split_long2(self.s3, self.tab)
        self.assertEqual(res.shape[0], 2)
        self.assertEqual(res.shape[1], 4)
        self.assertEqual(res[:, 1].sum(), 466)
        self.assertEqual(res[-1, 2], 1)
        self.assertEqual(res[:, 3].sum(), 41)
        self.assertEqual(res[0, 1], 365 - self.s2[0])
        self.assertEqual(res[1, 1], self.s2[1])



if __name__ == '__main__':
    unittest.main()
