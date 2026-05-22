"""Tests for rootloader.tdirectory.

Covers key dispatching, cycle resolution, empty_ok/quiet flags, key_filter,
tree_filter, unknown class warnings, copy(), to_dataframe(), from_dataframe(),
__repr__, and nested directory handling.
"""

import warnings
from array import array

import numpy as np
import pytest
import ROOT

from rootloader import tdirectory, th1, th2, ttree


# ---------------------------------------------------------------------------
# Basic parsing of the memfile fixture
# ---------------------------------------------------------------------------

def test_parse_memfile_keys(memfile):
    """Parsing a TMemFile yields the correct top-level keys.

    Expected keys: mytree, myhist, myhist2d, subdir.
    """
    fid, *_ = memfile
    d = tdirectory(fid)
    assert set(d.keys()) == {"mytree", "myhist", "myhist2d", "subdir"}


def test_parse_memfile_types(memfile):
    """Each top-level key maps to the correct rootloader wrapper type.

    mytree → ttree, myhist → th1, myhist2d → th2, subdir → tdirectory.
    """
    fid, *_ = memfile
    d = tdirectory(fid)
    assert isinstance(d["mytree"], ttree)
    assert isinstance(d["myhist"], th1)
    assert isinstance(d["myhist2d"], th2)
    assert isinstance(d["subdir"], tdirectory)


def test_keys_accessible_as_attributes(memfile):
    """Keys are reachable as attributes (attrdict behaviour).

    d.mytree and d['mytree'] refer to the same object.
    """
    fid, *_ = memfile
    d = tdirectory(fid)
    assert d.mytree is d["mytree"]
    assert d.myhist is d["myhist"]
    assert d.myhist2d is d["myhist2d"]
    assert d.subdir is d["subdir"]


def test_nested_directory_is_tdirectory(memfile):
    """The nested TDirectoryFile 'subdir' becomes a tdirectory instance.

    Its child 'subhist' should be a th1.
    """
    fid, *_ = memfile
    d = tdirectory(fid)
    sub = d["subdir"]
    assert isinstance(sub, tdirectory)
    assert "subhist" in sub
    assert isinstance(sub["subhist"], th1)


# ---------------------------------------------------------------------------
# Cycle resolution
# ---------------------------------------------------------------------------

def test_cycle_resolution_keeps_highest_cycle():
    """Writing the same key twice keeps only the highest-cycle version.

    ROOT assigns cycle 1 to the first write and cycle 2 to the second.
    tdirectory should expose only the second version (bin 1 content = 99.0).
    """
    f = ROOT.TMemFile("cycle_test", "RECREATE")

    h_v1 = ROOT.TH1F("samename", "v1;x;y", 5, 0, 5)
    h_v1.SetBinContent(1, 1.0)
    h_v1.Write()

    h_v2 = ROOT.TH1F("samename", "v2;x;y", 5, 0, 5)
    h_v2.SetBinContent(1, 99.0)
    h_v2.Write()  # creates cycle 2

    f.Write("", ROOT.TObject.kOverwrite)

    d = tdirectory(f)
    # Only one entry for 'samename', with the cycle-2 content
    assert "samename" in d
    # th1 reads bin 0 (underflow) at index 0, bin 1 at index 1
    assert d["samename"].y[1] == pytest.approx(99.0)

    f.Close()


# ---------------------------------------------------------------------------
# __repr__
# ---------------------------------------------------------------------------

def test_repr_contains_keys(memfile):
    """__repr__ lists the directory's keys in its output grid.

    Relies on patch_terminal_size (autouse) so get_terminal_size doesn't raise.
    """
    fid, *_ = memfile
    d = tdirectory(fid)
    r = repr(d)
    assert "mytree" in r
    assert "myhist" in r
    assert "myhist2d" in r
    assert "subdir" in r


def test_repr_empty_directory():
    """__repr__ of an empty tdirectory (from None) returns 'tdirectory()'."""
    d = tdirectory(None)
    assert repr(d) == "tdirectory()"


# ---------------------------------------------------------------------------
# tdirectory(None)
# ---------------------------------------------------------------------------

def test_none_returns_empty_object():
    """tdirectory(None) returns an empty dict-like object with no keys."""
    d = tdirectory(None)
    assert isinstance(d, tdirectory)
    assert len(d) == 0


# ---------------------------------------------------------------------------
# copy()
# ---------------------------------------------------------------------------

def test_copy_returns_new_instance(memfile):
    """copy() returns a new tdirectory that is not the same object."""
    fid, *_ = memfile
    d = tdirectory(fid)
    c = d.copy()
    assert c is not d


def test_copy_has_same_keys(memfile):
    """copy() preserves all top-level keys from the original."""
    fid, *_ = memfile
    d = tdirectory(fid)
    c = d.copy()
    assert set(c.keys()) == set(d.keys())


def test_copy_deep_copies_histograms(memfile):
    """Mutating a th1 in the copy does not affect the original.

    copy() calls value.copy() for children that support it, so the wrapped
    numpy arrays are independent.
    """
    fid, *_ = memfile
    d = tdirectory(fid)
    c = d.copy()

    original_y0 = d["myhist"].y[1]
    c["myhist"].y[1] = 9999.0
    assert d["myhist"].y[1] == pytest.approx(original_y0)


# ---------------------------------------------------------------------------
# to_dataframe() and from_dataframe()
# ---------------------------------------------------------------------------

def test_to_dataframe_converts_children(memfile, single_mt):
    """to_dataframe() converts each convertible child to a pandas DataFrame.

    single_mt is required because the tree in the TMemFile is evaluated via
    RDataFrame.AsNumpy(); with MT enabled TTreeProcessorMT cannot reopen the
    in-memory file by name.
    """
    import pandas as pd

    fid, *_ = memfile
    d = tdirectory(fid)
    d.to_dataframe()

    assert isinstance(d["myhist"], pd.DataFrame)
    assert isinstance(d["myhist2d"], pd.DataFrame)


def test_from_dataframe_restores_th1_th2(memfile, single_mt):
    """from_dataframe() round-trips th1 and th2 objects via stored attrs['type'].

    After to_dataframe() followed by from_dataframe(), the myhist and myhist2d
    entries should be th1 and th2 instances again.

    single_mt is required so RDataFrame can process the TMemFile-backed tree
    without TTreeProcessorMT trying to open the file from disk.
    """
    fid, *_ = memfile
    d = tdirectory(fid)
    d.to_dataframe()
    d.from_dataframe()

    assert isinstance(d["myhist"], th1)
    assert isinstance(d["myhist2d"], th2)


# ---------------------------------------------------------------------------
# empty_ok=False
# ---------------------------------------------------------------------------

def test_empty_ok_false_skips_empty_histogram():
    """An unfilled histogram is excluded when empty_ok=False.

    An empty TH1F (no fills, sum=0) should not appear in the resulting
    directory, while a filled one should still be present.
    """
    f = ROOT.TMemFile("empty_ok_test", "RECREATE")

    filled = ROOT.TH1F("filled", "filled;x;y", 5, 0, 5)
    filled.SetBinContent(1, 1.0)
    filled.Write()

    empty = ROOT.TH1F("empty", "empty;x;y", 5, 0, 5)
    empty.Write()

    f.Write("", ROOT.TObject.kOverwrite)

    d = tdirectory(f, empty_ok=False)
    assert "filled" in d
    assert "empty" not in d

    f.Close()


def test_empty_ok_false_skips_empty_tree():
    """A TTree with 0 entries is excluded when empty_ok=False."""
    f = ROOT.TMemFile("empty_tree_test", "RECREATE")

    empty_tree = ROOT.TTree("emptytree", "empty tree")
    buf = array("d", [0.0])
    empty_tree.Branch("x", buf, "x/D")
    # deliberately fill nothing
    empty_tree.Write()

    f.Write("", ROOT.TObject.kOverwrite)

    d = tdirectory(f, empty_ok=False)
    assert "emptytree" not in d

    f.Close()


# ---------------------------------------------------------------------------
# quiet=False
# ---------------------------------------------------------------------------

def test_quiet_false_prints_skipped_message(capsys):
    """quiet=False prints a 'Skipped' message for each empty/skipped object.

    tqdm.write goes to stdout; capsys.readouterr() captures it.
    """
    f = ROOT.TMemFile("quiet_test", "RECREATE")

    empty = ROOT.TH1F("quietempty", "empty;x;y", 5, 0, 5)
    empty.Write()

    f.Write("", ROOT.TObject.kOverwrite)

    tdirectory(f, empty_ok=False, quiet=False)
    captured = capsys.readouterr()
    assert "quietempty" in captured.out

    f.Close()


# ---------------------------------------------------------------------------
# key_filter
# ---------------------------------------------------------------------------

def test_key_filter_excludes_rejected_keys(memfile):
    """key_filter excludes keys for which the predicate returns False.

    Filtering out 'myhist' should leave it absent from the directory while
    other keys remain.
    """
    fid, *_ = memfile
    d = tdirectory(fid, key_filter=lambda name: name != "myhist")
    assert "myhist" not in d
    assert "mytree" in d
    assert "myhist2d" in d


def test_key_filter_include_only_one(memfile):
    """key_filter can restrict the directory to a single key."""
    fid, *_ = memfile
    d = tdirectory(fid, key_filter=lambda name: name == "myhist")
    assert list(d.keys()) == ["myhist"]


# ---------------------------------------------------------------------------
# Unknown class warning
# ---------------------------------------------------------------------------

def test_unknown_class_triggers_warning():
    """An unsupported ROOT class triggers a UserWarning via warnings.warn.

    TNamed is not handled by tdirectory and should produce a warning.
    """
    f = ROOT.TMemFile("warn_test", "RECREATE")

    named = ROOT.TNamed("myname", "My Named Object")
    named.Write()

    f.Write("", ROOT.TObject.kOverwrite)

    with pytest.warns(UserWarning, match='Unknown class'):
        tdirectory(f)

    f.Close()


# ---------------------------------------------------------------------------
# tree_filter
# ---------------------------------------------------------------------------

def test_tree_filter_applies_filter_and_columns(memfile, single_mt):
    """tree_filter builds the named tree with filter and column subset applied.

    Filtering 'mytree' to rows where x > 25 should reduce the entry count,
    and only the requested columns should be present.

    single_mt is required because the filtered RDataFrame is evaluated via
    to_dataframe() on a TMemFile-backed tree.
    """
    fid, *_ = memfile
    d = tdirectory(fid, tree_filter={"mytree": ("x > 25", ["x", "y"])})

    tree = d["mytree"]
    assert isinstance(tree, ttree)

    # After filtering x > 25 from 0..49 we expect 24 rows (26..49)
    df = tree.to_dataframe()
    assert len(df) == 24

    # Only the requested columns plus possibly the index; at minimum x and y present
    assert "x" in df.columns
    assert "y" in df.columns
    # tEntry was not requested so should not be in the filtered column set
    assert "tEntry" not in df.columns


def test_tree_filter_unknown_treename_ignored(memfile, single_mt):
    """A treename in tree_filter that doesn't exist in the file is silently ignored.

    The directory should still load normally with no errors.

    single_mt is required because to_dataframe() evaluates the TMemFile tree.
    """
    fid, *_ = memfile
    d = tdirectory(fid, tree_filter={"nonexistent_tree": ("x > 0", ["x"])})
    # The real tree is loaded without any filter
    assert isinstance(d["mytree"], ttree)
    df = d["mytree"].to_dataframe()
    assert len(df) == 50
