import numpy as  np

def split_long(long [:] di):

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

# def split_datax(predat):
#     edat = [split_longx(predat[di]) for di in range(predat.shape[0])]
#     return(edat)
