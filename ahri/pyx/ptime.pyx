# python3 setup.py build_ext --inplace

# import numpy as np
# def split_longx(di):
#     cdef int id = di[0]
#     cdef int syear = di[3]
#     cdef int eyear = di[4]
#     cdef int sday = di[1]
#     cdef int eday = di[2]
#     yi = np.arange(syear, eyear + 1, dtype = int)
#     cdef int ylen = len(yi)
#     ptime = np.zeros(ylen, dtype = int)
#     ir = np.repeat(id, ylen)
#     ei = np.zeros(ylen, dtype = int)
#     ei[ylen - 1] = di[5]
#     if (ylen == 1):
#         ptime[0] = eday - sday
#     elif (ylen == 2):
#         ptime[0] = 365 - sday
#         ptime[1] = eday
#     else:
#         ptime[0] = 365 - sday
#         ptime[1:(ylen - 1)] = 365
#         ptime[ylen - 1] = eday
#     return(np.c_[ir, yi, ptime, ei])

import numpy as np
def split_longx(di):
    cdef int ylen = (di[4] - di[3]) + 1
    index = np.arange(ylen) 
    yi = di[3] + index
    ag = di[6] + index
    id = np.repeat(di[0], ylen)
    ei = np.zeros(ylen, dtype = int)
    ei[ylen - 1] = di[5]
    if (ylen == 1):
        ptime = np.array(di[2] - di[1])
    else:
        ptime = np.array([365 - di[1], di[2]], dtype = int)
        if (ylen > 2):
            ptime = np.insert(ptime, 1, np.repeat(365, ylen - 2))
    out = np.c_[id, yi, ptime, ei, ag]
    return(out)

def split_datax(predat):
    edat = [split_longx(predat[di]) for di in range(predat.shape[0])]
    return(edat)
