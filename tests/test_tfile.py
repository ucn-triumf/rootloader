"""Tests for rootloader.tfile.

Covers opening a real ROOT file, key type resolution, tfile(None) sentinel,
as_dataframe conversion, copy(), key_filter/empty_ok forwarding, and expected
IOError cases for bad paths.
"""

import pandas as pd
import pytest

from rootloader import tfile, tdirectory, ttree, th1, th2


# ---------------------------------------------------------------------------
# Opening a real .root file
# ---------------------------------------------------------------------------

def test_open_real_file_returns_tfile(root_file_path):
    """Opening a valid .root file returns a tfile instance.

    Args:
        root_file_path: Path to the pre-built test ROOT file.
    """
    fid = tfile(root_file_path)
    assert isinstance(fid, tfile)


def test_open_real_file_expected_keys(root_file_path):
    """All top-level keys from the ROOT file are present after loading.

    Expected keys: mytree, myhist, myhist2d, subdir.

    Args:
        root_file_path: Path to the pre-built test ROOT file.
    """
    fid = tfile(root_file_path)
    assert "mytree" in fid
    assert "myhist" in fid
    assert "myhist2d" in fid
    assert "subdir" in fid


def test_item_and_attribute_access_equivalent(root_file_path):
    """Item access and attribute access return the same object.

    tfile inherits from attrdict, so fid["myhist"] and fid.myhist must be
    the identical object.

    Args:
        root_file_path: Path to the pre-built test ROOT file.
    """
    fid = tfile(root_file_path)
    assert fid["myhist"] is fid.myhist


# ---------------------------------------------------------------------------
# Key type resolution
# ---------------------------------------------------------------------------

def test_mytree_wraps_as_ttree(root_file_path):
    """A TTree in the ROOT file is mapped to a ttree wrapper.

    Args:
        root_file_path: Path to the pre-built test ROOT file.
    """
    fid = tfile(root_file_path)
    assert isinstance(fid["mytree"], ttree)


def test_myhist_wraps_as_th1(root_file_path):
    """A TH1F in the ROOT file is mapped to a th1 wrapper.

    Args:
        root_file_path: Path to the pre-built test ROOT file.
    """
    fid = tfile(root_file_path)
    assert isinstance(fid["myhist"], th1)


def test_myhist2d_wraps_as_th2(root_file_path):
    """A TH2F in the ROOT file is mapped to a th2 wrapper.

    Args:
        root_file_path: Path to the pre-built test ROOT file.
    """
    fid = tfile(root_file_path)
    assert isinstance(fid["myhist2d"], th2)


def test_subdir_wraps_as_tdirectory(root_file_path):
    """A nested TDirectoryFile is mapped to a tdirectory wrapper.

    Args:
        root_file_path: Path to the pre-built test ROOT file.
    """
    fid = tfile(root_file_path)
    assert isinstance(fid["subdir"], tdirectory)


def test_subdir_contains_subhist(root_file_path):
    """The nested subdir contains the expected subhist key mapped to th1.

    Args:
        root_file_path: Path to the pre-built test ROOT file.
    """
    fid = tfile(root_file_path)
    assert "subhist" in fid["subdir"]
    assert isinstance(fid["subdir"]["subhist"], th1)


# ---------------------------------------------------------------------------
# tfile(None) sentinel
# ---------------------------------------------------------------------------

def test_none_returns_empty_tfile():
    """tfile(None) returns an empty tfile without raising.

    The result must be a tfile (and therefore also a tdirectory), but must
    contain no keys.
    """
    fid = tfile(None)
    assert isinstance(fid, tfile)
    assert isinstance(fid, tdirectory)
    assert len(fid) == 0


# ---------------------------------------------------------------------------
# as_dataframe=True
# ---------------------------------------------------------------------------

def test_as_dataframe_converts_th1(root_file_path):
    """Opening with as_dataframe=True converts th1 contents to DataFrames.

    After loading, myhist should be a pd.DataFrame, not a th1.

    Args:
        root_file_path: Path to the pre-built test ROOT file.
    """
    fid = tfile(root_file_path, as_dataframe=True)
    assert isinstance(fid["myhist"], pd.DataFrame)


def test_as_dataframe_converts_th2(root_file_path):
    """Opening with as_dataframe=True converts th2 contents to DataFrames.

    Args:
        root_file_path: Path to the pre-built test ROOT file.
    """
    fid = tfile(root_file_path, as_dataframe=True)
    assert isinstance(fid["myhist2d"], pd.DataFrame)


def test_as_dataframe_converts_ttree(root_file_path):
    """Opening with as_dataframe=True converts ttree contents to DataFrames.

    Args:
        root_file_path: Path to the pre-built test ROOT file.
    """
    fid = tfile(root_file_path, as_dataframe=True)
    assert isinstance(fid["mytree"], pd.DataFrame)


# ---------------------------------------------------------------------------
# copy()
# ---------------------------------------------------------------------------

def test_copy_returns_tfile_instance(root_file_path):
    """copy() returns a tfile instance, not a plain tdirectory.

    Args:
        root_file_path: Path to the pre-built test ROOT file.
    """
    fid = tfile(root_file_path)
    copied = fid.copy()
    assert isinstance(copied, tfile)


def test_copy_has_same_keys(root_file_path):
    """copy() produces an object with the same top-level keys as the original.

    Args:
        root_file_path: Path to the pre-built test ROOT file.
    """
    fid = tfile(root_file_path)
    copied = fid.copy()
    assert set(copied.keys()) == set(fid.keys())


def test_copy_is_independent(root_file_path):
    """Mutating a value in the copy does not affect the original.

    Replaces a key in the copy with a sentinel and checks the original still
    holds the original wrapper type.

    Args:
        root_file_path: Path to the pre-built test ROOT file.
    """
    fid = tfile(root_file_path)
    copied = fid.copy()

    # Overwrite the copy's myhist with a sentinel value
    copied["myhist"] = "mutated"

    # Original must still have the th1 wrapper
    assert isinstance(fid["myhist"], th1)


# ---------------------------------------------------------------------------
# key_filter forwarding
# ---------------------------------------------------------------------------

def test_key_filter_limits_loaded_keys(root_file_path):
    """key_filter loads only keys accepted by the filter function.

    Passing key_filter=lambda k: k == "myhist" should result in only myhist
    being present in the loaded tfile.

    Args:
        root_file_path: Path to the pre-built test ROOT file.
    """
    fid = tfile(root_file_path, key_filter=lambda k: k == "myhist")
    # tfile stores self._fid via attrdict.__setattr__ = dict.__setitem__, so
    # '_fid' appears in the dict.  Filter to public (non-underscore) keys.
    public_keys = [k for k in fid.keys() if not str(k).startswith("_")]
    assert public_keys == ["myhist"]


def test_key_filter_excluded_keys_absent(root_file_path):
    """Keys rejected by key_filter are not present in the tfile.

    Args:
        root_file_path: Path to the pre-built test ROOT file.
    """
    fid = tfile(root_file_path, key_filter=lambda k: k != "mytree")
    assert "mytree" not in fid
    assert "myhist" in fid


# ---------------------------------------------------------------------------
# empty_ok forwarding
# ---------------------------------------------------------------------------

def test_empty_ok_true_loads_all_objects(root_file_path):
    """empty_ok=True (default) includes objects regardless of entry count.

    Args:
        root_file_path: Path to the pre-built test ROOT file.
    """
    fid = tfile(root_file_path, empty_ok=True)
    # tfile stores self._fid in the dict (attrdict.__setattr__ = dict.__setitem__),
    # so len(fid) == 5.  Check the four expected public keys directly.
    expected = {"mytree", "myhist", "myhist2d", "subdir"}
    assert expected.issubset(set(fid.keys()))


# ---------------------------------------------------------------------------
# IOError cases
# ---------------------------------------------------------------------------

def test_nonexistent_path_raises_ioerror(tmp_path):
    """A path that does not exist raises IOError.

    Args:
        tmp_path: pytest-provided temporary directory.
    """
    bad_path = str(tmp_path / "does_not_exist.root")
    with pytest.raises(IOError):
        tfile(bad_path)


def test_directory_path_raises_ioerror(tmp_path):
    """A path pointing to a directory (not a file) raises IOError.

    Args:
        tmp_path: pytest-provided temporary directory (exists but is a dir).
    """
    with pytest.raises(IOError):
        tfile(str(tmp_path))
