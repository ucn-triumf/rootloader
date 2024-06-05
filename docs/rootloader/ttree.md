# ttree

[Rootloader Index](../README.md#rootloader-index) / [Rootloader](./index.md#rootloader) / ttree

> Auto-generated documentation for [rootloader.ttree](../../rootloader/ttree.py) module.

- [ttree](#ttree)
  - [ttree](#ttree-1)
    - [ttree().get_subtree](#ttree()get_subtree)
    - [ttree().plot](#ttree()plot)
    - [ttree().to_dataframe](#ttree()to_dataframe)

## ttree

[Show source in ttree.py:11](../../rootloader/ttree.py#L11)

Extract ROOT.TTree fully into memory

#### Signature

```python
class ttree(attrdict):
    def __init__(self, tree): ...
```

### ttree().get_subtree

[Show source in ttree.py:93](../../rootloader/ttree.py#L93)

Return a copy of self but only for a subset of entries

#### Arguments

- `entries` *list|np.array* - list of entries to get from tree

#### Returns

- [ttree](#ttree) - copy with reduced entries

#### Signature

```python
def get_subtree(self, entries): ...
```

### ttree().plot

[Show source in ttree.py:115](../../rootloader/ttree.py#L115)

Convert to dataframe and plot. Arguments passed to [pandas.DataFrame.plot](https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.plot.html)

#### Returns

same as pandas.DataFrame.plot

#### Signature

```python
def plot(self, *args, **kwargs): ...
```

### ttree().to_dataframe

[Show source in ttree.py:124](../../rootloader/ttree.py#L124)

Convert tree to pandas dataframe

#### Returns

pd.DataFrame

#### Signature

```python
def to_dataframe(self): ...
```