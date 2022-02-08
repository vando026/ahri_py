# python3 setup.py build_ext --inplace

import numpy as np
def split_longx(di):
    cdef int id = di[0]
    cdef int syear = di[3]
    cdef int eyear = di[4]
    cdef int sday = di[1]
    cdef int eday = di[2]
    yi = np.arange(syear, eyear + 1, dtype = int)
    cdef int ylen = len(yi)
    ptime = np.zeros(ylen, dtype = int)
    ir = np.repeat(id, ylen)
    ei = np.zeros(ylen, dtype = int)
    ei[ylen - 1] = di[5]
    if (ylen == 1):
        ptime[0] = eday - sday
    elif (ylen == 2):
        ptime[0] = 365 - sday
        ptime[1] = eday
    else:
        ptime[0] = 365 - sday
        ptime[1:(ylen - 1)] = 365
        ptime[ylen - 1] = eday
    return(np.c_[ir, yi, ptime, ei])

# import numpy as np
# def split_longx(di):
#     cdef int ids = di[0]
#     cdef int syear = di[3]
#     cdef int eyear = di[4]
#     cdef int sday = di[1]
#     cdef int eday = di[2]
#     yi = np.arange(syear, eyear + 1, dtype = int)
#     cdef int ylen = len(yi)
#     ei = np.zeros(ylen, dtype = int)
#     ei[ylen - 1] = di[5]
#     if (ylen == 1):
#         ptime = di[2] - di[1]
#     else:
#         ptime = np.array([365 - di[1], di[2]], dtype = int)
#         if (ylen > 2):
#             ptime = np.insert(ptime, 1, np.repeat(365, ylen - 2))
#     out = np.array([np.repeat(di[0], ylen), yi, ptime, ei], dtype = int)
#     return(out.T)
