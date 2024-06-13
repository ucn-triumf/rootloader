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
    """

    def __init__(self, filename, as_dataframe=False, empty_ok=True):
        # check input
        if not os.path.isfile(filename):
            raise IOError(f'The path "{filename}" does not point to a file')

        # open file
        fid = ROOT.TFile(filename, 'READ')

        # get contents
        super().__init__(fid, empty_ok=empty_ok)

        # close the file
        fid.Close()

        # convert to dataframe
        if as_dataframe:
            self.to_dataframe()