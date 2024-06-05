# th1

[Rootloader Index](../README.md#rootloader-index) / [Rootloader](./index.md#rootloader) / th1

> Auto-generated documentation for [rootloader.th1](../../rootloader/th1.py) module.

- [th1](#th1)
  - [th1](#th1-1)
    - [th1().draw](#th1()draw)
    - [th1().to_dataframe](#th1()to_dataframe)

## th1

[Show source in th1.py:9](../../rootloader/th1.py#L9)

Extract histogram data from ROOT.TH1 data type

#### Attributes

- `bbase_class` *str* - output of TH1.Class_Name()
- `entries` *int* - output of TH1.GetEntries()
- `name` *str* - output of TH1.GetName()
- `nbins` *int* - output of TH1.GetNbinsX()
- `sum` *float* - output of TH1.GetSum()
- `title` *str* - output of TH1.GetTitle()
- `xlabel` *str* - output of TH1.GetXaxis.GetName()
- `ylabel` *str* - output of TH1.GetYaxis.GetName()

- `x` *np.array* - bin centers
- `y` *np.array* - bin content
- `dy` *np.array* - bin error

#### Signature

```python
class th1(object):
    def __init__(self, hist): ...
```

### th1().draw

[Show source in th1.py:65](../../rootloader/th1.py#L65)

Draw the histogram

#### Arguments

- `ax` *plt.Axes* - if None, draw in current axes, else draw on ax
- `kwargs` - passed to matplotlib.pyplot.errorbar

#### Signature

```python
def draw(self, ax=None, **kwargs): ...
```

### th1().to_dataframe

[Show source in th1.py:85](../../rootloader/th1.py#L85)

Convert tree to pandas dataframe

#### Returns

pd.DataFrame

#### Signature

```python
def to_dataframe(self): ...
```