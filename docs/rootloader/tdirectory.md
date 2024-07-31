# tdirectory

[Rootloader Index](../README.md#rootloader-index) / [Rootloader](./index.md#rootloader) / tdirectory

> Auto-generated documentation for [rootloader.tdirectory](../../rootloader/tdirectory.py) module.

- [tdirectory](#tdirectory)
  - [tdirectory](#tdirectory-1)
    - [tdirectory().copy](#tdirectory()copy)
    - [tdirectory().to_dataframe](#tdirectory()to_dataframe)

## tdirectory

[Show source in tdirectory.py:13](../../rootloader/tdirectory.py#L13)

Contains root file data

#### Arguments

- `directory` *ROOT.TDirectoryFile|ROOT.TFile* - object to parse
- `empty_ok` *bool* - if true, save empty objects
- `quiet` *bool* - if true, don't print skipped statement if object empty

#### Signature

```python
class tdirectory(attrdict):
    def __init__(self, directory, empty_ok=True, quiet=True): ...
```

### tdirectory().copy

[Show source in tdirectory.py:99](../../rootloader/tdirectory.py#L99)

Make a copy of this object

#### Signature

```python
def copy(self): ...
```

### tdirectory().to_dataframe

[Show source in tdirectory.py:108](../../rootloader/tdirectory.py#L108)

Convert all objects possible (th1 and ttree) into pandas dataframes

#### Signature

```python
def to_dataframe(self): ...
```