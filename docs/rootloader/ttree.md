# ttree

[Rootloader Index](../README.md#rootloader-index) / [Rootloader](./index.md#rootloader) / ttree

> Auto-generated documentation for [rootloader.ttree](../../rootloader/ttree.py) module.

- [ttree](#ttree)
  - [ttree](#ttree-1)
    - [ttree().copy](#ttree()copy)
    - [ttree().entries](#ttree()entries)
    - [ttree().get_subtree](#ttree()get_subtree)
    - [ttree().plot](#ttree()plot)
    - [ttree().to_dataframe](#ttree()to_dataframe)

## ttree

[Show source in ttree.py:12](../../rootloader/ttree.py#L12)

Extract ROOT.TTree fully into memory

#### Arguments

- `tree` *ROOT.TTree|pd.DataFrame* - tree to load

#### Signature

```python
class ttree(attrdict):
    def __init__(self, tree=None): ...
```

### ttree().copy

[Show source in ttree.py:135](../../rootloader/ttree.py#L135)

Produce a copy of this object

#### Signature

```python
def copy(self): ...
```

### ttree().entries

[Show source in ttree.py:146](../../rootloader/ttree.py#L146)

#### Signature

```python
@property
def entries(self): ...
```

### ttree().get_subtree

[Show source in ttree.py:149](../../rootloader/ttree.py#L149)

Return a copy of self but only for a subset of entries

#### Arguments

- [ttree().entries](#ttreeentries) *list|np.array* - list of entries to get from tree

#### Returns

- [ttree](#ttree) - copy with reduced entries

#### Signature

```python
def get_subtree(self, entries): ...
```

### ttree().plot

[Show source in ttree.py:171](../../rootloader/ttree.py#L171)

Convert to dataframe and plot. Arguments passed to [pandas.DataFrame.plot](https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.plot.html)

#### Returns

same as pandas.DataFrame.plot

#### Signature

```python
def plot(self, *args, **kwargs): ...
```

### ttree().to_dataframe

[Show source in ttree.py:179](../../rootloader/ttree.py#L179)

Convert tree to pandas dataframe

#### Returns

pd.DataFrame

#### Signature

```python
def to_dataframe(self): ...
```