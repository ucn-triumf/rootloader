"""Tests for rootloader.th1.

Covers construction from ROOT.TH1F, metadata extraction, bin-content correctness,
copy(), to_dataframe(), round-trip reconstruction, and plot() behaviour.

Bin-indexing note: th1.__init__ reads bins via range(nbins) = 0..nbins-1.
ROOT bin 0 is the underflow bin, so x[0]/y[0] correspond to the underflow slot.
The make_th1 fixture fills bins 1..nbins, giving y[0]=0, y[1]=1.0, y[2]=2.0, etc.
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import pytest

from rootloader import th1


# ---------------------------------------------------------------------------
# Construction from ROOT.TH1F
# ---------------------------------------------------------------------------

def test_init_metadata(make_th1):
    """Metadata fields are populated correctly from a ROOT TH1F.

    Checks name, title, nbins, entries, xlabel, ylabel, base_class, and sum.
    """
    root_hist = make_th1(nbins=10, xmin=0.0, xmax=10.0)
    h = th1(root_hist)

    assert h.name == root_hist.GetName()
    assert h.title == "Test Histogram"
    assert h.nbins == 10
    assert h.entries == int(root_hist.GetEntries())
    assert h.xlabel == "x axis"
    assert h.ylabel == "y axis"
    assert h.base_class == root_hist.Class_Name()
    # sum of contents in bins 1..10 = 1+2+...+10 = 55
    assert h.sum == pytest.approx(55.0)


def test_init_arrays_are_numpy(make_th1):
    """x, y, and dy are numpy arrays of length nbins after construction."""
    root_hist = make_th1(nbins=10, xmin=0.0, xmax=10.0)
    h = th1(root_hist)

    assert isinstance(h.x, np.ndarray)
    assert isinstance(h.y, np.ndarray)
    assert isinstance(h.dy, np.ndarray)
    assert len(h.x) == h.nbins
    assert len(h.y) == h.nbins
    assert len(h.dy) == h.nbins


def test_init_bin_contents(make_th1):
    """Bin contents match the deterministic fill pattern.

    ROOT bin 0 is the underflow; y[0]=0, y[1]=1.0, ..., y[nbins]=nbins.
    Errors are sqrt of the content for filled bins; underflow error is 0.
    """
    nbins = 10
    root_hist = make_th1(nbins=nbins, xmin=0.0, xmax=10.0)
    h = th1(root_hist)

    # Underflow bin (index 0) has content 0
    assert h.y[0] == pytest.approx(0.0)
    assert h.dy[0] == pytest.approx(0.0)

    # Filled bins 1..nbins-1 (0-indexed into th1's arrays)
    for i in range(1, nbins):
        assert h.y[i] == pytest.approx(float(i))
        assert h.dy[i] == pytest.approx(float(i) ** 0.5)


# ---------------------------------------------------------------------------
# __len__ and __repr__
# ---------------------------------------------------------------------------

def test_len(make_th1):
    """len(h) returns nbins."""
    root_hist = make_th1(nbins=7, xmin=0.0, xmax=7.0)
    h = th1(root_hist)
    assert len(h) == 7


def test_repr_contains_class_entries_sum(make_th1):
    """__repr__ includes the ROOT class name, entry count, and sum."""
    root_hist = make_th1(nbins=10, xmin=0.0, xmax=10.0)
    h = th1(root_hist)
    r = repr(h)

    assert h.base_class in r
    assert str(h.entries) in r
    assert str(h.sum) in r


# ---------------------------------------------------------------------------
# copy()
# ---------------------------------------------------------------------------

def test_copy_independent_arrays(make_th1):
    """copy() returns an object whose arrays are equal but independent.

    Mutating the copy's arrays does not affect the original.
    """
    root_hist = make_th1(nbins=10, xmin=0.0, xmax=10.0)
    h = th1(root_hist)
    c = h.copy()

    # Values equal before mutation
    np.testing.assert_array_equal(c.x, h.x)
    np.testing.assert_array_equal(c.y, h.y)
    np.testing.assert_array_equal(c.dy, h.dy)

    # Mutating the copy leaves the original intact
    c.y[1] = 999.0
    assert h.y[1] == pytest.approx(1.0)


def test_copy_metadata_equal(make_th1):
    """copy() preserves all scalar metadata fields."""
    root_hist = make_th1(nbins=10, xmin=0.0, xmax=10.0)
    h = th1(root_hist)
    c = h.copy()

    assert c.name == h.name
    assert c.title == h.title
    assert c.nbins == h.nbins
    assert c.entries == h.entries
    assert c.xlabel == h.xlabel
    assert c.ylabel == h.ylabel
    assert c.sum == pytest.approx(h.sum)
    assert c.base_class == h.base_class


# ---------------------------------------------------------------------------
# to_dataframe()
# ---------------------------------------------------------------------------

def test_to_dataframe_columns(make_th1):
    """to_dataframe() produces columns named xlabel, ylabel, and ylabel+' error'."""
    root_hist = make_th1(nbins=10, xmin=0.0, xmax=10.0)
    h = th1(root_hist)
    df = h.to_dataframe()

    expected_cols = {h.xlabel, h.ylabel, h.ylabel + " error"}
    assert set(df.columns) == expected_cols


def test_to_dataframe_attrs(make_th1):
    """to_dataframe() stores type and all metadata keys in df.attrs."""
    root_hist = make_th1(nbins=10, xmin=0.0, xmax=10.0)
    h = th1(root_hist)
    df = h.to_dataframe()

    assert df.attrs["type"] is th1
    for key in ("entries", "name", "nbins", "title", "xlabel", "ylabel", "sum", "base_class"):
        assert key in df.attrs, f"Missing df.attrs key: {key}"
        assert df.attrs[key] == getattr(h, key)


def test_to_dataframe_values(make_th1):
    """to_dataframe() column values match the th1's x, y, dy arrays."""
    root_hist = make_th1(nbins=10, xmin=0.0, xmax=10.0)
    h = th1(root_hist)
    df = h.to_dataframe()

    np.testing.assert_array_equal(df[h.xlabel].values, h.x)
    np.testing.assert_array_equal(df[h.ylabel].values, h.y)
    np.testing.assert_array_equal(df[h.ylabel + " error"].values, h.dy)


# ---------------------------------------------------------------------------
# Round-trip: th1 -> to_dataframe() -> th1(df)
# ---------------------------------------------------------------------------

def test_round_trip_arrays(make_th1):
    """Round-trip via DataFrame preserves x, y, and dy arrays exactly."""
    root_hist = make_th1(nbins=10, xmin=0.0, xmax=10.0)
    original = th1(root_hist)
    df = original.to_dataframe()
    restored = th1(df)

    np.testing.assert_array_equal(restored.x, original.x)
    np.testing.assert_array_equal(restored.y, original.y)
    np.testing.assert_array_equal(restored.dy, original.dy)


def test_round_trip_metadata(make_th1):
    """Round-trip via DataFrame preserves all scalar metadata fields."""
    root_hist = make_th1(nbins=10, xmin=0.0, xmax=10.0)
    original = th1(root_hist)
    df = original.to_dataframe()
    restored = th1(df)

    assert restored.name == original.name
    assert restored.title == original.title
    assert restored.nbins == original.nbins
    assert restored.entries == original.entries
    assert restored.xlabel == original.xlabel
    assert restored.ylabel == original.ylabel
    assert restored.sum == pytest.approx(original.sum)
    assert restored.base_class == original.base_class


# ---------------------------------------------------------------------------
# plot()
# ---------------------------------------------------------------------------

def test_plot_returns_artist(make_th1):
    """plot(ax=...) returns a non-None artist and draws on the given axes."""
    root_hist = make_th1(nbins=10, xmin=0.0, xmax=10.0)
    h = th1(root_hist)
    fig, ax = plt.subplots()
    line = h.plot(ax=ax)
    assert line is not None
    plt.close(fig)


def test_plot_sets_labels(make_th1):
    """plot() with default data_only=False sets xlabel, ylabel, and title."""
    root_hist = make_th1(nbins=10, xmin=0.0, xmax=10.0)
    h = th1(root_hist)
    fig, ax = plt.subplots()
    h.plot(ax=ax)
    assert ax.get_xlabel() == h.xlabel
    assert ax.get_ylabel() == h.ylabel
    assert ax.get_title() == h.title
    plt.close(fig)


def test_plot_errors_uses_errorbar(make_th1):
    """plot(errors=True) calls errorbar and returns an ErrorbarContainer."""
    import matplotlib.container as mcontainer

    root_hist = make_th1(nbins=10, xmin=0.0, xmax=10.0)
    h = th1(root_hist)
    fig, ax = plt.subplots()
    result = h.plot(ax=ax, errors=True)
    assert isinstance(result, mcontainer.ErrorbarContainer)
    plt.close(fig)


def test_plot_errors_applies_draw_defaults(make_th1):
    """plot(errors=True) applies draw_defaults when keys are absent from kwargs."""
    root_hist = make_th1(nbins=10, xmin=0.0, xmax=10.0)
    h = th1(root_hist)
    fig, ax = plt.subplots()
    # Capture via a wrapper to inspect the kwargs passed to errorbar
    captured = {}
    original_errorbar = ax.errorbar

    def mock_errorbar(*args, **kwargs):
        captured.update(kwargs)
        return original_errorbar(*args, **kwargs)

    ax.errorbar = mock_errorbar
    h.plot(ax=ax, errors=True)

    for key, val in th1.draw_defaults.items():
        assert captured.get(key) == val
    plt.close(fig)


def test_plot_data_only_no_labels(make_th1):
    """plot(data_only=True) does not set axis labels or title."""
    root_hist = make_th1(nbins=10, xmin=0.0, xmax=10.0)
    h = th1(root_hist)
    fig, ax = plt.subplots()
    h.plot(ax=ax, data_only=True)
    assert ax.get_xlabel() == ""
    assert ax.get_ylabel() == ""
    # Matplotlib sets title to "" by default; confirm it was not overwritten
    assert ax.get_title() == ""
    plt.close(fig)


def test_plot_ax_none_uses_gca(make_th1):
    """plot() with ax=None draws on the current axes (plt.gca())."""
    root_hist = make_th1(nbins=10, xmin=0.0, xmax=10.0)
    h = th1(root_hist)
    fig, ax = plt.subplots()
    plt.sca(ax)  # make ax the current axes
    line = h.plot()  # ax=None
    # The line should appear on the current axes
    assert line is not None
    assert ax.lines or ax.containers  # something was drawn
    plt.close(fig)


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------

def test_empty_construction_no_args():
    """th1() with no arguments creates an object with no data attributes set.

    None of the __slots__ are populated; the object can be created but any
    attribute access will raise AttributeError.
    """
    h = th1()
    assert isinstance(h, th1)
    with pytest.raises(AttributeError):
        _ = h.x


def test_empty_construction_hist_none():
    """th1(hist=None) behaves identically to th1() — no slots are populated."""
    h = th1(hist=None)
    assert isinstance(h, th1)
    with pytest.raises(AttributeError):
        _ = h.y


def test_zero_entries_histogram(make_th1):
    """A histogram with no fills: sum==0 and arrays are still length nbins."""
    import ROOT
    nbins = 5
    empty_hist = ROOT.TH1F("empty_h1", "Empty;x axis;y axis", nbins, 0.0, 5.0)
    empty_hist.SetDirectory(0)
    h = th1(empty_hist)

    assert h.entries == 0
    assert h.sum == pytest.approx(0.0)
    assert len(h.x) == nbins
    assert len(h.y) == nbins
    assert len(h.dy) == nbins
    np.testing.assert_array_equal(h.y, np.zeros(nbins))


def test_from_dataframe_missing_attrs_raises():
    """_from_dataframe on a DataFrame without the expected attrs raises an error.

    When df.attrs is empty, xlabel/ylabel are not set before the column lookup,
    so the method raises AttributeError (self.xlabel not set) or KeyError
    (column absent from df).
    """
    df = pd.DataFrame({"a": [1, 2, 3]})
    # df.attrs is empty — the reconstruction cannot proceed
    with pytest.raises((AttributeError, KeyError)):
        th1(df)
