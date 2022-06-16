import re
import os
import subprocess
import pandas as pd
import numpy as np

class ReadUniReg:
    def __init__(self, infile):
        with open(infile) as f:
            self.temp = [l.strip() for l in f if l.strip()]
        # get start line of each result
        self.slines = [i for i, ln in enumerate(self.temp)
                if re.search("(Covariate|(Cov|V)ariance|Hazard)", ln)]

    def covariance(self):
        offset = 0 if re.search("^Variance", self.temp[self.slines[1]]) != None else 1
        dat = self.temp[self.slines[1] + offset:self.slines[2]]
        dat = [re.sub(":", "", i) for i in dat]
        dat = [ln.split("\t") for ln in dat]
        # Add covariate label to make ncol equal
        dat[0].insert(0, "Covariate")
        dat = pd.DataFrame(dat[1:], columns = dat[0])
        dat.set_index("Covariate", inplace = True)
        dat = dat.astype(np.float64)
        return dat

    def hazard(self):
        dat = self.temp[self.slines[2] + 1:]
        dat = [ln.split("\t") for ln in dat]
        dat = pd.DataFrame(dat[1:], columns = dat[0])
        dat = dat.astype(np.float64)
        return dat

    def estimates(self):
        # estimates
        dat = self.temp[self.slines[0]:self.slines[1]]
        dat = [ln.split("\t") for ln in dat]
        dat = pd.DataFrame(dat[1:], columns = dat[0])
        dat.set_index("Covariate", inplace = True)
        dat = dat.astype(np.float64)
        return dat

tt = ReadUniReg(infile = "/home/alain/Seafile/Heidelberg/Projects/Inc4/data/res_dat_2.txt")
tt = ReadUniReg(infile = "/home/alain/Seafile/AHRI_Data/intcens/res_dat_mnth.txt")

class UniReg(ReadUniReg):
    def __init__(self,
        xpath, root, input, output, model, 
        convergence_threshold = 0.01, 
        inf_char = "Inf", r = 0.0):
        subprocess.Popen([
            xpath, 
            "--in", os.path.join(root, input), 
            "--out", os.path.join(root, output), 
            "--model",  model,
            "--sep", '" "',
            "--inf_char", f'"{inf_char}"',
            "--r", f"{r}",
            "--convergence_threshold", f"{convergence_threshold}"])
        ReadUniReg.__init__(self, os.path.join(root, output))

tt = UniReg(
    xpath = "/home/alain/Seafile/Programs/Python/library/ahri_dev/src/ahri/unireg",
    root = "/home/alain/Seafile/Heidelberg/Projects/Inc4/data",
    input = "input_data_1.txt",
    output = "res_data1.txt",
    model = "(left, right) = Age")

