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
    - [ttree.set_filter](#ttreeset_filter)
    - [ttree.set_index](#ttreeset_index)
    - [ttree.size](#ttreesize)
    - [ttree.std](#ttreestd)
    - [ttree.sum](#ttreesum)
    - [ttree.to_array](#ttreeto_array)
    - [ttree.to_dataframe](#ttreeto_dataframe)
    - [ttree.to_dict](#ttreeto_dict)
    - [ttree.values](#ttreevalues)

## ttree

[Show source in ttree.py:103](../../rootloader/ttree.py#L103)

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

[Show source in ttree.py:165](../../rootloader/ttree.py#L165)

Fetch a new dataframe with fewer 'columns', as a memory view

#### Signature

```python
def __getitem__(self, key): ...
```

### ttree.columns

[Show source in ttree.py:420](../../rootloader/ttree.py#L420)

#### Signature

```python
@property
def columns(self): ...
```

### ttree.filters

[Show source in ttree.py:423](../../rootloader/ttree.py#L423)

#### Signature

```python
@property
def filters(self): ...
```

### ttree.hist1d

[Show source in ttree.py:214](../../rootloader/ttree.py#L214)

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

[Show source in ttree.py:267](../../rootloader/ttree.py#L267)

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

[Show source in ttree.py:426](../../rootloader/ttree.py#L426)

#### Signature

```python
@property
def index(self): ...
```

### ttree.index_name

[Show source in ttree.py:429](../../rootloader/ttree.py#L429)

#### Signature

```python
@property
def index_name(self): ...
```

### ttree.loc

[Show source in ttree.py:432](../../rootloader/ttree.py#L432)

#### Signature

```python
@property
def loc(self): ...
```

### ttree.max

[Show source in ttree.py:464](../../rootloader/ttree.py#L464)

#### Signature

```python
def max(self): ...
```

### ttree.mean

[Show source in ttree.py:465](../../rootloader/ttree.py#L465)

#### Signature

```python
def mean(self): ...
```

### ttree.min

[Show source in ttree.py:463](../../rootloader/ttree.py#L463)

#### Signature

```python
def min(self): ...
```

### ttree.reset

[Show source in ttree.py:339](../../rootloader/ttree.py#L339)

Make a new tree

#### Signature

```python
def reset(self): ...
```

### ttree.reset_columns

[Show source in ttree.py:343](../../rootloader/ttree.py#L343)

Include all columns again

#### Signature

```python
def reset_columns(self): ...
```

### ttree.set_filter

[Show source in ttree.py:353](../../rootloader/ttree.py#L353)

Set a filter on the dataframe to select a subset of the data

#### Signature

```python
def set_filter(self, expression, inplace=False): ...
```

### ttree.set_index

[Show source in ttree.py:347](../../rootloader/ttree.py#L347)

Set the index column name

#### Signature

```python
def set_index(self, column): ...
```

### ttree.size

[Show source in ttree.py:435](../../rootloader/ttree.py#L435)

#### Signature

```python
@property
def size(self): ...
```

### ttree.std

[Show source in ttree.py:467](../../rootloader/ttree.py#L467)

#### Signature

```python
def std(self): ...
```

### ttree.sum

[Show source in ttree.py:466](../../rootloader/ttree.py#L466)

#### Signature

```python
def sum(self): ...
```

### ttree.to_array

[Show source in ttree.py:364](../../rootloader/ttree.py#L364)

Return numpy array of the data

#### Signature

```python
def to_array(self): ...
```

### ttree.to_dataframe

[Show source in ttree.py:375](../../rootloader/ttree.py#L375)

Return pandas dataframe of the data

#### Signature

```python
def to_dataframe(self): ...
```

### ttree.to_dict

[Show source in ttree.py:409](../../rootloader/ttree.py#L409)

#### Signature

```python
def to_dict(self): ...
```

### ttree.values

[Show source in ttree.py:438](../../rootloader/ttree.py#L438)

#### Signature

```python
@property
def values(self): ...
```