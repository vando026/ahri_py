import numpy as  np


cdef int add2(int origin , int day):
    return origin + day

cdef double divide(double a, double b):
    return a / b

cdef double pow(double a):
    return a * a

cdef int subtract(int a, int b):
    return a - b


def pre_split(int [:,:] ndat):
    cdef int i, origin = 2000
    cdef double sdate, edate
    cdef double DAY = 365.25
    cdef Py_ssize_t nrows = ndat.shape[0]
    result = np.zeros((nrows, 6), dtype = np.intc)
    cdef int[:, :] res = result
    
    for i in range(nrows):
        sdate = ndat[i, 1] / DAY 
        edate = ndat[i, 2] / DAY 
        res[i, 0] = int(sdate % 1  * DAY)
        res[i, 1] = int(edate % 1 * DAY)
        res[i, 2] = add2(origin, int(sdate))
        res[i, 3] = add2(origin, int(edate))
        res[i, 4] = ndat[i, 3]
        res[i, 5] = ndat[i, 4]

    return result


def split_data(int [:,:] predat):
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
    result_view[0, 1] = subtract(result_view[0, 1], di[0])

    return result


def age_adjust(int [:] count, int [:] pop, double [:] stpop):

    DTYPE = np.double
    cdef int i, ni = len(count)
    cdef double wt, ptot = 0.0

    out = np.zeros(2, dtype = DTYPE)
    cdef double[:]  res = out

    for i in range(ni):
        ptot += stpop[i]

    for i in range(ni):
        wt =  divide(stpop[i], ptot)
        res[0] += divide(count[i], pop[i]) * wt
        # pop2 = pow(pop[i])
        res[1] += divide(count[i], pow(pop[i])) * pow(wt)

    return out
