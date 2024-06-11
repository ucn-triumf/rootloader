# tdirectory

[Rootloader Index](../README.md#rootloader-index) / [Rootloader](./index.md#rootloader) / tdirectory

> Auto-generated documentation for [rootloader.tdirectory](../../rootloader/tdirectory.py) module.

- [tdirectory](#tdirectory)
  - [tdirectory](#tdirectory-1)
    - [tdirectory().to_dataframe](#tdirectory()to_dataframe)

## tdirectory

[Show source in tdirectory.py:13](../../rootloader/tdirectory.py#L13)

Contains root file data

#### Arguments

- `directory` *ROOT.TDirectoryFile|ROOT.TFile* - object to parse
- `keep_empty_objs` *bool* - if true, don't save empty objects

#### Signature

```python
class tdirectory(attrdict):
    def __init__(self, directory, keep_empty_objs=True): ...
```

### tdirectory().to_dataframe

[Show source in tdirectory.py:96](../../rootloader/tdirectory.py#L96)

Convert all objects possible (th1 and ttree) into pandas dataframes

#### Signature

```python
def to_dataframe(self): ...
```