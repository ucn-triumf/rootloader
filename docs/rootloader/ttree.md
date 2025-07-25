# ttree

[Rootloader Index](../README.md#rootloader-index) / [Rootloader](./index.md#rootloader) / ttree

> Auto-generated documentation for [rootloader.ttree](../../rootloader/ttree.py) module.

- [ttree](#ttree)
  - [ttree](#ttree-1)
    - [ttree.__getitem__](#ttree__getitem__)
    - [ttree.columns](#ttreecolumns)
    - [ttree.filters](#ttreefilters)
    - [ttree.hist1d](#ttreehist1d)
    - [ttree.hist2d](#ttreehist2d)
    - [ttree.index](#ttreeindex)
    - [ttree.index_name](#ttreeindex_name)
    - [ttree.loc](#ttreeloc)
    - [ttree.max](#ttreemax)
    - [ttree.mean](#ttreemean)
    - [ttree.min](#ttreemin)
    - [ttree.reset](#ttreereset)
    - [ttree.reset_columns](#ttreereset_columns)
    - [ttree.rms](#ttreerms)
    - [ttree.set_filter](#ttreeset_filter)
    - [ttree.set_index](#ttreeset_index)
    - [ttree.size](#ttreesize)
    - [ttree.std](#ttreestd)
    - [ttree.to_dataframe](#ttreeto_dataframe)
    - [ttree.to_dict](#ttreeto_dict)

## ttree

[Show source in ttree.py:14](../../rootloader/ttree.py#L14)

Extract ROOT.TTree with lazy operation. Looks like a dataframe in most ways

#### Arguments

- `tree` *str|hitstree* - tree to load
- `filter_string` *str|None* - if not none then pass this to [`RDataFrame.Filter`](https://root.cern/doc/master/classROOT_1_1RDF_1_1RInterface.html#ad6a94ba7e70fc8f6425a40a4057d40a0)
- `columns` *list|None* - list of column names to include in fetch, if None, get all

#### Signature

```python
class ttree(object):
    def __init__(self, tree): ...
```

### ttree.__getitem__

[Show source in ttree.py:79](../../rootloader/ttree.py#L79)

Fetch a new dataframe with fewer 'columns', as a memory view

#### Signature

```python
def __getitem__(self, key): ...
```

### ttree.columns

[Show source in ttree.py:318](../../rootloader/ttree.py#L318)

#### Signature

```python
@property
def columns(self): ...
```

### ttree.filters

[Show source in ttree.py:321](../../rootloader/ttree.py#L321)

#### Signature

```python
@property
def filters(self): ...
```

### ttree.hist1d

[Show source in ttree.py:129](../../rootloader/ttree.py#L129)

Return histogram of column

#### Arguments

- `column` *str* - column name, needed if more than one column
- `nbins` *int* - number of bins, span full range
- `step` *float* - bin spacing, span full range
- `edges` *array-like* - custom bin edges

Pick one of nbins|step|edges

#### Returns

rootloader.th1

#### Signature

```python
def hist1d(self, column=None, nbins=None, step=None, edges=None): ...
```

### ttree.hist2d

[Show source in ttree.py:182](../../rootloader/ttree.py#L182)

Return histogram of two columns

#### Arguments

- `column` *str* - column name, needed if more than one column
- `nbins` *int* - number of bins, span full range
- `step` *float* - bin spacing, span full range

#### Returns

rootloader.th2

#### Signature

```python
def hist2d(
    self, columnx=None, columny=None, nxbins=None, nybins=None, xstep=None, ystep=None
): ...
```

### ttree.index

[Show source in ttree.py:324](../../rootloader/ttree.py#L324)

#### Signature

```python
@property
def index(self): ...
```

### ttree.index_name

[Show source in ttree.py:327](../../rootloader/ttree.py#L327)

#### Signature

```python
@property
def index_name(self): ...
```

### ttree.loc

[Show source in ttree.py:330](../../rootloader/ttree.py#L330)

#### Signature

```python
@property
def loc(self): ...
```

### ttree.max

[Show source in ttree.py:354](../../rootloader/ttree.py#L354)

#### Signature

```python
def max(self): ...
```

### ttree.mean

[Show source in ttree.py:359](../../rootloader/ttree.py#L359)

#### Signature

```python
def mean(self): ...
```

### ttree.min

[Show source in ttree.py:349](../../rootloader/ttree.py#L349)

#### Signature

```python
def min(self): ...
```

### ttree.reset

[Show source in ttree.py:254](../../rootloader/ttree.py#L254)

Make a new tree

#### Signature

```python
def reset(self): ...
```

### ttree.reset_columns

[Show source in ttree.py:258](../../rootloader/ttree.py#L258)

Include all columns again

#### Signature

```python
def reset_columns(self): ...
```

### ttree.rms

[Show source in ttree.py:364](../../rootloader/ttree.py#L364)

#### Signature

```python
def rms(self): ...
```

### ttree.set_filter

[Show source in ttree.py:268](../../rootloader/ttree.py#L268)

Set a filter on the dataframe to select a subset of the data

#### Signature

```python
def set_filter(self, expression, inplace=False): ...
```

### ttree.set_index

[Show source in ttree.py:262](../../rootloader/ttree.py#L262)

Set the index column name

#### Signature

```python
def set_index(self, column): ...
```

### ttree.size

[Show source in ttree.py:333](../../rootloader/ttree.py#L333)

#### Signature

```python
@property
def size(self): ...
```

### ttree.std

[Show source in ttree.py:369](../../rootloader/ttree.py#L369)

#### Signature

```python
def std(self): ...
```

### ttree.to_dataframe

[Show source in ttree.py:280](../../rootloader/ttree.py#L280)

Return pandas dataframe of the data

#### Signature

```python
def to_dataframe(self): ...
```

### ttree.to_dict

[Show source in ttree.py:307](../../rootloader/ttree.py#L307)

#### Signature

```python
def to_dict(self): ...
```