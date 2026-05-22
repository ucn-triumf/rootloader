"""Tests for rootloader.attrdict."""

import pytest

from rootloader import attrdict


# ---------------------------------------------------------------------------
# Attribute and item access
# ---------------------------------------------------------------------------

def test_set_get_attribute():
    """Setting via attribute makes value accessible as both attribute and item."""
    ad = attrdict()
    ad.foo = 1
    assert ad.foo == 1
    assert ad["foo"] == 1  # attribute and item access are equivalent


def test_set_get_item():
    """Setting via item makes value accessible as both item and attribute."""
    ad = attrdict()
    ad["bar"] = 42
    assert ad["bar"] == 42
    assert ad.bar == 42  # item and attribute access are equivalent


def test_delete_attribute():
    """Deleting via attribute removes the key from the dict."""
    ad = attrdict()
    ad.foo = 1
    del ad.foo
    assert "foo" not in ad


# ---------------------------------------------------------------------------
# Inherited dict methods
# ---------------------------------------------------------------------------

def test_dict_methods_keys_values_items():
    """Standard dict methods (keys, values, items) work on attrdict."""
    ad = attrdict()
    ad.a = 1
    ad.b = 2
    assert set(ad.keys()) == {"a", "b"}
    assert set(ad.values()) == {1, 2}
    assert set(ad.items()) == {("a", 1), ("b", 2)}


def test_dict_method_get():
    """The dict.get method returns the value or a default for missing keys."""
    ad = attrdict()
    ad.x = 99
    assert ad.get("x") == 99
    assert ad.get("missing", -1) == -1  # default returned for absent key


# ---------------------------------------------------------------------------
# dir()
# ---------------------------------------------------------------------------

def test_dir_returns_current_keys():
    """dir(ad) returns exactly the current set of dict keys."""
    ad = attrdict()
    ad.alpha = 1
    ad.beta = 2
    assert set(dir(ad)) == {"alpha", "beta"}


# ---------------------------------------------------------------------------
# __repr__
# ---------------------------------------------------------------------------

def test_repr_populated_contains_class_name_and_keys():
    """repr of a populated attrdict includes the class name and quoted keys."""
    ad = attrdict()
    ad.foo = 1
    ad.bar = 2
    r = repr(ad)
    assert "attrdict" in r
    assert "'foo'" in r
    assert "'bar'" in r


def test_repr_empty():
    """repr of an empty attrdict is 'attrdict()'."""
    ad = attrdict()
    assert repr(ad) == "attrdict()"


def test_repr_skips_dunder_keys():
    """repr skips string keys that begin with '__'."""
    ad = attrdict()
    ad["__hidden"] = "secret"
    ad.visible = "shown"
    r = repr(ad)
    assert "__hidden" not in r
    assert "'visible'" in r


def test_repr_non_string_keys():
    """repr handles integer keys without quoting them."""
    ad = attrdict()
    ad[42] = "value"
    r = repr(ad)
    # Integer keys appear without surrounding quotes
    assert "42" in r
    assert "'42'" not in r


# ---------------------------------------------------------------------------
# copy()
# ---------------------------------------------------------------------------

def test_copy_returns_independent_attrdict():
    """copy() returns an attrdict whose mutations do not affect the original."""
    ad = attrdict()
    ad.x = 10
    copy = ad.copy()
    copy.x = 99
    # Original is unchanged after mutating the copy
    assert ad.x == 10
    assert copy.x == 99


def test_copy_recurses_into_nested_attrdict():
    """copy() deep-copies nested attrdict values via their own .copy()."""
    inner = attrdict()
    inner.val = 7
    outer = attrdict()
    outer.nested = inner

    outer_copy = outer.copy()
    outer_copy.nested.val = 999

    # The original inner attrdict is unaffected
    assert inner.val == 7


def test_copy_passes_through_non_copyable_values():
    """copy() passes ints and strings by reference (no .copy() available)."""
    ad = attrdict()
    ad.num = 5
    ad.text = "hello"
    copy = ad.copy()
    # Values are equal; ints/strings are immutable so reference equality is fine
    assert copy.num == 5
    assert copy.text == "hello"


# ---------------------------------------------------------------------------
# Missing attribute raises AttributeError
# ---------------------------------------------------------------------------

def test_missing_attribute_raises():
    """Accessing a key that does not exist raises AttributeError."""
    ad = attrdict()
    with pytest.raises(AttributeError):
        _ = ad.does_not_exist
