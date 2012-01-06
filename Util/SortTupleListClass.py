__author__ = 'Brian Sargent'

class SortTupleList:
    tupleSortIndex = 0
    reverseOrder = False

    def __init__(self,tupleIndex,isReversed=False):
        self.tupleSortIndex = tupleIndex
        self.reverseOrder = isReversed

    def doSort(self,aList):
        """Sort a list of tuples. Tuple tupleSortIndex is used to select the tuple member used."""
        sortedList = sorted(aList,key=self.SortSelect,reverse = self.reverseOrder)
        return sortedList

    def SortSelect(self,tuple):
        return tuple[self.tupleSortIndex]





