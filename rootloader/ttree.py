# TTree parser
# Derek Fujimoto
# June 2024

from .attrdict import attrdict
from tqdm import tqdm
import numpy as np
import pandas as pd
import os
import ROOT
ROOT.EnableImplicitMT()

class ttree(attrdict):
    """Extract ROOT.TTree fully into memory

    Args:
        tree (ROOT.TTree): tree to load
    """

    def __init__(self, tree):

        if tree is None:
            return

        # extraction of data: fast
        try:
            data = self._extract_event_fast(tree)

        # if there is a problem, revert to slower, but more robust version
        except Exception:

            tqdm.write("Reverting to robust ttree reader")
            entries = tree.GetEntries()
            if entries == 0: return

            iterator = tqdm(zip(tree, range(entries)), total=entries, leave=False,
                            desc=f'Loading {tree.GetName()}')
            data = pd.concat(map(self._extract_event, iterator))

            # setup tree structure in self
            for br in tree.GetListOfBranches():
                branch = attrdict()
                for leaf in br.GetListOfLeaves():
                    branch[leaf.GetName()] = data.loc[:, f'{leaf.GetFullName()}']

                if len(list(branch.keys())) > 1:
                    setattr(self, br.GetName(), branch)
                else:
                    setattr(self, br.GetName(), branch[leaf.GetName()])

    def __dir__(self):
        return sorted(self.keys())

    def __repr__(self):
        klist = list(self.keys())
        if klist:
            klist.sort()

            # get number of columns based on terminal size
            maxsize = max((len(k) for k in klist)) + 2
            terminal_width = os.get_terminal_size().columns - 4 # indent by 4 spaces below
            ncolumns = int(np.floor(terminal_width / maxsize))
            ncolumns = min(ncolumns, len(klist))

            # split into chunks
            needed_len = int(np.ceil(len(klist) / ncolumns)*ncolumns) - len(klist)
            klist = np.concatenate((klist, np.full(needed_len, '')))
            klist = np.array_split(klist, ncolumns)

            # print
            s = 'ttree branches:\n'
            for key in zip(*klist):
                s += ' '*4
                s += ''.join(['{0: <{1}}'.format(k, maxsize) for k in key])
                s += '\n'
            return s
        else:
            return self.__class__.__name__ + "()"

    def _extract_event_fast(self, tree):
        # fast version of getting events using RDataFrame
        data = ROOT.RDataFrame(tree).AsNumpy()
        for key, value in data.items():
            setattr(self, key, pd.Series(value))

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
        """Return a copy of self but only for a subset of entries

        Args:
            entries (list|np.array): list of entries to get from tree

        Returns:
            ttree: copy with reduced entries
        """

        copy = ttree(None)

        for brname, br in self.items():
            if type(br) is attrdict:
                newbr = attrdict()
                for leafname, leaf in br.items():
                    newbr[leafname] = leaf[entries]
                setattr(copy, brname, newbr)
            else:
                setattr(copy, brname, br.loc[entries])
        return copy

    def plot(self, *args, **kwargs):
        """Convert to dataframe and plot. Arguments passed to [pandas.DataFrame.plot](https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.plot.html)

        Returns:
            same as pandas.DataFrame.plot
        """
        return self.to_dataframe().plot(*args, **kwargs)

    def to_dataframe(self):
        """Convert tree to pandas dataframe

        Returns:
            pd.DataFrame
        """

        df = pd.DataFrame(self)
        if 'timestamp' in df.columns:
            df.set_index('timestamp', inplace=True)
        return df
