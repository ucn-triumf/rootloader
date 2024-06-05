# TTree parser
# Derek Fujimoto
# June 2024

from .attrdict import attrdict
from tqdm import tqdm
import numpy as np
import pandas as pd
import os

class ttree(attrdict):
    """Extract ROOT.TTree fully into memory"""

    def __init__(self, tree):
        """Constructor

        Args:
            tree (ROOT.TTree): tree to load
        """

        self.__dict__ = {}

        # extraction of data
        entries = tree.GetEntries()
        if entries == 0: return

        iterator = tqdm(zip(tree, range(entries)), total=entries, leave=False,
                        desc=f'Reading {tree.GetName()}')
        data = pd.concat(map(self._extract_event, iterator))

        # setup tree structure in self
        for br in tree.GetListOfBranches():
            branch = attrdict()
            for leaf in br.GetListOfLeaves():
                branch[leaf.GetName()] = data.loc[:, f'{leaf.GetFullName()}']

            if len(list(branch.keys())) > 1:
                setattr(self, br.GetName(), branch)
                self.__dict__[br.GetName()] = branch
            else:
                setattr(self, br.GetName(), branch[leaf.GetName()])
                self.__dict__[br.GetName()] = branch[leaf.GetName()]

    def __dir__(self):
        return sorted(self.keys())

    def __repr__(self):
        klist = [k for k in self.keys() if k != '__dict__']
        if klist:
            klist.sort()
            maxsize = max((len(k) for k in klist)) + 2
            terminal_width = os.get_terminal_size().columns
            ncolumns = int(np.floor(terminal_width / maxsize))
            ncolumns = min(ncolumns, len(klist))

            s = 'ttree branches:\n'
            for key in zip(*[klist[i::ncolumns] for i in range(ncolumns)]):
                s += '\t'
                s += ''.join(['{0: <{1}}'.format(k, maxsize) for k in key])
                s += '\n'
            return s
        else:
            return self.__class__.__name__ + "()"

    def _extract_event(self, tree_entry):
        leaves = {}

        tree, entry = tree_entry
        for leaf in tree.GetListOfLeaves():
            name = str(leaf.GetFullName())
            len = leaf.GetLen()

            # strings are special
            if leaf.ClassName() == "TLeafElement":
                leaftype = 'str'

            # numerical data types
            else:
                leaftype = leaf.ClassName()[-1].lower()


            if len == 1:
                if leaftype == 'str':
                    leaves[name] = ''.join((x for x in getattr(tree, name)))
                else:
                    leaves[name] = [leaf.GetValue()]
            else:
                leaves[name] = [np.fromiter((leaf.GetValue(i) for i in range(len)),
                                        dtype = leaftype)]

        return pd.DataFrame(leaves, index=[entry])

    def get_subtree(self, entries):
        """Return a copy of self but only for a subset of entries"""

        copy = ttree()

        for brname, br in self.__dict__.items():
            if type(br) is attrdict:
                newbr = attrdict()
                for leafname, leaf in br.items():
                    newbr[leafname] = leaf[entries]
                setattr(copy, brname, newbr)
            else:
                setattr(copy, brname, br.loc[entries])
        return copy

    def to_dataframe(self):
        """Convert tree to pandas dataframe

        Returns:
            pd.DataFrame
        """

        df = pd.DataFrame(self)
        df.drop(columns='__dict__', inplace=True)
        if 'timestamp' in df.columns:
            df.set_index('timestamp', inplace=True)
        return df
