from collections import deque,namedtuple


KombinacijaTuple = namedtuple("Kombinacija","boja ukus oblik")
MemoryTuple =namedtuple("Memorija","kombinacija hranljivost")

class MemoryDeque(deque):
    def __init__(self,liste,maxlen):
        super().__init__(liste,maxlen)
    def insert_and_pop(self,index,what):
        assert(type(what)==MemoryTuple)
        assert(type(what.kombinacija)==KombinacijaTuple)
        try:
            self.insert(index,what)
        except IndexError:
            self.pop()
            self.insert(index,what)

    def search_memory(self,ktuple):
        """Trazi da li ima u memoriji dati objekat """
        assert(type(ktuple)==KombinacijaTuple)
        for entry in self:
            if entry.kombinacija ==ktuple:
                print ("nadjeno u memoriji!")
                return entry
        return None

class PoisonError(Exception):
    """Can't have this number of poisions"""

class SmallMemoryError(Exception):
    """Can't have zero memory size"""

class HranaError(Exception):
    """Wrong number of food"""
