from cython cimport int, long
from core_utils cimport Move
from cpython.mem cimport PyMem_Malloc, PyMem_Realloc, PyMem_Free
cdef extern from "string.h":
    void memset(void* dest, int c, size_t n)

cdef class Entry:
    """
    This class represents an entry in the transposition table
    """

    def __cinit__(self, key, score, depth, node_type, best):
        self.zobrist_key = key
        self.score = score
        self.depth = depth
        self.node_type = node_type
        self.best = best
        self.is_white = False


cdef class Transposition_table:
    """
    This class represents the transposition table
    """

    def __cinit__(self, size_in_MB: int):
        self.num_entries = size_in_MB // sizeof(Entry)
        self.table = []
        for i in range(self.num_entries):
            self.table.append(Entry(0,0,0,-1,None))
    

    cpdef Entry get_entry(self, unsigned long long node_zobrist_key):
        cdef int index
        cdef Entry entry

        index = node_zobrist_key % self.num_entries
        entry = self.table[index]
        
        if entry.zobrist_key != node_zobrist_key:
            return None
        
        return entry


    cpdef void store_entry(self, unsigned long long key, float score, int depth, int node_type, Move best, bint is_white):
        cdef int index

        index = key % self.num_entries
        self.table[index].zobrist_key = key
        self.table[index].score = score
        self.table[index].depth = depth
        self.table[index].node_type = node_type
        self.table[index].best = best
        self.table[index].is_white = is_white
        