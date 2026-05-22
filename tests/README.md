# Test Plan for `rootloader`

A comprehensive unit-test plan to be executed with `pytest`. No live/external
ROOT data files are required — every test builds its ROOT inputs in memory or
in a per-test temporary directory.

---

## 1. Objectives

- Exercise every public class (`attrdict`, `tdirectory`, `tfile`, `ttree`,
  `th1`, `th2`, `tleaf`) and every public method/property.
- Cover the **core usage path** (open → inspect → convert → plot) and the
  **edge cases** (empty objects, bad input, error branches).
- Verify the round-trip conversions (`th1`/`th2` ↔ `pd.DataFrame`,
  `tdirectory.to_dataframe()` ↔ `from_dataframe()`).
- Achieve ≥ 90 % line coverage and 100 % public-method coverage.

---

## 2. Testing Strategy — No Live Data

ROOT objects are created programmatically; the wrappers accept ROOT objects
directly, not just file paths.

| Target                       | How it is fed test data                                              |
|-------------------------------|----------------------------------------------------------------------|
| `th1`, `th2`                  | `ROOT.TH1F` / `ROOT.TH2F` built and filled in memory                  |
| `ttree`                       | `ROOT.TTree` built in memory (branch + fill loop)                     |
| `tleaf`                       | `tree.GetLeaf(name)` from an in-memory `ROOT.TTree`                   |
| `tdirectory`                  | `ROOT.TMemFile` — an in-memory `TFile`, no disk needed                |
| `tfile`                       | A real `.root` file written into `pytest`'s `tmp_path` at test time   |

`tfile` is the only class that requires a path on disk (`os.path.isfile` +
`ROOT.TFile(path, 'READ')`). Generating that file inside `tmp_path` keeps the
suite free of any committed/external data dependency.

**Determinism.** All inputs must be reproducible:
- Prefer deterministic fills (e.g. column = `np.arange(n)`) over random fills.
- When random fills are needed, call `ROOT.gRandom.SetSeed(<fixed>)` first.
- Compare floats with `pytest.approx` / `np.testing.assert_allclose`.

---

## 3. Directory Layout

```
tests/
├── README.md            # this plan
├── conftest.py          # shared fixtures + autouse environment patches
├── test_attrdict.py
├── test_th1.py
├── test_th2.py
├── test_ttree.py
├── test_tleaf.py
├── test_tdirectory.py
├── test_tfile.py
└── test_package.py
```

---

## 4. Shared Fixtures (`conftest.py`)

| Fixture                | Scope    | Provides                                                                 |
|------------------------|----------|--------------------------------------------------------------------------|
| `patch_terminal_size`  | autouse  | Patches `os.get_terminal_size` → `os.terminal_size((80, 24))` — see §5.1  |
| `mpl_agg`              | autouse  | Sets `matplotlib.use("Agg")` so `plot()` never opens a window            |
| `single_mt` (opt-out)  | function | `ROOT.DisableImplicitMT()` for order-sensitive tests — see §5.2          |
| `make_th1`             | function | Factory → filled `ROOT.TH1F` (params: nbins, range, fill pattern)        |
| `make_th2`             | function | Factory → filled `ROOT.TH2F`                                             |
| `make_tree`            | function | Factory → in-memory `ROOT.TTree` from a `{column: np.ndarray}` dict      |
| `memfile`              | function | `ROOT.TMemFile` populated with a tree + `th1` + `th2` + nested directory |
| `root_file_path`       | function | Writes a populated `.root` file into `tmp_path`, yields its path         |

Fixture implementation notes:
- `make_th1` / `make_th2` must call `hist.SetDirectory(0)` so the histogram is
  not destroyed when a parent file closes.
- `make_tree` keeps the branch buffer arrays and the `TTree` alive for the
  whole test (return them together / use a `yield`).
- `root_file_path` must `yield` (not `return`) and close the `TFile` only in
  teardown, so the file stays valid while the test reads it.
- A column dict for `make_tree` should cover `int` and `float` dtypes and
  include trees both with and without the index columns
  (`tUnixTimePrecise`, `timestamp`, `tEntry`).

---

## 5. Environment & Known Gotchas

These affect *how* tests are written; ignoring them causes spurious failures.

### 5.1 `os.get_terminal_size()` fails under `pytest`
`tdirectory.__repr__` and `ttree.__repr__` call `os.get_terminal_size()`.
Under `pytest`'s captured stdout this raises
`OSError: Inappropriate ioctl for device`. **Mitigation:** the autouse
`patch_terminal_size` fixture. Every `__repr__` test depends on it.

### 5.2 Implicit multithreading reorders rows
`ttree.py` calls `ROOT.EnableImplicitMT()` at import. With MT enabled,
`RDataFrame.AsNumpy()` (used by `to_dict`/`to_array`/`to_dataframe`) does **not
guarantee row order**. **Mitigation:** for tests that assert exact ordered
arrays, use the `single_mt` fixture (`DisableImplicitMT`) or compare
order-independently (sorted arrays / sets / aggregate stats).

### 5.3 ROOT object ownership / lifetime
Histograms auto-register in `gDirectory`; closing a file deletes attached
objects. Always `SetDirectory(0)` on standalone histograms, and keep
`TFile`/`TMemFile`/`TTree` references alive for the test's duration.

### 5.4 Global JIT interpreter state
`ttree._getstat` declares C++ into the shared ROOT interpreter and caches the
function on the `ROOT` module. State persists across tests — never assume a
clean interpreter. The `hasattr(ROOT, fn_name)` guard already makes
re-declaration safe; tests just must not depend on declaration order.

### 5.5 Matplotlib backend
Force the `Agg` backend (`mpl_agg` fixture) before any `plot()` test.

---

## 6. Test Modules

Legend: **[C]** core usage · **[E]** edge case.

### 6.1 `test_attrdict.py`

- [C] set/get via attribute (`ad.foo = 1` ⇒ `ad.foo == ad['foo'] == 1`).
- [C] set/get via item; attribute and item access are equivalent.
- [C] `del ad.foo` removes the key.
- [C] inherited dict methods still work (`keys`, `values`, `items`, `get`).
- [C] `dir(ad)` returns the current keys.
- [C] `__repr__` of a populated dict contains the class name and quoted keys.
- [C] `copy()` returns an independent `attrdict`; mutating the copy does not
  affect the original.
- [C] `copy()` recurses into values that expose `.copy()` (nested `attrdict`).
- [E] `copy()` passes non-copyable values (ints, strings) through by reference.
- [E] `__repr__` of an empty dict ⇒ `"attrdict()"`.
- [E] `__repr__` skips keys beginning with `__`.
- [E] `__repr__` handles non-string keys (e.g. integer keys).
- [E] accessing a genuinely missing attribute raises `AttributeError`.

### 6.2 `test_th1.py`

- [C] init from `ROOT.TH1F`: `name`, `title`, `nbins`, `entries`, `sum`,
  `base_class`, `xlabel`, `ylabel` populated correctly.
- [C] `x`, `y`, `dy` are numpy arrays of length `nbins`.
- [C] bin contents match the known fill pattern (use a deterministic fill).
- [C] `len(h) == nbins`.
- [C] `__repr__` contains class name, entries, and sum.
- [C] `copy()` produces independent arrays with equal values.
- [C] `to_dataframe()` columns are `xlabel`, `ylabel`, `"<ylabel> error"`.
- [C] `to_dataframe()` populates `df.attrs` with `type` and all metadata keys.
- [C] **round-trip**: `th1` → `to_dataframe()` → `th1(df)` reproduces `x/y/dy`
  and all metadata.
- [C] `plot(ax=...)` returns a matplotlib artist and draws on the given axes.
- [C] `plot(errors=True)` uses the errorbar branch and applies `draw_defaults`.
- [E] `th1()` (no arg) yields an empty object with no data attributes set.
- [E] `th1(hist=None)` behaves the same as no arg.
- [E] histogram with zero entries: `sum == 0`, arrays still length `nbins`.
- [E] `plot(data_only=True)` does not set axis labels/title.
- [E] `plot(ax=None)` falls back to `plt.gca()`.
- [E] `_from_dataframe` on a DataFrame missing `attrs` — document expected
  failure mode (`KeyError`/`AttributeError`).

### 6.3 `test_th2.py`

- [C] init from `ROOT.TH2F`: `nbinsx`, `nbinsy`, `xlabel`, `ylabel`, `zlabel`,
  `entries`, `sum`, `base_class` correct.
- [C] `x` length `nbinsx`, `y` length `nbinsy`.
- [C] `z` and `dz` have shape `(nbinsy, nbinsx)` after the internal transpose.
- [C] **orientation test**: fill one known asymmetric bin `(i, j)` with a
  unique value and assert it lands at `z[j, i]` — guards the transpose logic.
- [C] `copy()` produces independent arrays.
- [C] `to_dataframe()` has a 2-level `MultiIndex` named `(xlabel, ylabel)` and
  columns `zlabel`, `"<zlabel> error"`.
- [C] **round-trip**: `th2` → `to_dataframe()` → `th2(df)` reproduces the data.
- [C] `plot(flat=True)` draws a `pcolormesh`; `plot(flat=False)` draws a 3D
  surface.
- [E] `th2()` (no arg) yields an empty object.
- [E] zero-entry histogram.
- [C] `len(th2_obj)` equals `nbinsx * nbinsy`.

### 6.4 `test_ttree.py`

**Construction & identity**
- [C] init from `ROOT.TTree`: `columns`, `size`, `name` correct.
- [C] init from another `ttree` (copy semantics): independent filter list.
- [C] init from `None` yields a view stub (`name is None`).
- [E] init from an invalid type (e.g. `int`) raises `RuntimeError`.
- [C] index auto-detection priority: `tUnixTimePrecise` → `timestamp` →
  `tEntry` → `None` (one test per branch).

**Access & views**
- [C] `__getitem__` with a string returns a single-column view.
- [C] `__getitem__` with a list returns a multi-column view.
- [C] view shares `_rdf`/`_tree`; selecting columns does not mutate the parent.
- [C] `__getattr__` returns a column as a one-column `ttree`.
- [C] `__dir__` lists sorted column names.
- [C] `len(tr) == tr.size == tr._rdf.Count()`.
- [C] `__repr__` lists branch names (depends on `patch_terminal_size`).
- [E] `__getattr__` for a missing column falls back to object attribute lookup.

**Conversion**
- [C] `to_dict()` returns a dict of numpy arrays; index column is included.
- [C] `to_array()` → 1D array for one column, 2D for multiple.
- [C] `to_dataframe()` with ≥ 2 columns → `DataFrame` with the index set.
- [C] `to_dataframe()` with one non-index column → `pd.Series`.
- [C] `values` property mirrors `to_array()`.
- *(All conversion value-checks use `single_mt` or order-independent compares — §5.2.)*

**Statistics**
- [C] `min`, `max`, `mean`, `sum`, `std` on a single column → scalar value,
  verified against numpy on the known data.
- [C] same methods on a multi-column tree → `pd.Series` indexed by column.
- [C] calling a stat twice reuses the cached JIT function (no error; the
  `RDF_*` attribute exists on `ROOT` afterwards).
- [C] stats work for both `int` and `float` columns (distinct C++ dtypes).
- [E] stats on a zero-row tree — document the observed behavior.

**Histogramming**
- [C] `hist1d(nbins=...)`, `hist1d(step=...)`, `hist1d(edges=...)` each return
  a `th1` with the expected bin count.
- [C] `hist1d()` auto-selects the column when the tree has exactly one.
- [C] `hist2d(nxbins=, nybins=)` and `hist2d(xstep=, ystep=)` return a `th2`.
- [E] `hist1d()` with no binning arg raises `RuntimeError`.
- [E] `hist1d()` with more than one binning arg raises `RuntimeError`.
- [E] `hist1d()` on a multi-column tree with no `column` raises `KeyError`.
- [E] `hist1d(column=<unknown>)` raises `KeyError`.
- [E] `hist2d()` on a tree with < 2 or > 2 columns and no explicit columns
  raises `KeyError`.
- [E] `hist2d()` with both `nxbins` and `xstep` raises `RuntimeError`.

**Filters & mutation**
- [C] `set_filter(expr)` (not in place) returns a new `ttree` with reduced
  `size`; the original is unchanged.
- [C] `set_filter(expr, inplace=True)` reduces `size` and appends to `filters`.
- [C] `filters` property reflects applied filters.
- [C] `reset()` returns a fresh full tree.
- [C] `reset_columns()` restores all columns after a selection.
- [C] `set_index(col)` changes `index_name`.
- [E] `set_index(<unknown>)` raises `KeyError`.
- [C] `index` / `index_name` properties return the index view / name.

**`.loc` indexing (`_ttree_indexed`)**
- [C] `tr.loc[start:stop]` applies `>=`/`<` filters and reduces `size`.
- [E] `tr.loc[::step]` (slice with step) raises `NotImplementedError`.
- [C] `tr.loc[<scalar>]` applies an `==` filter on the index column.

### 6.5 `test_tleaf.py`

- [C] properties `name`, `branch`, `fullname`, `leaftype`, `len` for a scalar
  leaf taken from an in-memory tree.
- [C] `value` returns a Python float for a length-1 leaf.
- [C] `get_entry(i)` loads row `i` and returns its value.
- [E] `value` returns a numpy array for a multi-element leaf (build a tree
  with an array branch, e.g. `arr[3]/D`).
- [C] `copy()` returns a new `tleaf` wrapping the same underlying leaf.

### 6.6 `test_tdirectory.py`

- [C] parsing a `TMemFile` with a tree + `th1` + `th2` yields the correct
  wrapper type for each key.
- [C] keys are reachable both as items and as attributes.
- [C] a nested `TDirectoryFile` becomes a nested `tdirectory`.
- [C] cycle resolution: write the same key name twice (two cycles); only the
  highest cycle is kept.
- [C] `__repr__` renders the contents grid (depends on `patch_terminal_size`).
- [C] `copy()` deep-copies all wrapped objects.
- [C] `to_dataframe()` converts every convertible child to a `DataFrame`.
- [C] `from_dataframe()` round-trips a `to_dataframe()`'d directory back to
  `th1`/`th2`/`ttree` objects via the stored `attrs['type']`.
- [E] `empty_ok=False` skips an empty histogram / empty tree.
- [E] `quiet=False` prints a "Skipped …" message (assert with `capsys`).
- [E] `key_filter` excludes keys for which the predicate is `False`.
- [E] an object of an unsupported class triggers `warnings.warn`
  (assert with `pytest.warns`).
- [E] `tdirectory(None)` returns an empty object.
- [E] `__repr__` of an empty directory ⇒ `"tdirectory()"`.
- [C] `tree_filter={treename: (filter_string, columns)}` builds the named tree
  with that `RDataFrame.Filter` applied and that column subset selected. Also test a `treename` not present in the
  directory — it is simply ignored.

### 6.7 `test_tfile.py`

- [C] opening a real `.root` file (from `root_file_path`) reads its contents.
- [C] keys resolve to the correct wrapper types.
- [C] `tfile(None)` returns an empty object.
- [C] `as_dataframe=True` leaves all contents as `DataFrame`s.
- [C] `copy()` deep-copies contents.
- [C] `key_filter` / `empty_ok` are forwarded to `tdirectory`.
- [E] a non-existent path raises `IOError`.
- [E] a path pointing to a directory raises `IOError`.

### 6.8 `test_package.py`

- [C] every public name imports from `rootloader`: `attrdict`, `tdirectory`,
  `tfile`, `ttree`, `th1`, `th2`, `tleaf`.
- [C] ROOT batch mode is enabled after import (`ROOT.gROOT.IsBatch()` is true).
- [C] `rootloader.version.__version__` is a non-empty string.

---

## 7. Running the Suite

```bash
pip install -e ".[test]"          # or: pip install pytest pytest-cov

pytest                            # full suite
pytest tests/test_ttree.py        # one module
pytest tests/test_ttree.py::test_hist1d_nbins   # one test
pytest -q --cov=rootloader --cov-report=term-missing   # coverage
```

**Coverage goal:** ≥ 90 % line coverage, every public method exercised.
