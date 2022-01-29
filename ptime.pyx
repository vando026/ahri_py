def agg_incx(di, events, ptimes):
    cdef int syear = di[3]
    cdef int eyear = di[4]
    cdef int sday = di[1]
    cdef int eday = di[2]
    cdef int sero = di[5]
    cdef int y
    events[eyear] += sero
    if (eyear - syear == 0):
        ptimes[eyear] += eday - sday
    else:
        ptimes[syear] += 365 - sday
        ptimes[eyear] += eday
        if (eyear - syear > 2):
            for y in range(syear + 1, eyear): 
                ptimes[y] += 365

# use this version possibly for adjusted hiv
# import numpy as np
# def agg_inc_long(di):
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
