"""Tests for rootloader.tleaf."""

from array import array

import numpy as np
import pytest
import ROOT

from rootloader import tleaf


# ---------------------------------------------------------------------------
# Scalar leaf — properties and value
# ---------------------------------------------------------------------------

def test_scalar_leaf_properties(make_tree):
    """Properties name, branch, fullname, leaftype, and len are correct for a scalar double leaf.

    A double branch produces ClassName() == 'TLeafD', so leaftype should be 'd'
    and len should be 1.
    """
    tree = make_tree({"col": np.array([1.0, 2.0, 3.0])})
    tree.GetEntry(0)
    root_leaf = tree.GetLeaf("col")
    leaf = tleaf(root_leaf)

    assert leaf.name == "col"
    assert leaf.branch == "col"
    # fullname is returned by ROOT.TLeaf.GetFullName(); should contain the column name
    assert "col" in str(leaf.fullname)
    assert leaf.leaftype == "d"  # TLeafD → last char 'd'
    assert leaf.len == 1


def test_scalar_leaf_value_is_float(make_tree):
    """value returns a plain Python float for a length-1 (scalar) leaf."""
    tree = make_tree({"col": np.array([42.0])})
    tree.GetEntry(0)
    root_leaf = tree.GetLeaf("col")
    leaf = tleaf(root_leaf)

    val = leaf.value
    assert isinstance(val, float)
    assert val == pytest.approx(42.0)


# ---------------------------------------------------------------------------
# get_entry — per-row access
# ---------------------------------------------------------------------------

def test_get_entry_returns_correct_values(make_tree):
    """get_entry(i) loads row i from the tree and returns its value.

    Each entry is verified against the original data array.
    """
    data = np.array([10.0, 20.0, 30.0])
    tree = make_tree({"col": data})
    root_leaf = tree.GetLeaf("col")
    leaf = tleaf(root_leaf)

    for i, expected in enumerate(data):
        val = leaf.get_entry(i)
        assert val == pytest.approx(expected), f"row {i}: expected {expected}, got {val}"


# ---------------------------------------------------------------------------
# Array leaf — multi-element value
# ---------------------------------------------------------------------------

def test_array_leaf_value_returns_numpy_array():
    """value returns a numpy array for a fixed-size array branch (len > 1).

    The array branch 'arr[3]/D' should yield GetLen() == 3, leaftype == 'd',
    and value == np.array([1.0, 2.0, 3.0]).
    """
    # Build a plain TTree with a fixed-size array branch; not via make_tree
    # because make_tree only handles scalar columns.
    tree = ROOT.TTree("arr_tree", "arr_tree")
    buf = array("d", [0.0, 0.0, 0.0])
    tree.Branch("arr", buf, "arr[3]/D")

    buf[0] = 1.0
    buf[1] = 2.0
    buf[2] = 3.0
    tree.Fill()

    # Load entry 0 so the branch buffer is populated
    tree.GetEntry(0)
    root_leaf = tree.GetLeaf("arr")
    leaf = tleaf(root_leaf)

    assert leaf.len == 3
    assert leaf.leaftype == "d"

    val = leaf.value
    assert isinstance(val, np.ndarray)
    assert val.dtype == np.dtype("d")
    np.testing.assert_array_almost_equal(val, np.array([1.0, 2.0, 3.0]))

    # Keep tree and buf alive until assertions complete
    _ = tree
    _ = buf


# ---------------------------------------------------------------------------
# copy
# ---------------------------------------------------------------------------

def test_copy_wraps_same_underlying_leaf(make_tree):
    """copy() returns a new tleaf instance wrapping the same ROOT leaf.

    name, branch, leaftype, and len should match the original.
    """
    tree = make_tree({"col": np.array([5.0, 6.0])})
    tree.GetEntry(0)
    root_leaf = tree.GetLeaf("col")
    leaf = tleaf(root_leaf)

    copied = leaf.copy()

    assert isinstance(copied, tleaf)
    assert copied is not leaf                      # distinct Python wrapper
    assert copied.name == leaf.name
    assert copied.branch == leaf.branch
    assert copied.leaftype == leaf.leaftype
    assert copied.len == leaf.len
    # Both wrappers point to the same underlying ROOT leaf
    assert copied._leaf is leaf._leaf
