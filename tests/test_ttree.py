"""Tests for rootloader.ttree.

Covers construction, column access and views, data conversion, statistics,
histogramming, filter/mutation operations, and .loc indexing.

Row-order note: RDataFrame.AsNumpy() does not guarantee row order when
ROOT implicit multithreading is active. All tests that compare exact array
values use the `single_mt` fixture to disable MT for that test.
"""

import numpy as np
import pandas as pd
import pytest
import ROOT

from rootloader import ttree, th1, th2

# All tests in this module evaluate RDataFrame lazy operations on in-memory
# trees (created by make_tree) or TMemFile-backed trees.  With implicit
# multithreading enabled, TTreeProcessorMT can't access in-memory trees and
# fails with "not linked to any file" or "error opening file".  Applying
# single_mt (DisableImplicitMT) module-wide fixes this without affecting
# tests that independently request it.
pytestmark = pytest.mark.usefixtures("single_mt")


# ---------------------------------------------------------------------------
# Construction & identity
# ---------------------------------------------------------------------------

def test_init_from_root_ttree(make_tree):
    """ttree constructed from ROOT.TTree has correct columns, size, and name.

    Verifies that the column tuple contains all branch names, that size
    matches the number of rows, and that name matches the TTree name.
    """
    data = {"x": np.arange(10, dtype=float), "n": np.arange(10, dtype=int)}
    root_tree = make_tree(data, name="mytree")
    tr = ttree(root_tree)

    assert tr.name == "mytree"
    assert tr.size == 10
    assert "x" in tr.columns
    assert "n" in tr.columns


def test_init_copy_from_ttree(make_tree):
    """Copying a ttree gives an independent filter list.

    Modifying the copy's filters must not affect the original.
    """
    root_tree = make_tree({"x": np.arange(5, dtype=float)})
    original = ttree(root_tree)
    copy = ttree(original)

    # Mutate the copy's filter list directly to verify independence.
    copy._filters.append("sentinel")
    assert "sentinel" not in original._filters


def test_init_from_none():
    """Constructing a ttree from None produces a stub with name=None.

    This is the internal pattern used by __getitem__ to create column views
    without allocating a new RDataFrame.
    """
    stub = ttree(None)
    assert stub.name is None


def test_init_invalid_type_raises():
    """Passing an unsupported type raises RuntimeError.

    The error message should identify the offending type.
    """
    with pytest.raises(RuntimeError):
        ttree(42)


# --- index auto-detection ---

def test_index_autodetect_tUnixTimePrecise(make_tree):
    """tUnixTimePrecise is chosen as the index when present.

    Takes highest priority over timestamp and tEntry.
    """
    data = {
        "tUnixTimePrecise": np.arange(5, dtype=float),
        "timestamp": np.arange(5, dtype=float),
        "tEntry": np.arange(5, dtype=float),
        "x": np.arange(5, dtype=float),
    }
    tr = ttree(make_tree(data))
    assert tr.index_name == "tUnixTimePrecise"


def test_index_autodetect_timestamp(make_tree):
    """timestamp is chosen as the index when tUnixTimePrecise is absent."""
    data = {
        "timestamp": np.arange(5, dtype=float),
        "tEntry": np.arange(5, dtype=float),
        "x": np.arange(5, dtype=float),
    }
    tr = ttree(make_tree(data))
    assert tr.index_name == "timestamp"


def test_index_autodetect_tEntry(make_tree):
    """tEntry is chosen as the index when neither tUnixTimePrecise nor timestamp is present."""
    data = {
        "tEntry": np.arange(5, dtype=float),
        "x": np.arange(5, dtype=float),
    }
    tr = ttree(make_tree(data))
    assert tr.index_name == "tEntry"


def test_index_autodetect_none(make_tree):
    """index_name is None when no recognized timestamp column exists."""
    data = {"x": np.arange(5, dtype=float)}
    tr = ttree(make_tree(data))
    assert tr.index_name is None


# ---------------------------------------------------------------------------
# Access & views
# ---------------------------------------------------------------------------

def test_getitem_string_returns_single_column_view(make_tree):
    """__getitem__ with a string returns a one-column ttree view.

    The view has exactly one column and shares the same underlying _rdf.
    """
    root_tree = make_tree({"x": np.arange(5, dtype=float), "y": np.arange(5, dtype=float)})
    tr = ttree(root_tree)
    view = tr["x"]

    assert view.columns == ("x",)
    assert view._rdf is tr._rdf


def test_getitem_list_returns_multi_column_view(make_tree):
    """__getitem__ with a list returns a view containing exactly those columns."""
    root_tree = make_tree({
        "x": np.arange(5, dtype=float),
        "y": np.arange(5, dtype=float),
        "z": np.arange(5, dtype=float),
    })
    tr = ttree(root_tree)
    view = tr[["x", "z"]]

    assert set(view.columns) == {"x", "z"}


def test_getitem_does_not_mutate_parent(make_tree):
    """Column selection via __getitem__ does not change the parent's columns."""
    root_tree = make_tree({"x": np.arange(5, dtype=float), "y": np.arange(5, dtype=float)})
    tr = ttree(root_tree)
    original_columns = set(tr.columns)

    _ = tr["x"]

    assert set(tr.columns) == original_columns


def test_getattr_returns_column_view(make_tree):
    """Attribute access for a known column returns a one-column ttree."""
    root_tree = make_tree({"myvar": np.arange(5, dtype=float)})
    tr = ttree(root_tree)
    view = tr.myvar

    assert isinstance(view, ttree)
    assert view.columns == ("myvar",)


def test_dir_lists_sorted_column_names(make_tree):
    """__dir__ includes all branch names in sorted order."""
    root_tree = make_tree({"b": np.arange(3, dtype=float), "a": np.arange(3, dtype=float)})
    tr = ttree(root_tree)
    d = dir(tr)

    col_idx_a = d.index("a")
    col_idx_b = d.index("b")
    assert col_idx_a < col_idx_b


def test_len_equals_size(make_tree):
    """len(tr) and tr.size both return the row count."""
    root_tree = make_tree({"x": np.arange(7, dtype=float)})
    tr = ttree(root_tree)

    assert len(tr) == 7
    assert tr.size == 7
    assert tr.size == tr._rdf.Count().GetValue()


def test_repr_contains_branch_names(make_tree):
    """__repr__ includes branch names in its output."""
    root_tree = make_tree({"alpha": np.arange(3, dtype=float), "beta": np.arange(3, dtype=float)})
    tr = ttree(root_tree)
    r = repr(tr)

    assert "alpha" in r
    assert "beta" in r


def test_getattr_missing_column_raises(make_tree):
    """Accessing a non-existent attribute raises AttributeError.

    __getattr__ falls through to getattr(object, name) for unknown names,
    which raises AttributeError.
    """
    root_tree = make_tree({"x": np.arange(3, dtype=float)})
    tr = ttree(root_tree)

    with pytest.raises(AttributeError):
        _ = tr.nonexistent_column_name


# ---------------------------------------------------------------------------
# Conversion (single_mt required for exact-value checks)
# ---------------------------------------------------------------------------

def test_to_dict_returns_numpy_arrays(make_tree, single_mt):
    """to_dict() returns a dict mapping column names to numpy arrays."""
    root_tree = make_tree({"x": np.arange(5, dtype=float)})
    tr = ttree(root_tree)
    result = tr.to_dict()

    assert isinstance(result, dict)
    for val in result.values():
        assert isinstance(val, np.ndarray)

def test_to_array_1d_for_single_column(make_tree, single_mt):
    """to_array() returns a 1D array when the tree view has one column."""
    values = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
    root_tree = make_tree({"x": values})
    tr = ttree(root_tree)["x"]
    result = tr.to_array()

    assert result.ndim == 1
    np.testing.assert_array_equal(np.sort(result), np.sort(values))


def test_to_array_2d_for_multiple_columns(make_tree, single_mt):
    """to_array() returns a 2D array when the tree view has multiple columns."""
    root_tree = make_tree({
        "x": np.arange(4, dtype=float),
        "y": np.arange(4, dtype=float),
    })
    # Select only non-index columns so both are stacked
    tr = ttree(root_tree)[["x", "y"]]
    result = tr.to_array()

    assert result.ndim == 2
    assert result.shape[0] == 2


def test_to_dataframe_multi_column_returns_dataframe(make_tree, single_mt):
    """to_dataframe() returns a DataFrame (with index set) for 2+ non-index columns."""
    data = {
        "tEntry": np.arange(6, dtype=float),
        "x": np.arange(6, dtype=float),
        "y": np.arange(6, dtype=float),
    }
    root_tree = make_tree(data)
    tr = ttree(root_tree)
    result = tr.to_dataframe()

    assert isinstance(result, pd.DataFrame)
    assert result.index.name == "tEntry"
    assert "x" in result.columns
    assert "y" in result.columns


def test_to_dataframe_single_non_index_column_returns_series(make_tree, single_mt):
    """to_dataframe() returns a pd.Series when one non-index column is selected.

    Per the implementation: when len(df.columns)==1 after set_index, the
    single remaining column is returned as a Series.
    """
    data = {"tEntry": np.arange(5, dtype=float), "x": np.arange(5, dtype=float)}
    root_tree = make_tree(data)
    tr = ttree(root_tree)["x"]
    result = tr.to_dataframe()

    assert isinstance(result, pd.Series)


def test_values_property_mirrors_to_array(make_tree, single_mt):
    """The .values property returns the same result as to_array()."""
    root_tree = make_tree({"x": np.array([3.0, 1.0, 4.0, 1.0, 5.0])})
    tr = ttree(root_tree)["x"]

    np.testing.assert_array_equal(tr.values, tr.to_array())


# ---------------------------------------------------------------------------
# Statistics
# ---------------------------------------------------------------------------

def test_stats_scalar_single_column_float(make_tree):
    """min/max/mean/sum/std return scalars for a single float column.

    Results are verified against numpy equivalents.
    """
    values = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
    root_tree = make_tree({"x": values})
    tr = ttree(root_tree)["x"]

    assert tr.min() == pytest.approx(values.min())
    assert tr.max() == pytest.approx(values.max())
    assert tr.mean() == pytest.approx(values.mean())
    assert tr.sum() == pytest.approx(values.sum())
    # ROOT RDataFrame.StdDev uses the sample std dev (N-1 denominator);
    # numpy's std() defaults to population std dev (N).  Use ddof=1 to match.
    assert tr.std() == pytest.approx(values.std(ddof=1), rel=1e-5)


def test_stats_scalar_single_column_int(make_tree):
    """min/max/mean/sum/std return scalars for a single int column."""
    values = np.array([10, 20, 30, 40, 50], dtype=int)
    root_tree = make_tree({"n": values})
    tr = ttree(root_tree)["n"]

    assert tr.min() == pytest.approx(int(values.min()))
    assert tr.max() == pytest.approx(int(values.max()))
    assert tr.sum() == pytest.approx(int(values.sum()))


def test_stats_series_multi_column(make_tree):
    """min/max/mean/sum/std return pd.Series for multi-column trees.

    The Series index must match the column names.
    """
    root_tree = make_tree({
        "x": np.array([1.0, 2.0, 3.0]),
        "y": np.array([4.0, 5.0, 6.0]),
    })
    tr = ttree(root_tree)[["x", "y"]]
    result = tr.min()

    assert isinstance(result, pd.Series)
    assert set(result.index) == {"x", "y"}


def test_stats_jit_cache_no_error_on_second_call(make_tree):
    """Calling a stat method twice must not raise; JIT cache is reused.

    After the first call, the compiled C++ function is attached to the ROOT
    module, so the second call must find it via hasattr(ROOT, fn_name).
    """
    values = np.array([1.0, 2.0, 3.0])
    root_tree = make_tree({"x": values})
    tr = ttree(root_tree)["x"]

    first = tr.min()
    second = tr.min()
    assert first == pytest.approx(second)


def test_stats_jit_function_cached_on_root_module(make_tree):
    """After the first stat call, the JIT function exists on the ROOT module.

    Verifies that the caching mechanism attaches the compiled function as
    an attribute of ROOT (e.g. ROOT.RDF_Min_double).
    """
    root_tree = make_tree({"x": np.array([1.0, 2.0, 3.0])})
    tr = ttree(root_tree)["x"]
    tr.min()

    dtype = tr._rdf.GetColumnType("x")  # e.g. "double"
    fn_name = f"RDF_Min_{dtype}"
    assert hasattr(ROOT, fn_name)


def test_stats_zero_row_tree(make_tree):
    """Stats on an empty (zero-row) tree: document the behavior.

    Calling min/max/mean/sum on an empty tree should not raise a Python
    exception; ROOT returns a default value (typically 0 for sum, or
    implementation-defined for min/max/mean).
    """
    root_tree = make_tree({"x": np.array([1.0, 2.0, 3.0])})
    tr = ttree(root_tree)["x"]
    # Filter to produce zero rows.
    tr_empty = tr.set_filter("x > 1000.0")

    # Should not raise; actual return value is implementation-defined.
    _ = tr_empty.sum()
    _ = tr_empty.min()


# ---------------------------------------------------------------------------
# Histogramming
# ---------------------------------------------------------------------------

def test_hist1d_nbins(make_tree):
    """hist1d(nbins=N) returns a th1 with N bins."""
    root_tree = make_tree({"x": np.linspace(0.0, 10.0, 50)})
    tr = ttree(root_tree)["x"]
    h = tr.hist1d(nbins=10)

    assert isinstance(h, th1)
    assert h.nbins == 10


def test_hist1d_step(make_tree):
    """hist1d(step=...) returns a th1 with the expected bin count.

    With data in [0, 10) and step=2, ceil((10-0)/2)=5 bins expected.
    """
    root_tree = make_tree({"x": np.linspace(0.0, 9.9, 100)})
    tr = ttree(root_tree)["x"]
    h = tr.hist1d(step=2.0)

    assert isinstance(h, th1)
    assert h.nbins == 5


def test_hist1d_edges(make_tree):
    """hist1d(edges=array) returns a th1 with len(edges)-1 bins."""
    edges = np.array([0.0, 2.0, 5.0, 10.0])
    root_tree = make_tree({"x": np.linspace(0.0, 9.9, 30)})
    tr = ttree(root_tree)["x"]
    h = tr.hist1d(edges=edges)

    assert isinstance(h, th1)
    assert h.nbins == len(edges) - 1


def test_hist1d_auto_selects_column(make_tree):
    """hist1d() without specifying column works when tree has exactly one column."""
    root_tree = make_tree({"x": np.linspace(0.0, 5.0, 20)})
    tr = ttree(root_tree)["x"]
    h = tr.hist1d(nbins=5)

    assert isinstance(h, th1)


def test_hist2d_nbins(make_tree):
    """hist2d(nxbins=, nybins=) returns a th2 with the specified bin counts."""
    root_tree = make_tree({
        "x": np.linspace(0.0, 10.0, 50),
        "y": np.linspace(0.0, 5.0, 50),
    })
    tr = ttree(root_tree)[["x", "y"]]
    h = tr.hist2d(nxbins=10, nybins=5)

    assert isinstance(h, th2)
    assert h.nbinsx == 10
    assert h.nbinsy == 5


def test_hist2d_step(make_tree):
    """hist2d(xstep=, ystep=) returns a th2 with computed bin counts."""
    root_tree = make_tree({
        "x": np.linspace(0.0, 9.9, 50),
        "y": np.linspace(0.0, 4.9, 50),
    })
    tr = ttree(root_tree)[["x", "y"]]
    h = tr.hist2d(xstep=2.0, ystep=1.0)

    assert isinstance(h, th2)


def test_hist1d_no_binning_raises(make_tree):
    """hist1d() with no binning argument raises RuntimeError."""
    root_tree = make_tree({"x": np.arange(5, dtype=float)})
    tr = ttree(root_tree)["x"]

    with pytest.raises(RuntimeError):
        tr.hist1d()


def test_hist1d_multiple_binning_args_raises(make_tree):
    """hist1d() with more than one binning argument raises RuntimeError."""
    root_tree = make_tree({"x": np.arange(5, dtype=float)})
    tr = ttree(root_tree)["x"]

    with pytest.raises(RuntimeError):
        tr.hist1d(nbins=5, step=1.0)


def test_hist1d_multi_column_no_column_arg_raises(make_tree):
    """hist1d() on a multi-column view without specifying column raises KeyError."""
    root_tree = make_tree({
        "x": np.arange(5, dtype=float),
        "y": np.arange(5, dtype=float),
    })
    tr = ttree(root_tree)[["x", "y"]]

    with pytest.raises(KeyError):
        tr.hist1d(nbins=5)


def test_hist1d_unknown_column_raises(make_tree):
    """hist1d(column=<unknown>) raises KeyError."""
    root_tree = make_tree({"x": np.arange(5, dtype=float)})
    tr = ttree(root_tree)["x"]

    with pytest.raises(KeyError):
        tr.hist1d(column="nonexistent", nbins=5)


def test_hist2d_too_few_columns_raises(make_tree):
    """hist2d() on a single-column view without explicit column args raises KeyError."""
    root_tree = make_tree({"x": np.arange(5, dtype=float)})
    tr = ttree(root_tree)["x"]

    with pytest.raises(KeyError):
        tr.hist2d(nxbins=5, nybins=5)


def test_hist2d_too_many_columns_raises(make_tree):
    """hist2d() on a 3-column view without explicit column args raises KeyError."""
    root_tree = make_tree({
        "x": np.arange(5, dtype=float),
        "y": np.arange(5, dtype=float),
        "z": np.arange(5, dtype=float),
    })
    tr = ttree(root_tree)[["x", "y", "z"]]

    with pytest.raises(KeyError):
        tr.hist2d(nxbins=5, nybins=5)


def test_hist2d_both_xbins_and_xstep_raises(make_tree):
    """hist2d() with both nxbins and xstep raises RuntimeError."""
    root_tree = make_tree({
        "x": np.arange(5, dtype=float),
        "y": np.arange(5, dtype=float),
    })
    tr = ttree(root_tree)[["x", "y"]]

    with pytest.raises(RuntimeError):
        tr.hist2d(nxbins=5, xstep=1.0, nybins=5)


# ---------------------------------------------------------------------------
# Filters & mutation
# ---------------------------------------------------------------------------

def test_set_filter_not_inplace_returns_new_tree(make_tree):
    """set_filter() without inplace=True returns a new filtered tree.

    The original tree must remain unchanged.
    """
    data = {"x": np.arange(10, dtype=float)}
    root_tree = make_tree(data)
    tr = ttree(root_tree)["x"]
    original_size = tr.size

    filtered = tr.set_filter("x > 4.5")

    assert filtered.size < original_size
    assert tr.size == original_size  # original unchanged


def test_set_filter_inplace_reduces_size(make_tree):
    """set_filter(expr, inplace=True) shrinks the tree in place."""
    data = {"x": np.arange(10, dtype=float)}
    root_tree = make_tree(data)
    tr = ttree(root_tree)["x"]

    tr.set_filter("x > 4.5", inplace=True)

    assert tr.size == 5


def test_set_filter_inplace_appends_to_filters(make_tree):
    """set_filter(expr, inplace=True) appends the expression to .filters."""
    root_tree = make_tree({"x": np.arange(10, dtype=float)})
    tr = ttree(root_tree)["x"]

    tr.set_filter("x > 2.5", inplace=True)

    assert "x > 2.5" in tr.filters


def test_filters_property_reflects_applied_filters(make_tree):
    """The .filters property lists all applied filter expressions."""
    root_tree = make_tree({"x": np.arange(20, dtype=float)})
    tr = ttree(root_tree)["x"]

    tr.set_filter("x > 5.0", inplace=True)
    tr.set_filter("x < 15.0", inplace=True)

    assert "x > 5.0" in tr.filters
    assert "x < 15.0" in tr.filters
    assert len(tr.filters) == 2


def test_reset_returns_full_tree(make_tree):
    """reset() returns a fresh ttree with no filters, restoring full row count."""
    root_tree = make_tree({"x": np.arange(10, dtype=float)})
    tr = ttree(root_tree)
    full_size = tr.size

    tr.set_filter("x > 7.5", inplace=True)
    assert tr.size < full_size

    fresh = tr.reset()
    assert fresh.size == full_size
    assert fresh.filters == []


def test_reset_columns_restores_all_columns(make_tree):
    """reset_columns() restores all RDataFrame columns after manual restriction."""
    root_tree = make_tree({"x": np.arange(5, dtype=float), "y": np.arange(5, dtype=float)})
    tr = ttree(root_tree)
    all_cols = set(tr.columns)

    # Manually restrict columns to one.
    tr._columns = ("x",)
    assert set(tr.columns) == {"x"}

    tr.reset_columns()
    assert set(tr.columns) == all_cols


def test_set_index_changes_index_name(make_tree):
    """set_index(col) updates index_name to the given column."""
    root_tree = make_tree({"x": np.arange(5, dtype=float), "y": np.arange(5, dtype=float)})
    tr = ttree(root_tree)

    tr.set_index("x")
    assert tr.index_name == "x"


def test_set_index_unknown_column_raises(make_tree):
    """set_index() with a column not in the tree raises KeyError."""
    root_tree = make_tree({"x": np.arange(5, dtype=float)})
    tr = ttree(root_tree)

    with pytest.raises(KeyError):
        tr.set_index("nonexistent")


def test_index_property_returns_view(make_tree):
    """The .index property returns a one-column ttree view of the index column."""
    data = {"tEntry": np.arange(5, dtype=float), "x": np.arange(5, dtype=float)}
    root_tree = make_tree(data)
    tr = ttree(root_tree)

    idx = tr.index
    assert isinstance(idx, ttree)
    assert idx.columns == ("tEntry",)


def test_index_name_property(make_tree):
    """index_name property returns the string name of the current index column."""
    data = {"tEntry": np.arange(5, dtype=float), "x": np.arange(5, dtype=float)}
    root_tree = make_tree(data)
    tr = ttree(root_tree)

    assert tr.index_name == "tEntry"


# ---------------------------------------------------------------------------
# .loc indexing
# ---------------------------------------------------------------------------

def test_loc_slice_reduces_size(make_tree):
    """tr.loc[start:stop] applies >= and < filters and reduces the row count.

    tEntry is included so the auto-detected index is 'tEntry' (not None).
    With tEntry in [0, 10), loc[3:7] selects rows where 3 <= tEntry < 7 (4 rows).
    """
    root_tree = make_tree({"tEntry": np.arange(10, dtype=float),
                           "x": np.arange(10, dtype=float)})
    tr = ttree(root_tree)

    sliced = tr.loc[3.0:7.0]
    assert sliced.size == 4


def test_loc_slice_start_only(make_tree):
    """tr.loc[start:] applies only the >= filter.

    tEntry column ensures a valid index for loc operations.
    """
    root_tree = make_tree({"tEntry": np.arange(10, dtype=float),
                           "x": np.arange(10, dtype=float)})
    tr = ttree(root_tree)

    sliced = tr.loc[5.0:]
    assert sliced.size == 5


def test_loc_slice_stop_only(make_tree):
    """tr.loc[:stop] applies only the < filter.

    tEntry column ensures a valid index for loc operations.
    """
    root_tree = make_tree({"tEntry": np.arange(10, dtype=float),
                           "x": np.arange(10, dtype=float)})
    tr = ttree(root_tree)

    sliced = tr.loc[:5.0]
    assert sliced.size == 5


def test_loc_step_raises(make_tree):
    """tr.loc[::step] raises NotImplementedError.

    Slicing steps are not supported by the _ttree_indexed implementation.
    tEntry column ensures a valid index; the error fires before any evaluation.
    """
    root_tree = make_tree({"tEntry": np.arange(10, dtype=float),
                           "x": np.arange(10, dtype=float)})
    tr = ttree(root_tree)

    with pytest.raises(NotImplementedError):
        _ = tr.loc[::2]


def test_loc_scalar_applies_equality_filter(make_tree):
    """tr.loc[val] applies an == filter and returns matching rows only.

    tEntry column is used as the index; two rows share tEntry==2.
    """
    root_tree = make_tree({"tEntry": np.array([1.0, 2.0, 3.0, 2.0, 1.0]),
                           "x":      np.array([10., 20., 30., 20., 10.])})
    tr = ttree(root_tree)

    selected = tr.loc[2.0]
    assert selected.size == 2
