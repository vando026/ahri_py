# python3 setup.py build_ext --inplace

import numpy as np
def split_longx(di):
    cdef int id = di[0]
    cdef int syear = di[3]
    cdef int eyear = di[4]
    cdef int sday = di[1]
    cdef int eday = di[2]
    cdef int ylen = len(yi)
    cdef int y0 = syear
    cdef int yi[ylen]
    
    while y0 <= eyear:
        for i in yi[:ylen]:
            yi[i] = y0
            y0 += 1

    # print(yi)
    # # yi = np.arange(syear, eyear + 1, dtype = int)
    # # ptime = np.zeros(20, dtype = int)
    # cdef int ptime[30]
    # ir = np.repeat(id, ylen)
    # ei = np.zeros(ylen)
    # ei[ylen - 1] = di[5]
    # if (ylen == 1):
    #     ptime[0] = eday - sday
    #     ptime = ptime[0:1]
    # elif (ylen == 2):
    #     ptime[0] = 365 - sday
    #     ptime[1] = eday
    #     ptime = ptime[0:2]
    # else:
    #     ptime[0] = 365 - sday
    #     ptime[1:(ylen - 1)] = 365
    #     ptime[ylen - 1] = eday
    #     ptime = ptime[:ylen]
    return(np.c_[ir, yi, ptime, ei])
