from cython cimport int, long
from core_utils cimport Move

cdef class Entry:
    """
    This class represents an entry in the transposition table
    """
    cdef public unsigned long long zobrist_key
    cdef public float score
    cdef public int depth
    # 0 is exact value, 1 is lowerbound, 2 is upperbound
    cdef public int node_type
    cdef public Move best
    # Used for perspective
    cdef public bint is_white

cdef class Transposition_table:
    """
    This class represents the transposition table
    """
    cdef list table
    cdef int num_entries

    cpdef Entry get_entry(self, unsigned long long node_zobrist_key)
    cpdef void store_entry(self, unsigned long long key, float score, int depth, int node_type, Move best, bint is_white)
