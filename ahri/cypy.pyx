import numpy as  np

def pre_splitx(int [:,:] ndat):
    cdef int i, origin = 2000
    cdef double syear, sday, eyear, eday
    cdef double DAY = 365.25
    cdef Py_ssize_t nrows = ndat.shape[0]
    result = np.zeros((nrows, 6), dtype = np.intc)
    cdef int[:, :] res = result
    
    for i in range(nrows):
        syear =  origin + (ndat[i, 1] / DAY)
        sday =  syear % 1 * DAY
        eyear =  origin + (ndat[i, 2] / DAY)
        eday = eyear % 1 * DAY
        res[i, 0] = np.ceil(sday)
        res[i, 1] = np.ceil(eday)
        res[i, 2] = np.floor(syear)
        res[i, 3] = np.floor(eyear)
        res[i, 4] = ndat[i, 3]
        res[i, 5] = ndat[i, 4]

    return result


def split_datax(int [:,:] predat):
    cdef Py_ssize_t nrow = predat.shape[0]
    edat = [split_long(predat[di]) for di in range(nrow)]
    return(edat)

def split_long(int [:] di):

    DTYPE = np.intc
    cdef int nrow = (di[3] - di[2]) + 1
    cdef int year = di[2]
    cdef int age = di[5]
    cdef Py_ssize_t lastn = nrow - 1

    result = np.zeros((nrow, 4), dtype=DTYPE)
    cdef int[:, :] result_view = result

    for x in range(nrow):
        result_view[x, 0] = year
        result_view[x, 1] = 365
        result_view[x, 3] = age
        year += 1
        age += 1

    result_view[lastn, 2] = di[4]
    result_view[-1, 1] = di[1]
    result_view[0, 1] = result_view[0, 1] - di[0]

    return result


def age_adjustx(double [:] count, double [:] pop, long [:] stpop):

    DTYPE = np.float64
    cdef int i, ni = len(count)
    cdef float ptot = 0.0
    cdef float ds = 0.0
    cdef float dsvar = 0.0

    mat = np.zeros(ni, dtype=DTYPE)
    cdef double[:] wt = mat
    mat2 = np.zeros(ni, dtype=DTYPE)
    cdef double[:] rate = mat2
    mat3 = np.zeros(ni, dtype=DTYPE)
    cdef double[:] var = mat3

    out = np.zeros(2, dtype = DTYPE)
    cdef double[:]  res = out

    for i in range(ni):
        ptot += stpop[i]

    for i in range(ni):
        wt[i] =  stpop[i] / ptot
        rate[i] = (count[i] / pop[i]) * wt[i]
        var[i] = (count[i] / pop[i]**2) * (wt[i]**2)
        res[0] += rate[i]
        res[1] += var[i]

    return out
