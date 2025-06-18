# TFile parser from filename
# Derek Fujimoto
# June 2024

import ROOT
import os
from .tdirectory import tdirectory

class tfile(tdirectory):
    """Contains root file data

    Args:
        filename (str): path to root file to read
        as_dataframe (bool): if true, run to_dataframe upon read
        empty_ok (bool): if true, don't save empty objects
        quiet (bool): if true, don't print skipped statement if object empty
        key_filter (function handle): a function with the following signature:
                bool fn(str) -- takes as input a string and returns a bool
                indicating whether the object with the corresponding key should
                be read
        tree_filter (dict): {treename: (filter_string, [columns])}
            treename (str): name of the tree to apply elements to
            filter_string (str|None): if not none then pass this to [`RDataFrame.Filter`](https://root.cern/doc/master/classROOT_1_1RDF_1_1RInterface.html#ad6a94ba7e70fc8f6425a40a4057d40a0)
            [columns] (list|None): list of column names to include in fetch, if None, get all
    """

    def __init__(self, filename, as_dataframe=False, empty_ok=True, quiet=True,
                 key_filter=None, tree_filter=None):

        if filename is None: return

        # check input
        if not os.path.isfile(filename):
            raise IOError(f'The path "{filename}" does not point to a file')

        # open file
        self._fid = ROOT.TFile(filename, 'READ')

        # get contents
        super().__init__(self._fid,
                         empty_ok=empty_ok,
                         quiet=quiet,
                         key_filter=key_filter,
                         tree_filter=tree_filter,
                         )

        # convert to dataframe
        if as_dataframe:
            self.to_dataframe()

    def copy(self):
        """Make a copy of this object"""

        copy = tfile(None)
        for key, value in self.items():
            if hasattr(value, 'copy'):  copy[key] = value.copy()
            else:                       copy[key] = value
        return copy