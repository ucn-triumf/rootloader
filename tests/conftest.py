"""Shared fixtures for the rootloader test suite.

All fixtures that build ROOT objects must keep Python references alive for the
test's duration; ROOT frees objects when their Python wrapper is GC'd.

Gotchas addressed here:
  - os.get_terminal_size() raises OSError under pytest's captured stdout;
    patched globally via patch_terminal_size (autouse).
  - ROOT.EnableImplicitMT() (called at ttree import) reorders RDataFrame rows;
    the single_mt fixture disables MT for order-sensitive tests.
  - TH1/TH2 auto-register in gDirectory; SetDirectory(0) prevents deletion on
    file close for standalone histograms.
"""

import os
from array import array

import matplotlib
import numpy as np
import pytest
import ROOT


# ---------------------------------------------------------------------------
# Environment patches (autouse — always applied)
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def patch_terminal_size(monkeypatch):
    """Patch os.get_terminal_size so repr() methods don't raise under pytest."""
    # Accept the optional fd argument that shutil.get_terminal_size passes when
    # called by pytest's terminal reporter (e.g. with -v).  Without this,
    # pytest raises TypeError("takes 0 positional arguments but 1 was given")
    # and crashes with INTERNALERROR.
    monkeypatch.setattr(os, "get_terminal_size", lambda fd=None: os.terminal_size((80, 24)))


@pytest.fixture(autouse=True)
def mpl_agg():
    """Force the non-interactive Agg backend so plot() never opens a window."""
    matplotlib.use("Agg")


# ---------------------------------------------------------------------------
# Optional fixtures (not autouse)
# ---------------------------------------------------------------------------

@pytest.fixture
def single_mt():
    """Disable ROOT implicit multithreading for tests that assert on row order.

    RDataFrame.AsNumpy() does *not* guarantee row order when MT is active.
    Use this fixture for any test that compares arrays element-by-element.
    Re-enables MT in teardown.
    """
    ROOT.DisableImplicitMT()
    yield
    ROOT.EnableImplicitMT()


# ---------------------------------------------------------------------------
# Histogram factories
# ---------------------------------------------------------------------------

# Unique name counter shared across the module so repeated fixture calls never
# collide in ROOT's global object registry.
_name_counter = [0]


def _unique(prefix: str) -> str:
    _name_counter[0] += 1
    return f"{prefix}_{_name_counter[0]}"


@pytest.fixture
def make_th1():
    """Factory that returns a filled ROOT.TH1F.

    Usage::

        def test_foo(make_th1):
            hist = make_th1(nbins=10, xmin=0.0, xmax=10.0)

    The histogram is detached from gDirectory (SetDirectory(0)) so it is not
    deleted when a parent file closes.

    Deterministic fill: bin i (1-indexed) gets content i and error sqrt(i).
    """

    def _make(nbins: int = 10, xmin: float = 0.0, xmax: float = 10.0) -> ROOT.TH1F:
        hist = ROOT.TH1F(_unique("h1"), "Test Histogram;x axis;y axis",
                         nbins, xmin, xmax)
        hist.SetDirectory(0)
        for i in range(1, nbins + 1):
            hist.SetBinContent(i, float(i))
            hist.SetBinError(i, float(i) ** 0.5)
        return hist

    return _make


@pytest.fixture
def make_th2():
    """Factory that returns a filled ROOT.TH2F.

    Usage::

        def test_foo(make_th2):
            hist = make_th2(nbinsx=5, nbinsy=4)

    Detached from gDirectory (SetDirectory(0)).
    Deterministic fill: bin (i, j) gets content i*10+j and error sqrt(i*10+j).
    """

    def _make(nbinsx: int = 5, nbinsy: int = 4,
              xmin: float = 0.0, xmax: float = 5.0,
              ymin: float = 0.0, ymax: float = 4.0) -> ROOT.TH2F:
        hist = ROOT.TH2F(_unique("h2"), "Test 2D Histogram;x axis;y axis;z axis",
                         nbinsx, xmin, xmax, nbinsy, ymin, ymax)
        hist.SetDirectory(0)
        for i in range(1, nbinsx + 1):
            for j in range(1, nbinsy + 1):
                val = float(i * 10 + j)
                hist.SetBinContent(i, j, val)
                hist.SetBinError(i, j, val ** 0.5)
        return hist

    return _make


# ---------------------------------------------------------------------------
# Tree factory
# ---------------------------------------------------------------------------

@pytest.fixture
def make_tree():
    """Factory that builds an in-memory ROOT.TTree from a column dict.

    Usage::

        def test_foo(make_tree):
            tree = make_tree({"x": np.arange(10, dtype=float),
                              "n": np.arange(10, dtype=int)})

    Column arrays with integer dtype → /I (int32) branches.
    Column arrays with float dtype  → /D (double) branches.

    Both the TTree and all branch buffers are kept alive until the test ends.
    """
    # Holds (tree, buffers) tuples for the fixture's lifetime to prevent GC.
    _alive: list = []

    def _make(columns: dict, name: str = "test_tree") -> ROOT.TTree:
        tree = ROOT.TTree(name, name)
        bufs: dict = {}

        for col, data in columns.items():
            arr = np.asarray(data)
            if np.issubdtype(arr.dtype, np.integer):
                buf = array("i", [0])
                tree.Branch(col, buf, f"{col}/I")
            else:
                buf = array("d", [0.0])
                tree.Branch(col, buf, f"{col}/D")
            bufs[col] = (buf, arr)

        n = len(next(iter(columns.values())))
        for i in range(n):
            for col, (buf, arr) in bufs.items():
                buf[0] = type(buf[0])(arr[i])
            tree.Fill()

        _alive.append((tree, bufs))
        return tree

    yield _make
    _alive.clear()


# ---------------------------------------------------------------------------
# In-memory file fixture
# ---------------------------------------------------------------------------

@pytest.fixture
def memfile():
    """An in-memory ROOT.TMemFile with tree + th1 + th2 + nested directory.

    Yields:
        fid (ROOT.TMemFile): the open in-memory file (readable via tdirectory)

    Structure written to fid::

        mytree    — TTree: tEntry/D, x/D, y/I   (50 rows)
        myhist    — TH1F: 10 bins, bins 1..10 filled with i
        myhist2d  — TH2F: 5×4 bins, bin (i,j) = i*10+j
        subdir/   — TDirectoryFile
            subhist — TH1F: 5 bins

    All objects are written before the file is yielded. The TMemFile stays
    open until teardown so that tdirectory can read its keys.
    """
    fid = ROOT.TMemFile("memtestfile", "RECREATE")

    # --- TTree ---
    fid.cd()
    n = 50
    tree = ROOT.TTree("mytree", "My Tree")
    tentry_buf = array("d", [0.0])
    x_buf = array("d", [0.0])
    y_buf = array("i", [0])
    tree.Branch("tEntry", tentry_buf, "tEntry/D")
    tree.Branch("x", x_buf, "x/D")
    tree.Branch("y", y_buf, "y/I")
    for i in range(n):
        tentry_buf[0] = float(i)
        x_buf[0] = float(i)
        y_buf[0] = i
        tree.Fill()
    tree.Write()

    # --- TH1F ---
    h1 = ROOT.TH1F("myhist", "My Histogram;x axis;counts", 10, 0.0, 10.0)
    h1.SetDirectory(fid)
    for i in range(1, 11):
        h1.SetBinContent(i, float(i))
        h1.SetBinError(i, float(i) ** 0.5)
    h1.Write()

    # --- TH2F ---
    h2 = ROOT.TH2F("myhist2d", "My 2D Histogram;x axis;y axis;z axis",
                   5, 0.0, 5.0, 4, 0.0, 4.0)
    h2.SetDirectory(fid)
    for i in range(1, 6):
        for j in range(1, 5):
            val = float(i * 10 + j)
            h2.SetBinContent(i, j, val)
            h2.SetBinError(i, j, val ** 0.5)
    h2.Write()

    # --- Nested directory ---
    subdir = fid.mkdir("subdir")
    subdir.cd()
    subhist = ROOT.TH1F("subhist", "Sub Histogram;x axis;counts", 5, 0.0, 5.0)
    subhist.SetDirectory(subdir)
    for i in range(1, 6):
        subhist.SetBinContent(i, float(i))
    subhist.Write()

    fid.cd()
    fid.Write("", ROOT.TObject.kOverwrite)

    # Keep Python references alive so ROOT doesn't GC them while fid is open.
    yield fid, tree, h1, h2, subhist

    fid.Close()


# ---------------------------------------------------------------------------
# On-disk file fixture
# ---------------------------------------------------------------------------

@pytest.fixture
def root_file_path(tmp_path):
    """Write a populated ROOT file to disk and yield its path.

    The file is closed before the path is yielded, so tests can open it fresh
    with ROOT.TFile(path, 'READ') or rootloader.tfile(path).

    Structure mirrors memfile::

        mytree, myhist, myhist2d, subdir/subhist
    """
    path = str(tmp_path / "test.root")
    fid = ROOT.TFile(path, "RECREATE")

    # --- TTree ---
    n = 50
    tree = ROOT.TTree("mytree", "My Tree")
    tentry_buf = array("d", [0.0])
    x_buf = array("d", [0.0])
    y_buf = array("i", [0])
    tree.Branch("tEntry", tentry_buf, "tEntry/D")
    tree.Branch("x", x_buf, "x/D")
    tree.Branch("y", y_buf, "y/I")
    for i in range(n):
        tentry_buf[0] = float(i)
        x_buf[0] = float(i)
        y_buf[0] = i
        tree.Fill()
    tree.Write()

    # --- TH1F ---
    h1 = ROOT.TH1F("myhist", "My Histogram;x axis;counts", 10, 0.0, 10.0)
    h1.SetDirectory(fid)
    for i in range(1, 11):
        h1.SetBinContent(i, float(i))
    h1.Write()

    # --- TH2F ---
    h2 = ROOT.TH2F("myhist2d", "My 2D Histogram;x axis;y axis;z axis",
                   5, 0.0, 5.0, 4, 0.0, 4.0)
    h2.SetDirectory(fid)
    for i in range(1, 6):
        for j in range(1, 5):
            h2.SetBinContent(i, j, float(i * 10 + j))
    h2.Write()

    # --- Nested directory ---
    subdir = fid.mkdir("subdir")
    subdir.cd()
    subhist = ROOT.TH1F("subhist", "Sub Histogram;x axis;counts", 5, 0.0, 5.0)
    subhist.SetDirectory(subdir)
    subhist.Write()
    fid.cd()

    fid.Write("", ROOT.TObject.kOverwrite)
    fid.Close()

    yield path
