# tdirectory

[Rootloader Index](../README.md#rootloader-index) / [Rootloader](./index.md#rootloader) / tdirectory

> Auto-generated documentation for [rootloader.tdirectory](../../rootloader/tdirectory.py) module.

- [tdirectory](#tdirectory)
  - [tdirectory](#tdirectory-1)
    - [tdirectory.copy](#tdirectorycopy)
    - [tdirectory.from_dataframe](#tdirectoryfrom_dataframe)
    - [tdirectory.to_dataframe](#tdirectoryto_dataframe)

## tdirectory

[Show source in tdirectory.py:15](../../rootloader/tdirectory.py#L15)

Contains root file data

#### Arguments

- `directory` *ROOT.TDirectoryFile|ROOT.TFile* - object to parse
- `empty_ok` *bool* - if true, save empty objects
- `quiet` *bool* - if true, don't print skipped statement if object empty
key_filter (function handle): a function with the following signature:
    bool fn(str) -- takes as input a string and returns a bool
    indicating whether the object with the corresponding key should
    be read
- `tree_filter` *dict* - {treename: (filter_string, [columns])}
    - `treename` *str* - name of the tree to apply elements to
    - `filter_string` *str|None* - if not none then pass this to [`RDataFrame.Filter`](https://root.cern/doc/master/classROOT_1_1RDF_1_1RInterface.html#ad6a94ba7e70fc8f6425a40a4057d40a0)
    - `[columns]` *list|None* - list of column names to include in fetch, if None, get all

#### Signature

```python
class tdirectory(attrdict):
    def __init__(
        self, directory, empty_ok=True, quiet=True, key_filter=None, tree_filter=None
    ): ...
```

### tdirectory.copy

[Show source in tdirectory.py:122](../../rootloader/tdirectory.py#L122)

Make a copy of this object

#### Signature

```python
def copy(self): ...
```

### tdirectory.from_dataframe

[Show source in tdirectory.py:131](../../rootloader/tdirectory.py#L131)

Convert all elements contained in self to original objects

#### Signature

```python
def from_dataframe(self): ...
```

### tdirectory.to_dataframe

[Show source in tdirectory.py:142](../../rootloader/tdirectory.py#L142)

Convert all objects possible (th1, th2, and ttree) into pandas dataframes

#### Signature

```python
def to_dataframe(self): ...
```