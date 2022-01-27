# import numpy as np
# def get_ptimex(di):
#     cdef int syear = di[3]
#     cdef int eyear = di[4]
#     cdef int sday = di[1]
#     cdef int eday = di[2]
#     yi = np.arange(syear, eyear + 1, dtype = int)
#     ptime = np.zeros(20, dtype = int)
#     cdef int ylen = len(yi)
#     if (ylen == 1):
#         ptime[0] = eday - sday
#         ptime = ptime[0:1]
#     elif (ylen == 2):
#         ptime[0] = 365 - sday
#         ptime[1] = eday
#         ptime = ptime[0:2]
#     else:
#         ptime[0] = 365 - sday
#         ptime[1:(ylen - 1)] = 365
#         ptime[ylen - 1] = eday
#         ptime = ptime[:ylen]
#     return(np.c_[yi, ptime])

xx = {2005: 0, 2006: 0}
for i in [2005, 2006]:
    xx[i] += 2



import numpy as np
def get_ptimex(di):
    cdef int syear = di[3]
    cdef int eyear = di[4]
    cdef int sday = di[1]
    cdef int eday = di[2]
    yi = np.arange(syear, eyear + 1, dtype = int)
    ptime = np.zeros(20, dtype = int)
    cdef int ylen = len(yi)
    if (ylen == 1):
        ptime[0] = eday - sday
        ptime = ptime[0:1]
    elif (ylen == 2):
        ptime[0] = 365 - sday
        ptime[1] = eday
        ptime = ptime[0:2]
    else:
        ptime[0] = 365 - sday
        ptime[1:(ylen - 1)] = 365
        ptime[ylen - 1] = eday
        ptime = ptime[:ylen]
    return(np.c_[yi, ptime])
