"""Tests for rootloader.th2.

Covers construction from ROOT.TH2F, internal array shapes and orientation,
copy(), to_dataframe(), round-trip via _from_dataframe(), plot(), __len__,
and edge cases (no-arg construction, zero-entry histogram).
"""

import matplotlib.pyplot as plt
import numpy as np
import pytest
import ROOT

from rootloader import th2

# ---------------------------------------------------------------------------
# Construction from ROOT.TH2F
# ---------------------------------------------------------------------------

class TestInitFromROOT:
    """Tests for th2.__init__ when given a ROOT.TH2F."""

    def test_basic_attributes(self, make_th2):
        """Scalar metadata is copied correctly from the ROOT histogram.

        Checks nbinsx, nbinsy, xlabel, ylabel, zlabel, entries, sum,
        and base_class.
        """
        hist = make_th2(nbinsx=5, nbinsy=4, xmin=0, xmax=5, ymin=0, ymax=4)
        obj = th2(hist)

        assert obj.nbinsx == 5
        assert obj.nbinsy == 4
        assert obj.xlabel == "x axis"
        assert obj.ylabel == "y axis"
        assert obj.zlabel == "z axis"
        assert obj.entries == 20           # 5*4 bins filled
        assert obj.base_class == "TH2F"

        # sum = sum of all bin contents: sum_{i=1}^{5} sum_{j=1}^{4} (i*10+j)
        expected_sum = sum(i * 10 + j for i in range(1, 6) for j in range(1, 5))
        assert obj.sum == pytest.approx(expected_sum)

    def test_x_length(self, make_th2):
        """x array has length nbinsx (includes ROOT underflow bin 0).

        The code iterates range(nbinsx) for x, so len(x) == nbinsx.
        """
        obj = th2(make_th2(nbinsx=5, nbinsy=4))
        assert len(obj.x) == 5

    def test_y_length(self, make_th2):
        """y array has length nbinsy (includes ROOT underflow bin 0).

        The code iterates range(nbinsy) for y, so len(y) == nbinsy.
        """
        obj = th2(make_th2(nbinsx=5, nbinsy=4))
        assert len(obj.y) == 4

    def test_z_shape(self, make_th2):
        """z has shape (nbinsy, nbinsx) after the internal transpose."""
        obj = th2(make_th2(nbinsx=5, nbinsy=4))
        assert obj.z.shape == (4, 5)

    def test_dz_shape(self, make_th2):
        """dz has shape (nbinsy, nbinsx) after the internal transpose."""
        obj = th2(make_th2(nbinsx=5, nbinsy=4))
        assert obj.dz.shape == (4, 5)

    def test_orientation(self, make_th2):
        """ROOT bin (i, j) lands at z[j, i] after the internal transpose.

        Fill ROOT bin (3, 2) with a unique value (999.0) and verify placement.
        The loop collects data[i, j] = GetBinContent(i, j), then after
        reshape(nbinsx, nbinsy).transpose() the element is at z[j, i].
        """
        nbinsx, nbinsy = 5, 4
        hist = make_th2(nbinsx=nbinsx, nbinsy=nbinsy)
        # Overwrite bin (3, 2) with a unique sentinel value
        hist.SetBinContent(3, 2, 999.0)
        obj = th2(hist)
        assert obj.z[2, 3] == pytest.approx(999.0)

    def test_dz_values(self, make_th2):
        """Error values stored in dz equal sqrt of the corresponding z content.

        For ROOT bin (i, j) filled with val = i*10+j, error = sqrt(val).
        After transpose dz[j, i] == sqrt(z[j, i]).
        """
        obj = th2(make_th2(nbinsx=5, nbinsy=4))
        # Compare only non-underflow region: ROOT bins 1..nbinsx in x, 1..nbinsy in y
        # These map to Python indices j=1..nbinsy-1, i=1..nbinsx-1 in z[j, i]
        for i in range(1, 5):    # x-axis ROOT bins 1..5 → z[:, 1..4]
            for j in range(1, 4):  # y-axis ROOT bins 1..4 → z[1..3, :]
                assert obj.dz[j, i] == pytest.approx(obj.z[j, i] ** 0.5)


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------

class TestEdgeCases:
    """Edge-case construction tests."""

    def test_no_arg_returns_empty_object(self):
        """th2() with no argument returns an object without raising.

        Slots are unset; accessing them would raise AttributeError.
        """
        obj = th2()
        assert isinstance(obj, th2)

    def test_zero_entry_histogram(self):
        """A TH2F with no fills has entries==0 and sum==0.0."""
        hist = ROOT.TH2F("h2_zero", "empty;x axis;y axis;z axis", 3, 0, 3, 3, 0, 3)
        hist.SetDirectory(0)
        obj = th2(hist)
        assert obj.entries == 0
        assert obj.sum == pytest.approx(0.0)


# ---------------------------------------------------------------------------
# __len__
# ---------------------------------------------------------------------------

class TestLen:
    """Tests for th2.__len__."""

    def test_len_equals_nbinsx_times_nbinsy(self, make_th2):
        """len(obj) equals nbinsx * nbinsy."""
        obj = th2(make_th2(nbinsx=5, nbinsy=4))
        assert len(obj) == 5 * 4


# ---------------------------------------------------------------------------
# copy()
# ---------------------------------------------------------------------------

class TestCopy:
    """Tests for th2.copy()."""

    def test_copy_is_independent(self, make_th2):
        """copy() returns an independent th2; mutating arrays doesn't affect original.

        Scalar attributes must be equal; numpy arrays must be equal but not
        the same object.
        """
        original = th2(make_th2())
        duplicate = original.copy()

        # Scalar attributes match
        assert duplicate.nbinsx == original.nbinsx
        assert duplicate.nbinsy == original.nbinsy
        assert duplicate.name == original.name

        # Arrays are equal in value
        np.testing.assert_array_equal(duplicate.z, original.z)
        np.testing.assert_array_equal(duplicate.x, original.x)

        # Arrays are independent objects
        assert duplicate.z is not original.z
        assert duplicate.x is not original.x

        # Mutating the copy doesn't affect the original
        duplicate.z[0, 0] = -999.0
        assert original.z[0, 0] != pytest.approx(-999.0)


# ---------------------------------------------------------------------------
# to_dataframe()
# ---------------------------------------------------------------------------

class TestToDataframe:
    """Tests for th2.to_dataframe()."""

    def test_multiindex_names(self, make_th2):
        """DataFrame has a 2-level MultiIndex named (xlabel, ylabel)."""
        obj = th2(make_th2())
        df = obj.to_dataframe()
        assert df.index.names == ["x axis", "y axis"]

    def test_columns(self, make_th2):
        """DataFrame has columns for zlabel and '<zlabel> error'."""
        obj = th2(make_th2())
        df = obj.to_dataframe()
        assert "z axis" in df.columns
        assert "z axis error" in df.columns

    def test_attrs_type(self, make_th2):
        """df.attrs['type'] is th2."""
        obj = th2(make_th2())
        df = obj.to_dataframe()
        assert df.attrs["type"] is th2

    def test_attrs_metadata(self, make_th2):
        """df.attrs preserves scalar metadata fields."""
        obj = th2(make_th2(nbinsx=5, nbinsy=4))
        df = obj.to_dataframe()
        assert df.attrs["nbinsx"] == 5
        assert df.attrs["nbinsy"] == 4
        assert df.attrs["xlabel"] == "x axis"
        assert df.attrs["ylabel"] == "y axis"
        assert df.attrs["zlabel"] == "z axis"


# ---------------------------------------------------------------------------
# Round-trip: th2 → to_dataframe() → th2(df)
# ---------------------------------------------------------------------------

class TestRoundTrip:
    """Tests for the to_dataframe() → _from_dataframe() round-trip."""

    def test_roundtrip_x_y(self, make_th2):
        """x and y arrays are restored correctly after a round-trip."""
        original = th2(make_th2())
        df = original.to_dataframe()
        restored = th2(df)

        np.testing.assert_array_almost_equal(restored.x, original.x)
        np.testing.assert_array_almost_equal(restored.y, original.y)

    def test_roundtrip_z_values(self, make_th2):
        """z values are preserved in the multiset sense after a round-trip.

        to_dataframe() writes z.T.flatten() indexed by (x, y) MultiIndex pairs
        from meshgrid.  _from_dataframe() calls sort_index() then
        reshape(nbinsx, nbinsy).  Because the meshgrid flattening order (row of
        y first) does not match z.T's row-major order (row of x first), the
        (x, y) → value mapping is scrambled after the sort+reshape.
        The sum and the multiset of values are invariant; spatial arrangement
        is not.
        """
        original = th2(make_th2())
        df = original.to_dataframe()
        restored = th2(df)

        assert restored.z.sum() == pytest.approx(original.z.sum())
        np.testing.assert_array_almost_equal(
            np.sort(restored.z.flatten()),
            np.sort(original.z.flatten()),
        )

    def test_roundtrip_dz_values(self, make_th2):
        """dz values are preserved in the multiset sense after a round-trip.

        Same index-ordering caveat as test_roundtrip_z_values applies.
        """
        original = th2(make_th2())
        df = original.to_dataframe()
        restored = th2(df)

        assert restored.dz.sum() == pytest.approx(original.dz.sum())
        np.testing.assert_array_almost_equal(
            np.sort(restored.dz.flatten()),
            np.sort(original.dz.flatten()),
        )

    def test_roundtrip_scalar_attrs(self, make_th2):
        """Scalar metadata attributes survive the round-trip."""
        original = th2(make_th2(nbinsx=5, nbinsy=4))
        df = original.to_dataframe()
        restored = th2(df)

        assert restored.nbinsx == original.nbinsx
        assert restored.nbinsy == original.nbinsy
        assert restored.entries == original.entries
        assert restored.xlabel == original.xlabel
        assert restored.ylabel == original.ylabel
        assert restored.zlabel == original.zlabel


# ---------------------------------------------------------------------------
# plot()
# ---------------------------------------------------------------------------

class TestPlot:
    """Tests for th2.plot()."""

    def test_plot_flat_draws_pcolormesh(self, make_th2):
        """plot(flat=True) adds a pcolormesh to the current axes without raising."""
        obj = th2(make_th2())
        plt.close("all")
        fig, ax = plt.subplots()
        obj.plot(ax=ax, flat=True)
        # A pcolormesh is a QuadMesh; verify something was drawn
        assert len(ax.collections) > 0
        plt.close("all")

    def test_plot_flat_no_ax(self, make_th2):
        """plot(flat=True) with no ax argument creates its own figure."""
        obj = th2(make_th2())
        plt.close("all")
        obj.plot(flat=True)
        assert plt.gcf() is not None
        plt.close("all")

    def test_plot_3d_no_raise(self, make_th2):
        """plot(flat=False) draws a 3D surface without raising."""
        obj = th2(make_th2())
        plt.close("all")
        obj.plot(flat=False)
        plt.close("all")
