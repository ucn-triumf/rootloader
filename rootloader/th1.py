# TH1 parser
# Derek Fujimoto
# June 2024

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

class th1(object):
    """Extract histogram data from ROOT.TH1 data type

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
        """Constructor

        Args:
            hist (ROOT.TH1): histogram to import"""

        self.base_class = hist.Class_Name()
        self.entries = int(hist.GetEntries())
        self.name = hist.GetName()
        self.sum = hist.GetSum()
        self.nbins = int(hist.GetNbinsX())
        self.title = hist.GetTitle()
        self.xlabel = hist.GetXaxis().GetName()
        self.ylabel = hist.GetYaxis().GetName()

        self.x = np.fromiter((hist.GetBinCenter(i) for i in range(self.nbins)),
                             dtype=float,
                             count=self.nbins)
        self.y = np.fromiter((hist.GetBinContent(i) for i in range(self.nbins)),
                             dtype=float,
                             count=self.nbins)
        self.dy = np.fromiter((hist.GetBinError(i) for i in range(self.nbins)),
                             dtype=float,
                             count=self.nbins)

    def __len__(self):
        return self.nbins

    def __repr__(self):
        return f'{self.base_class}: "{self.name}", {self.entries} entries, sum = {self.sum}'

    def plot(self, ax=None, **kwargs):
        """Draw the histogram

        Args:
            ax (plt.Axes): if None, draw in current axes, else draw on ax
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
