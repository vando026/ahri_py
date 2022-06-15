import re

class ReadUniReg:
    def __init__(self, infile):
        slines = list()
        with open(infile) as f:
            for i, line in enumerate(f):
                if re.match("^Covariate", line):
                    slines.append(i)
                if re.match("^Covariance", line):
                    slines.append(i)
                if re.search("Hazard", line):
                    slines.append(i + 1)
        # Estimates
        edat = pd.read_table(infile, sep = "\t",
                skiprows = slines[0], nrows = slines[1] - (slines[0] + 2))
        self.estimates = edat
        # Covariance
        cdat = pd.read_table(infil, sep = "\t",
                skiprows = slines[1] + 1, nrows = slines[2] - (slines[1] + 4))
        cdat = cdat.iloc[:, 1:]
        self.covariance = cdat
        # Hazard
        sdat = pd.read_table(infile, sep = "\t", skiprows = slines[2])
        self.hazard = sdat

tt = ReadUniReg(ic_dir + "/res_dat.txt")
