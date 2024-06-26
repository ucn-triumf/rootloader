# tfile

[Rootloader Index](../README.md#rootloader-index) / [Rootloader](./index.md#rootloader) / tfile

> Auto-generated documentation for [rootloader.tfile](../../rootloader/tfile.py) module.

- [tfile](#tfile)
  - [tfile](#tfile-1)

## tfile

[Show source in tfile.py:9](../../rootloader/tfile.py#L9)

Contains root file data

#### Arguments

- `filename` *str* - path to root file to read
- `as_dataframe` *bool* - if true, run to_dataframe upon read
- `empty_ok` *bool* - if true, don't save empty objects

#### Signature

```python
class tfile(tdirectory):
    def __init__(self, filename, as_dataframe=False, empty_ok=True): ...
```