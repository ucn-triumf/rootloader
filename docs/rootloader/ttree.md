# ttree

[Rootloader Index](../README.md#rootloader-index) / [Rootloader](./index.md#rootloader) / ttree

> Auto-generated documentation for [rootloader.ttree](../../rootloader/ttree.py) module.

- [ttree](#ttree)
  - [ttree](#ttree-1)
    - [ttree.copy](#ttreecopy)
    - [ttree.entries](#ttreeentries)
    - [ttree.get_subtree](#ttreeget_subtree)
    - [ttree.plot](#ttreeplot)
    - [ttree.to_dataframe](#ttreeto_dataframe)

## ttree

[Show source in ttree.py:12](../../rootloader/ttree.py#L12)

Extract ROOT.TTree fully into memory

#### Arguments

- `tree` *ROOT.TTree|pd.DataFrame* - tree to load
- `filter_string` *str|None* - if not none then pass this to [`RDataFrame.Filter`](https://root.cern/doc/master/classROOT_1_1RDF_1_1RInterface.html#ad6a94ba7e70fc8f6425a40a4057d40a0)
- `columns` *list|None* - list of column names to include in fetch, if None, get all

#### Signature

```python
class ttree(attrdict):
    def __init__(self, tree=None, filter_str=None, columns=None): ...
```

### ttree.copy

[Show source in ttree.py:162](../../rootloader/ttree.py#L162)

Produce a copy of this object

#### Signature

```python
def copy(self): ...
```

### ttree.entries

[Show source in ttree.py:173](../../rootloader/ttree.py#L173)

#### Signature

```python
@property
def entries(self): ...
```

### ttree.get_subtree

[Show source in ttree.py:176](../../rootloader/ttree.py#L176)

Return a copy of self but only for a subset of entries

#### Arguments

- [ttree.entries](#ttreeentries) *list|np.array* - list of entries to get from tree

#### Returns

- [ttree](#ttree) - copy with reduced entries

#### Signature

```python
def get_subtree(self, entries): ...
```

### ttree.plot

[Show source in ttree.py:198](../../rootloader/ttree.py#L198)

Convert to dataframe and plot. Arguments passed to [pandas.DataFrame.plot](https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.plot.html)

#### Returns

same as pandas.DataFrame.plot

#### Signature

```python
def plot(self, *args, **kwargs): ...
```

### ttree.to_dataframe

[Show source in ttree.py:206](../../rootloader/ttree.py#L206)

Convert tree to pandas dataframe

#### Returns

pd.DataFrame

#### Signature

```python
def to_dataframe(self): ...
```