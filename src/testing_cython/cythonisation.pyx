cdef int N_C = 1000


cpdef int while_loop_c():
    cdef int total = 0
    cdef int i = 0
    while i < N_C + 1:
        total += i
        i += 1


cpdef int for_loop_c():
    cdef int total = 0
    cdef int i
    for i in range(N_C + 1):
        total += i


cpdef int sum_function_c():
    cdef int total
    total = sum(range(N_C + 1))


cpdef double sum_calculation_c():
    cdef double total
    total = (N_C + 1) * N_C / 2
