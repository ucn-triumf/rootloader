# th2

[Rootloader Index](../README.md#rootloader-index) / [Rootloader](./index.md#rootloader) / th2

> Auto-generated documentation for [rootloader.th2](../../rootloader/th2.py) module.

- [th2](#th2)
  - [th2](#th2-1)
    - [th2.copy](#th2copy)
    - [th2.plot](#th2plot)
    - [th2.to_dataframe](#th2to_dataframe)

## th2

[Show source in th2.py:9](../../rootloader/th2.py#L9)

Extract histogram data from ROOT.TH2 data type

#### Arguments

- `hist` *ROOT.TH2* - histogram to import

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
class th2(object):
    def __init__(self, hist=None): ...
```

### th2.copy

[Show source in th2.py:98](../../rootloader/th2.py#L98)

Produce a copy of this object

#### Signature

```python
def copy(self): ...
```

### th2.plot

[Show source in th2.py:108](../../rootloader/th2.py#L108)

Draw the histogram

#### Arguments

- `ax` *plt.Axes* - if None, draw in current axes, else draw on ax
- `flat` *bool* - if True, draw 2D, else 3D
- `kwargs` - if flat: passed to ax.pcolormesh
        - `else` - passed to ax.plot_surface

#### Signature

```python
def plot(self, ax=None, flat=True, **kwargs): ...
```

### th2.to_dataframe

[Show source in th2.py:159](../../rootloader/th2.py#L159)

Convert tree to pandas dataframe

#### Returns

pd.DataFrame

#### Signature

```python
def to_dataframe(self): ...
```