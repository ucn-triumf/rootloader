# TLeaf parser
# Derek Fujimoto
# June 2024

import numpy as np

class tleaf(object):
    """Ease of access for ROOT.TLeaf

    Args:
        leaf (ROOT.TLeaf): root leaf object
    """

    def __init__(self, leaf):
        self._leaf = leaf

    def copy(self):
        """Make a copy of this object"""
        return tleaf(self._leaf.copy())

    def get_entry(self, i):
        self._leaf.GetBranch().GetEntry(i)
        return self.value

    @property
    def branch(self): return self._leaf.GetBranch().GetName()
    @property
    def fullname(self): return self._leaf.GetFullName()
    @property
    def name(self): return self._leaf.GetName()
    @property
    def leaftype(self): return self._leaf.ClassName()[-1].lower()
    @property
    def len(self): return self._leaf.GetLen()
    @property
    def value(self):
        if self.len == 1:
            return self._leaf.GetValue()
        else:
            return np.fromiter((self._leaf.GetValue(i) for i in range(self.len)),
                               dtype = self.leaftype)

