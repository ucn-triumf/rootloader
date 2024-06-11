# TDirectoryFile or TFile parser
# Derek Fujimoto
# June 2024

from .attrdict import attrdict
from .ttree import ttree
from .th1 import th1
from .th2 import th2
import warnings, os
import numpy as np
from tqdm import tqdm

class tdirectory(attrdict):
    """Contains root file data

    Args:
            directory (ROOT.TDirectoryFile|ROOT.TFile): object to parse
            keep_empty_objs (bool): if true, don't save empty objects
    """

    def __init__(self, directory, keep_empty_objs=True):

        # read trees and histograms from data file
        for key in tqdm(directory.GetListOfKeys(), desc=f'Loading {directory.GetName()}', leave=False):
            name = key.GetName()
            obj = directory.Get(name)
            classname = obj.ClassName()

            # TTree
            if 'TTree' == classname:
                if keep_empty_objs or obj.GetEntries() > 0:
                    self[name] = ttree(obj)
                else:
                    tqdm.write(f'Skipped "{name}" due to lack of entries')

            # TH1
            elif 'TH1' in classname:
                if keep_empty_objs or obj.GetSum() > 0:
                    self[name] = th1(obj)
                else:
                    tqdm.write(f'Skipped "{name}" due to lack of entries')

            # TH2
            elif 'TH2' in classname:
                if keep_empty_objs or obj.GetSum() > 0:
                    self[name] = th2(obj)
                else:
                    tqdm.write(f'Skipped "{name}" due to lack of entries')

            # TDirectory
            elif 'TDirectoryFile' == classname:
                self[name] = tdirectory(obj)

            else:
                warnings.warn(f'Unknown class "{classname}" for key "{name}".')

    def __repr__(self):
        klist = list(self.keys())
        if klist:
            klist.sort()
            maxsize = max((len(k) for k in klist)) + 2
            terminal_width = os.get_terminal_size().columns
            ncolumns = int(np.floor(terminal_width / maxsize))
            ncolumns = min(ncolumns, len(klist))

            s = 'contents:\n'
            for key in zip(*[klist[i::ncolumns] for i in range(ncolumns)]):
                s += '\t'
                s += ''.join(['{0: <{1}}'.format(k, maxsize) for k in key])
                s += '\n'
            return s
        else:
            return self.__class__.__name__ + "()"

    def to_dataframe(self):
        """Convert all objects possible (th1 and ttree) into pandas dataframes"""
        for k in self.keys():
            try:
                self[k] = self[k].to_dataframe()
            except AttributeError:
                pass