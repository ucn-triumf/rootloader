# TFile parser from filename
# Derek Fujimoto
# June 2024

import ROOT
from .tdirectory import tdirectory

class tfile(tdirectory):
    """Contains root file data"""

    def __init__(self, filename, as_dataframe=False):
        """Read the file

        Args:
            filename (str): path to root file to read
            as_dataframe (bool): if true, run to_dataframe upon read
        """

        # open file
        fid = ROOT.TFile(filename, 'READ')

        # get contents
        super().__init__(fid)

        # close the file
        fid.Close()

        # convert to dataframe
        if as_dataframe:
            self.to_dataframe()