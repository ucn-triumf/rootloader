"""Tests for top-level rootloader package imports and global state.

Covers §6.8 of the test plan:
  - All seven public names are importable directly from rootloader.
  - ROOT batch mode is enabled after import.
  - rootloader.version.__version__ is a non-empty string.
"""

import ROOT
import rootloader
import rootloader.version
from rootloader import attrdict, tdirectory, tfile, ttree, th1, th2, tleaf


def test_public_names_importable():
    """All seven public names are accessible directly from the rootloader namespace.

    Checks that each name is not None, which confirms the import succeeded and
    the symbol was bound to a real object.
    """
    assert attrdict is not None
    assert tdirectory is not None
    assert tfile is not None
    assert ttree is not None
    assert th1 is not None
    assert th2 is not None
    assert tleaf is not None


def test_root_batch_mode_enabled():
    """ROOT batch mode is active after importing rootloader.

    rootloader/__init__.py calls ROOT.gROOT.SetBatch(1); this test confirms
    that call was executed so no graphical windows are opened during tests.
    """
    assert ROOT.gROOT.IsBatch()


def test_version_is_nonempty_string():
    """rootloader.version.__version__ is a non-empty string.

    The version value is not hardcoded here so the test remains valid across
    releases.
    """
    version = rootloader.version.__version__
    assert isinstance(version, str)
    assert len(version) > 0
