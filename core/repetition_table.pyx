from cython cimport int, long

cdef class Repetition_entry:
    """
    This class represents an entry in the repetition table
    """

    def __cinit__(self, key):
        self.zobrist_key = key
        self.occurences = 0


cdef class Repetition_table:
    """
    This class represents the repetition table
    """

    def __cinit__(self, size_in_MB: int):
        self.num_entries = size_in_MB // sizeof(Repetition_entry)
        self.table = []
        for i in range(self.num_entries):
            self.table.append(Repetition_entry(0))
    

    cpdef int get_entry(self, unsigned long long node_zobrist_key):
        cdef int index
        cdef Repetition_entry entry

        index = node_zobrist_key % self.num_entries
        entry = self.table[index]
        
        if entry.zobrist_key != node_zobrist_key:
            return -1
        
        return entry.occurences


    cpdef void update_entry(self, unsigned long long key, bint is_add):
        cdef int index, change

        index = key % self.num_entries
        change = 1 if is_add else -1

        self.table[index].zobrist_key = key
        self.table[index].occurences = self.table[index].occurences + change