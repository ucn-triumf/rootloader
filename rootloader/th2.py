# TH2 parser
# Derek Fujimoto
# June 2024

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

class th2(object):
    """Extract histogram data from ROOT.TH1 data type

    Args:
        hist (ROOT.TH2): histogram to import

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

    __slots__ = ['x', 'y', 'z', 'dz', 'entries', 'name', 'nbinsx', 'nbinsy',
                 'title', 'xlabel', 'ylabel', 'zlabel', 'sum', 'base_class']

    def __init__(self, hist):
        self.base_class = hist.Class_Name()
        self.entries = int(hist.GetEntries())
        self.name = hist.GetName()
        self.sum = hist.GetSum()
        self.nbinsx = int(hist.GetNbinsX())
        self.nbinsy = int(hist.GetNbinsY())
        self.title = hist.GetTitle()
        self.xlabel = hist.GetXaxis().GetName()
        self.ylabel = hist.GetYaxis().GetName()
        self.zlabel = hist.GetZaxis().GetName()

        self.x = np.fromiter((hist.GetXaxis().GetBinCenter(i) for i in range(self.nbinsx)),
                             dtype=float, count=self.nbinsx)
        self.y = np.fromiter((hist.GetYaxis().GetBinCenter(i) for i in range(self.nbinsy)),
                             dtype=float, count=self.nbinsy)

        self.z = np.fromiter((hist.GetBinContent(i, j)  for i in range(self.nbinsx)
                                                        for j in range(self.nbinsy)),
                             dtype=float,
                             count=self.nbinsx*self.nbinsy)

        self.dz = np.fromiter((hist.GetBinError(i, j)   for i in range(self.nbinsx)
                                                        for j in range(self.nbinsy)),
                              dtype=float,
                              count=self.nbinsx*self.nbinsy)

        self.z = self.z.reshape(self.nbinsx, self.nbinsy)
        self.dz = self.dz.reshape(self.nbinsx, self.nbinsy)

    def __len__(self):
        return self.nbins

    def __repr__(self):
        return f'{self.base_class}: "{self.name}", {self.entries} entries, sum = {self.sum}'

    def plot(self, ax=None):
        """Draw the histogram

        Args:
            ax (plt.Axes): if None, draw in current axes, else draw on ax
        """

        # get axes
        if ax is None:
            ax = plt.gcf().add_subplot(projection='3d')

        # draw
        xx, yy = np.meshgrid(self.x, self.y)

        ax.plot_surface(xx, yy, self.z)
        ax.set_xlabel(self.xlabel)
        ax.set_ylabel(self.ylabel)
        ax.set_zlabel(self.zlabel)

    def to_dataframe(self):
        """Convert tree to pandas dataframe

        Returns:
            pd.DataFrame
        """
        xx, yy = np.meshgrid(self.x, self.y)
        idx = pd.MultiIndex.from_arrays((xx.flatten(), yy.flatten()),
                                        names=(self.xlabel, self.ylabel))
        df = pd.DataFrame({self.zlabel: self.z.flatten(),
                           f'{self.zlabel} err': self.dz.flatten()},
                           index=idx)

        return df
