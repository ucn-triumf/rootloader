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
import pandas as pd
import ROOT

class tdirectory(attrdict):
    """Contains root file data

    Args:
        directory (ROOT.TDirectoryFile|ROOT.TFile): object to parse
        empty_ok (bool): if true, save empty objects
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

    def __init__(self, directory, empty_ok=True, quiet=True, key_filter=None,
                 tree_filter=None):

        # copy
        if directory is None: return

        # defaults
        if key_filter is None: key_filter = lambda x: True
        tree_filter = {} if tree_filter is None else tree_filter

        # get keys and read only those with highest cycle number
        keys = {}
        for key in directory.GetListOfKeys():
            name = key.GetName()

            # filter
            if key_filter(name):

                # keep key if not yet in dict
                if name not in keys.keys():
                    keys[name] = (name, key.GetCycle())
                else:

                    # keep key with largest cycle number
                    if key.GetCycle() > keys[name][1]:
                        keys[name] = (name, key.GetCycle())

        # read trees and histograms from data file
        for name, cycle in tqdm(keys.values(), desc=f'Loading {directory.GetName()}',
                              leave=False, total=len(keys)):
            obj = directory.Get(f'{name};{cycle}')
            classname = obj.ClassName()

            # TTree
            if 'TTree' == classname:
                if empty_ok or obj.GetEntries() > 0:
                    self[name] = ttree(obj)
                elif not quiet:
                    tqdm.write(f'Skipped "{name}" due to lack of entries')

            # TH1
            elif 'TH1' in classname:
                if empty_ok or obj.GetSum() > 0:
                    self[name] = th1(obj)
                elif not quiet:
                    tqdm.write(f'Skipped "{name}" due to lack of entries')

            # TH2
            elif 'TH2' in classname:
                if empty_ok or obj.GetSum() > 0:
                    self[name] = th2(obj)
                elif not quiet:
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

            # drop hidden variables
            klist = [k for k in klist if k[0] != '_']

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
            s = 'contents:\n'
            for key in zip(*klist):
                s += ' '*4
                s += ''.join(['{0: <{1}}'.format(k, maxsize) for k in key])
                s += '\n'
            return s
        else:
            return self.__class__.__name__ + "()"

    def copy(self):
        """Make a copy of this object"""

        copy = tdirectory(None)
        for key, value in self.items():
            if hasattr(value, 'copy'):  copy[key] = value.copy()
            else:                       copy[key] = value
        return copy

    def from_dataframe(self):
        """Convert all elements contained in self to original objects"""

        for key, value in self.items():
            try:
                self[key] = value.attrs['type'](value)
            except AttributeError as err:
                print(f'{key} does not have proper attribute to be backconverted')
            except KeyError as err:
                print(f'{key} does not know its own type to be backconverted')

    def to_dataframe(self):
        """Convert all objects possible (th1, th2, and ttree) into pandas dataframes"""
        for k in self.keys():
            if type(self[k]) is not pd.DataFrame:
                try:
                    self[k] = self[k].to_dataframe()
                except AttributeError:
                    pass