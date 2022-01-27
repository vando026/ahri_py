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
