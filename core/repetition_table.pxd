from cython cimport int, long

cdef class Repetition_entry:
    """
    This class represents an entry in the repetition table
    """
    cdef public unsigned long long zobrist_key
    cdef public int occurences


cdef class Repetition_table:
    """
    This class represents the repetition table
    """
    cdef list table
    cdef int num_entries

    cpdef int get_entry(self, unsigned long long node_zobrist_key)
    cpdef void update_entry(self, unsigned long long key, bint is_add)
