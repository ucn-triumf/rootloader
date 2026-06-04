# ttree

[Rootloader Index](../README.md#rootloader-index) / [Rootloader](./index.md#rootloader) / ttree

> Auto-generated documentation for [rootloader.ttree](../../rootloader/ttree.py) module.

#### Attributes

- `cpp_template` - template to pre-compile stats functions to avoid memory creep during JIT compilations
  used in ttree._get_stat: '\n{TYPE2} RDF_{FNNAME}_{TYPE2}({DTYPE} df, string col){\n    return df.{FNNAME}<{TYPE2}>(col).GetValue.\n}\n'


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

[Show source in ttree.py:22](../../rootloader/ttree.py#L22)

Extract ROOT.TTree with lazy operation. Looks like a dataframe in most ways

#### Arguments

- `tree` *str|hitstree* - tree to load
- `filter_string` *str|None* - if not none then pass this to [`RDataFrame.Filter`](https://root.cern/doc/master/classROOT_1_1RDF_1_1RInterface.html#ad6a94ba7e70fc8f6425a40a4057d40a0)
- `columns` *list|None* - list of column names to include in fetch, if None, get all

#### Signature

```python
class ttree(object):
    def __init__(self, tree, filter_string=None, columns=None): ...
```

### ttree.__getitem__

[Show source in ttree.py:90](../../rootloader/ttree.py#L90)

Fetch a new dataframe with fewer 'columns', as a memory view

#### Signature

```python
def __getitem__(self, key): ...
```

### ttree.columns

[Show source in ttree.py:345](../../rootloader/ttree.py#L345)

Return list of column (branch) names

#### Signature

```python
@property
def columns(self): ...
```

### ttree.filters

[Show source in ttree.py:349](../../rootloader/ttree.py#L349)

Return list of RDataFrame filters

#### Signature

```python
@property
def filters(self): ...
```

### ttree.hist1d

[Show source in ttree.py:139](../../rootloader/ttree.py#L139)

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

[Show source in ttree.py:192](../../rootloader/ttree.py#L192)

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

[Show source in ttree.py:353](../../rootloader/ttree.py#L353)

Return ttree of just the index data

#### Signature

```python
@property
def index(self): ...
```

### ttree.index_name

[Show source in ttree.py:357](../../rootloader/ttree.py#L357)

Return string of the name of the index branch

#### Signature

```python
@property
def index_name(self): ...
```

### ttree.loc

[Show source in ttree.py:361](../../rootloader/ttree.py#L361)

Return a ttree that can be indexed like a pandas dataframe

#### Signature

```python
@property
def loc(self): ...
```

### ttree.max

[Show source in ttree.py:402](../../rootloader/ttree.py#L402)

Return the max value of the tree, for each branch

#### Signature

```python
def max(self): ...
```

### ttree.mean

[Show source in ttree.py:405](../../rootloader/ttree.py#L405)

Return the mean value of the tree, for each branch

#### Signature

```python
def mean(self): ...
```

### ttree.min

[Show source in ttree.py:399](../../rootloader/ttree.py#L399)

Return the min value of the tree, for each branch

#### Signature

```python
def min(self): ...
```

### ttree.reset

[Show source in ttree.py:264](../../rootloader/ttree.py#L264)

Make a new tree

#### Signature

```python
def reset(self): ...
```

### ttree.reset_columns

[Show source in ttree.py:268](../../rootloader/ttree.py#L268)

Include all columns again

#### Signature

```python
def reset_columns(self): ...
```

### ttree.set_filter

[Show source in ttree.py:278](../../rootloader/ttree.py#L278)

Set a filter on the dataframe to select a subset of the data

#### Signature

```python
def set_filter(self, expression, inplace=False): ...
```

### ttree.set_index

[Show source in ttree.py:272](../../rootloader/ttree.py#L272)

Set the index column name

#### Signature

```python
def set_index(self, column): ...
```

### ttree.size

[Show source in ttree.py:365](../../rootloader/ttree.py#L365)

Return the number of rows in the ttree

#### Signature

```python
@property
def size(self): ...
```

### ttree.std

[Show source in ttree.py:411](../../rootloader/ttree.py#L411)

Return the standard deviationif the of values the tree, for each branch

#### Signature

```python
def std(self): ...
```

### ttree.sum

[Show source in ttree.py:408](../../rootloader/ttree.py#L408)

Return the sum of the values of the tree, for each branch

#### Signature

```python
def sum(self): ...
```

### ttree.to_array

[Show source in ttree.py:289](../../rootloader/ttree.py#L289)

Return ttree data as 1D or 2D numpy array (depending on number of columns)

#### Signature

```python
def to_array(self): ...
```

### ttree.to_dataframe

[Show source in ttree.py:300](../../rootloader/ttree.py#L300)

Return ttree data as pandas dataframe

#### Signature

```python
def to_dataframe(self): ...
```

### ttree.to_dict

[Show source in ttree.py:334](../../rootloader/ttree.py#L334)

Return ttree data as dict of numpy arrays

#### Signature

```python
def to_dict(self): ...
```

### ttree.values

[Show source in ttree.py:369](../../rootloader/ttree.py#L369)

Convert ttree 1D or 2D numpy array (depending on number of columns)

#### Signature

```python
@property
def values(self): ...
```