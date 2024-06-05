# ttree

[Rootloader Index](../README.md#rootloader-index) / [Rootloader](./index.md#rootloader) / ttree

> Auto-generated documentation for [rootloader.ttree](../../rootloader/ttree.py) module.

- [ttree](#ttree)
  - [ttree](#ttree-1)
    - [ttree().get_subtree](#ttree()get_subtree)
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

#### Signature

```python
def get_subtree(self, entries): ...
```

### ttree().to_dataframe

[Show source in ttree.py:108](../../rootloader/ttree.py#L108)

Convert tree to pandas dataframe

#### Returns

pd.DataFrame

#### Signature

```python
def to_dataframe(self): ...
```