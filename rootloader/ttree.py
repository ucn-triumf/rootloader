    # TTree object for the giant UCN hits trees
# Derek Fujimoto
# June 2025

from .th1 import th1
from .th2 import th2
from collections.abc import Iterable
import pandas as pd
import numpy as np
import os
import ROOT
ROOT.EnableImplicitMT()

class ttree(object):
    """Extract ROOT.TTree with lazy operation. Looks like a dataframe in most ways

    Args:
        tree (str|hitstree): tree to load
        filter_string (str|None): if not none then pass this to [`RDataFrame.Filter`](https://root.cern/doc/master/classROOT_1_1RDF_1_1RInterface.html#ad6a94ba7e70fc8f6425a40a4057d40a0)
        columns (list|None): list of column names to include in fetch, if None, get all
    """

    def __init__(self, tree):

        # copy
        if isinstance(tree, ttree):
            self._rdf = ROOT.RDataFrame(tree._tree)
            self._tree = tree._tree
            self._columns = tree._columns
            self._index = tree._index
            self._filters = tree._filters.copy()
            self.name = tree.name

        # new from path or TTree
        elif isinstance(tree, ROOT.TTree):

            self._rdf = ROOT.RDataFrame(tree)
            self._columns = ('tEntry')
            self._columns = tuple((str(s) for s in self._rdf.GetColumnNames()))
            self._filters = list()
            self._tree = tree
            self.name = tree.GetName()

            # set index, default to times
            if 'tUnixTimePrecise' in self._columns:
                self._index = 'tUnixTimePrecise'
            elif 'timestamp' in self._columns:
                self._index = 'timestamp'
            elif 'tEntry' in self._columns:
                self._index = 'tEntry'
            else:
                self._index = None

        # viewing - see __getitem__
        elif tree is None:
            self.name = None
            return

        else:
            raise RuntimeError(f'tree must be of type ttree|str|ROOT.TTree, not {type(tree)}')

        # set filters
        for filt in self._filters:
            self._rdf = self._rdf.Filter(filt, filt)

        # track stats
        self._stats = {}

    def __dir__(self):
        superdir = [d for d in super().__dir__() if d[0] != '_']
        return sorted(self._columns) + superdir

    def __getattr__(self, name):
        if name in self._columns:
            return self[name]
        else:
            return getattr(object, name)

    def __getitem__(self, key):
        """Fetch a new dataframe with fewer 'columns', as a memory view"""

        h = ttree(None)

        h._tree = self._tree
        h._rdf = self._rdf
        h._columns = self._columns
        h._index = self._index
        h._filters = self._filters
        h._stats = self._stats
        h.name = self.name

        # get list of keys
        if isinstance(key, str):
            h._columns = (key,)
        else:
            h._columns = tuple(key)

        return h

    def __len__(self):
        return self.size

    def __repr__(self):
        klist = list(self._columns)
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

    def hist1d(self, column=None, nbins=None, step=None, edges=None):
        """Return histogram of column

        Args:
            column (str): column name, needed if more than one column
            nbins (int): number of bins, span full range
            step (float): bin spacing, span full range
            edges (array-like): custom bin edges

            Pick one of nbins|step|edges

        Returns:
            rootloader.th1
        """

        # get column name
        if column is None:
            if len(self._columns) > 1:
                raise KeyError('tree has more than one column, please specify')
            column = self._columns[0]
        else:
            if column not in self._columns:
                raise KeyError(f'Column "{column}" must be one of {self._columns}')

        # need at least one of nbins and step and edges
        if nbins is None and step is None and edges is None:
            raise RuntimeError('Specify nbins or step or edges')
        if sum((nbins is not None, step is not None, edges is not None)) > 1:
            raise RuntimeError('Must specify only one of nbins, step, or edges')

        # get via custom edges
        if edges is not None:
            nbins = len(edges)-1
            hist = self._rdf.Histo1D((f'Hist{column}', f";{column};Count", nbins, edges), column)

        # get via nbins or step
        else:

            # range of histogram
            minval = self[column].min()
            maxval = self[column].max()

            # set n bins
            if step is not None:
                nbins = int(np.ceil((maxval-minval)/step))
                maxval = nbins*step + minval    # ensure proper bin size
            nbins = int(nbins)

            # histogram
            hist = self._rdf.Histo1D((f'Hist{column}', f";{column};Count", nbins, minval, maxval), column)

        return th1(hist)

    def hist2d(self, columnx=None, columny=None,
               nxbins=None, nybins=None, xstep=None, ystep=None):
        """Return histogram of two columns

        Args:
            column (str): column name, needed if more than one column
            nbins (int): number of bins, span full range
            step (float): bin spacing, span full range

        Returns:
            rootloader.th2
        """

        # get column names
        if columnx is None:
            if len(self._columns) > 2:
                raise KeyError('tree has more than two columns, please specify')
            elif len(self._columns) < 2:
                raise KeyError('tree has fewer than two columns, please specify')
            columnx = self._columns[0]
        else:
            if columnx not in self._columns:
                raise KeyError(f'Columnx "{columnx}" must be one of {self._columns}')

        if columny is None:
            if len(self._columns) > 2:
                raise KeyError('tree has more than two columns, please specify')
            elif len(self._columns) < 2:
                raise KeyError('tree has fewer than two columns, please specify')
            columny = self._columns[1]
        else:
            if columny not in self._columns:
                raise KeyError(f'Columny "{columny}" must be one of {self._columns}')

        # need at least one of nbins and step
        if nxbins is None and xstep is None:
            raise RuntimeError('Specify nxbins or xstep')
        if nxbins is not None and xstep is not None:
            raise RuntimeError('Must specify either nxbins or xstep, not both')

        if nybins is None and ystep is None:
            raise RuntimeError('Specify nybins or ystep')
        if nybins is not None and ystep is not None:
            raise RuntimeError('Must specify either nybins or ystep, not both')


        # range of histogram
        minvalx = self[columnx].min()
        maxvalx = self[columnx].max()

        minvaly = self[columny].min()
        maxvaly = self[columny].max()

        # set n bins
        if xstep is not None:
            nxbins = int(np.ceil((maxvalx-minvalx)/xstep))
            maxvalx = nxbins*xstep + minvalx    # ensure proper bin size
        nxbins = int(nxbins)

        if ystep is not None:
            nybins = int(np.ceil((maxvaly-minvaly)/ystep))
            maxvaly = nybins*ystep + minvaly    # ensure proper bin size
        nybins = int(nybins)

        # histogram
        hist = self._rdf.Histo2D((f'Hist{columnx}_{columny}',
                                  f";{columnx};{columny}",
                                  nxbins, minvalx, maxvalx,
                                  nybins, minvaly, maxvaly), columnx, columny)

        return th2(hist)

    def reset(self):
        """Make a new tree"""
        return ttree(self._tree)

    def reset_columns(self):
        """Include all columns again"""
        self._columns = tuple((str(s) for s in self._rdf.GetColumnNames()))

    def set_index(self, column):
        """Set the index column name"""
        if column not in self._columns:
            raise KeyError(f'{column} not found in branch names list: {self._columns}')
        self._index = column

    def set_filter(self, expression, inplace=False):
        """Set a filter on the dataframe to select a subset of the data"""

        if inplace:
            self._rdf = self._rdf.Filter(expression, expression)
            self._filters.append(expression)
            self._stats = {}
        else:
            new = ttree(self)
            new.set_filter(expression, inplace=True)
            return new

    def to_dataframe(self):
        """Return pandas dataframe of the data"""

        df = self.to_dict()

        # convert root data types into python data types
        for key, val in df.items():
            if isinstance(val, ROOT.module.cppyy.gbl.std.string):
                df[key] = str(val)
            elif isinstance(val, Iterable):
                if len(val) == 0:
                    df[key] = [np.nan]
                else:
                    if isinstance(val[0], ROOT.module.cppyy.gbl.std.string):
                        df[key] = np.fromiter((str(v) for v in val), dtype=object)
                    elif isinstance(val[0], (ROOT.RVec('int'), ROOT.RVec('float'))):
                        df[key] = np.fromiter((np.asarray(v) for v in val), dtype=object)

        df = pd.DataFrame(df)

        # set index
        if self._index is not None:
            df.set_index(self._index, inplace=True)

        # convert to series?
        if len(df.columns) == 1:
            return df[df.columns[0]]

        return df

    def to_dict(self):

        # ensure index is loaded
        if self._index not in self._columns and self._index is not None:
            columns = [*self._columns, self._index]
        else:
            columns = self._columns

        return self._rdf.AsNumpy(columns=columns)

    # PROPERTIES ===========================
    @property
    def columns(self):
        return self._columns
    @property
    def filters(self):
        return self._filters
    @property
    def index(self):
        return self[self._index]
    @property
    def index_name(self):
        return self._index
    @property
    def loc(self):
        return _ttree_indexed(self)
    @property
    def size(self):
        try:
            return self._stats['size']
        except KeyError:
            self._stats['size'] = self._rdf.Count().GetValue()
            return self.size

    # STATS ================================
    def _get_stats(self, col):
        try:
            return self._stats[col]
        except KeyError:
            self._stats[col] = self._rdf.Stats(col).GetValue()
            return self._stats[col]

    def min(self):
        vals = [self._get_stats(col).GetMin() for col in self._columns]
        if len(vals) == 1:  return vals[0]
        return pd.Series(vals, index=self._columns)

    def max(self):
        vals = [self._get_stats(col).GetMax() for col in self._columns]
        if len(vals) == 1:  return vals[0]
        return pd.Series(vals, index=self._columns)

    def mean(self):
        vals = [self._get_stats(col).GetMean() for col in self._columns]
        if len(vals) == 1:  return vals[0]
        return pd.Series(vals, index=self._columns)

    def rms(self):
        vals = [self._get_stats(col).GetRMS() for col in self._columns]
        if len(vals) == 1:  return vals[0]
        return pd.Series(vals, index=self._columns)

    def std(self):
        vals = [self._rdf.StdDev(col).GetValue() for col in self._columns]
        if len(vals) == 1:  return vals[0]
        return pd.Series(vals, index=self._columns)

# ttree but slice on time
class _ttree_indexed(object):

    def __init__(self, tree):
        self._tree = ttree(tree)

    def __getitem__(self, key):

        # get rdataframe
        tr = self._tree

        # set fancy slicing
        if isinstance(key, slice):
            if key.start is not None:
                tr.set_filter(f'{tr._index} >= {key.start}', inplace=True)
            if key.stop is not None:
                tr.set_filter(f'{tr._index} < {key.stop}', inplace=True)
            if key.step is not None:
                raise NotImplementedError('Slicing steps not implemented')

        elif isinstance(key, (int, float)):
            tr.set_filter(f'{self._index} == {key}', inplace=True)

        return tr
