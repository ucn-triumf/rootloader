# TFile parser from filename
# Derek Fujimoto
# June 2024

import ROOT
import os
from .tdirectory import tdirectory

class tfile(tdirectory):
    """Contains root file data"""

    def __init__(self, filename, as_dataframe=False, keep_empty_objs=True):
        """Read the file

        Args:
            filename (str): path to root file to read
            as_dataframe (bool): if true, run to_dataframe upon read
            keep_empty_objs (bool): if true, don't save empty objects
        """

        # check input
        if not os.path.isfile(filename):
            raise IOError(f'The path "{filename}" does not point to a file')

        # open file
        fid = ROOT.TFile(filename, 'READ')

        # get contents
        super().__init__(fid, keep_empty_objs=keep_empty_objs)

        # close the file
        fid.Close()

        # convert to dataframe
        if as_dataframe:
            self.to_dataframe()