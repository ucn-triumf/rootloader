# TH1 parser
# Derek Fujimoto
# June 2024

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

class th1(object):
    """Extract histogram data from ROOT.TH1 data type

    Args:
        hist (ROOT.TH1): histogram to import

    Attributes:
        bbase_class (str): output of TH1.Class_Name()
        entries (int): output of TH1.GetEntries()
        name (str): output of TH1.GetName()
        nbins (int): output of TH1.GetNbinsX()
        sum (float): output of TH1.GetSum()
        title (str): output of TH1.GetTitle()
        xlabel (str): output of TH1.GetXaxis.GetName()
        ylabel (str): output of TH1.GetYaxis.GetName()

        x (np.array): bin centers
        y (np.array): bin content
        dy (np.array): bin error
    """

    __slots__ = ['x', 'y', 'dy', 'entries', 'name', 'nbins', 'title', 'xlabel',
                 'ylabel', 'sum', 'base_class']

    draw_defaults = {'fmt': '.',
                     'capsize': 0,
                     }

    def __init__(self, hist):
        self.base_class = hist.Class_Name()
        self.entries = int(hist.GetEntries())
        self.name = hist.GetName()
        self.sum = hist.GetSum()
        self.nbins = int(hist.GetNbinsX())
        self.title = hist.GetTitle()
        self.xlabel = hist.GetXaxis().GetTitle()
        self.ylabel = hist.GetYaxis().GetTitle()

        self.x = np.fromiter(map(hist.GetBinCenter, range(self.nbins)),
                             dtype=float,
                             count=self.nbins)
        self.y = np.fromiter(map(hist.GetBinContent, range(self.nbins)),
                             dtype=float,
                             count=self.nbins)
        self.dy = np.fromiter(map(hist.GetBinError, range(self.nbins)),
                             dtype=float,
                             count=self.nbins)

    def __len__(self):
        return self.nbins

    def __repr__(self):
        return f'{self.base_class}: "{self.name}", {self.entries} entries, sum = {self.sum}'

    def plot(self, ax=None, data_only=False, **kwargs):
        """Draw the histogram

        Args:
            ax (plt.Axes): if None, draw in current axes, else draw on ax
            data_only (bool): if true don't set axis labels, title
            kwargs: passed to matplotlib.pyplot.errorbar
        """

        # get axes
        if ax is None:
            ax = plt.gca()

        # get kwargs defaults if not present
        for key, val in self.draw_defaults.items():
            if key not in kwargs.keys():
                kwargs[key] = val

        # draw
        ax.errorbar(self.x, self.y, self.dy, **kwargs)

        # plot elements
        if not data_only:
            ax.set_xlabel(self.xlabel)
            ax.set_ylabel(self.ylabel)
            ax.set_title(self.title, fontsize='x-small')
            plt.tight_layout()

    def to_dataframe(self):
        """Convert tree to pandas dataframe

        Returns:
            pd.DataFrame
        """

        df = {self.xlabel: self.x,
              self.ylabel: self.y,
              self.ylabel + " error": self.dy,
             }
        return pd.DataFrame(df)
