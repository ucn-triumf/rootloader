# tfile

[Rootloader Index](../README.md#rootloader-index) / [Rootloader](./index.md#rootloader) / tfile

> Auto-generated documentation for [rootloader.tfile](../../rootloader/tfile.py) module.

- [tfile](#tfile)
  - [tfile](#tfile-1)
    - [tfile.copy](#tfilecopy)

## tfile

[Show source in tfile.py:9](../../rootloader/tfile.py#L9)

Contains root file data

#### Arguments

- `filename` *str* - path to root file to read
- `as_dataframe` *bool* - if true, run to_dataframe upon read
- `empty_ok` *bool* - if true, don't save empty objects
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
class tfile(tdirectory):
    def __init__(
        self,
        filename,
        as_dataframe=False,
        empty_ok=True,
        quiet=True,
        key_filter=None,
        tree_filter=None,
    ): ...
```

### tfile.copy

[Show source in tfile.py:51](../../rootloader/tfile.py#L51)

Make a copy of this object

#### Signature

```python
def copy(self): ...
```