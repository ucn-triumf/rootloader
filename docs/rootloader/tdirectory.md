# tdirectory

[Rootloader Index](../README.md#rootloader-index) / [Rootloader](./index.md#rootloader) / tdirectory

> Auto-generated documentation for [rootloader.tdirectory](../../rootloader/tdirectory.py) module.

- [tdirectory](#tdirectory)
  - [tdirectory](#tdirectory-1)
    - [tdirectory().copy](#tdirectory()copy)
    - [tdirectory().from_dataframe](#tdirectory()from_dataframe)
    - [tdirectory().to_dataframe](#tdirectory()to_dataframe)

## tdirectory

[Show source in tdirectory.py:14](../../rootloader/tdirectory.py#L14)

Contains root file data

#### Arguments

- `directory` *ROOT.TDirectoryFile|ROOT.TFile* - object to parse
- `empty_ok` *bool* - if true, save empty objects
- `quiet` *bool* - if true, don't print skipped statement if object empty
key_filter (function handle): a function with the following signature:
    bool fn(str) -- takes as input a string and returns a bool
    indicating whether the object with the corresponding key should
    be read

#### Signature

```python
class tdirectory(attrdict):
    def __init__(self, directory, empty_ok=True, quiet=True, key_filter=None): ...
```

### tdirectory().copy

[Show source in tdirectory.py:108](../../rootloader/tdirectory.py#L108)

Make a copy of this object

#### Signature

```python
def copy(self): ...
```

### tdirectory().from_dataframe

[Show source in tdirectory.py:117](../../rootloader/tdirectory.py#L117)

Convert all elements contained in self to original objects

#### Signature

```python
def from_dataframe(self): ...
```

### tdirectory().to_dataframe

[Show source in tdirectory.py:128](../../rootloader/tdirectory.py#L128)

Convert all objects possible (th1, th2, and ttree) into pandas dataframes

#### Signature

```python
def to_dataframe(self): ...
```