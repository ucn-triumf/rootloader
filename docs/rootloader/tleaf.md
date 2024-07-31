# tleaf

[Rootloader Index](../README.md#rootloader-index) / [Rootloader](./index.md#rootloader) / tleaf

> Auto-generated documentation for [rootloader.tleaf](../../rootloader/tleaf.py) module.

- [tleaf](#tleaf)
  - [tleaf](#tleaf-1)
    - [tleaf().branch](#tleaf()branch)
    - [tleaf().copy](#tleaf()copy)
    - [tleaf().fullname](#tleaf()fullname)
    - [tleaf().get_entry](#tleaf()get_entry)
    - [tleaf().leaftype](#tleaf()leaftype)
    - [tleaf().len](#tleaf()len)
    - [tleaf().name](#tleaf()name)
    - [tleaf().value](#tleaf()value)

## tleaf

[Show source in tleaf.py:7](../../rootloader/tleaf.py#L7)

Ease of access for ROOT.TLeaf

#### Arguments

- `leaf` *ROOT.TLeaf* - root leaf object

#### Signature

```python
class tleaf(object):
    def __init__(self, leaf): ...
```

### tleaf().branch

[Show source in tleaf.py:25](../../rootloader/tleaf.py#L25)

#### Signature

```python
@property
def branch(self): ...
```

### tleaf().copy

[Show source in tleaf.py:17](../../rootloader/tleaf.py#L17)

Make a copy of this object

#### Signature

```python
def copy(self): ...
```

### tleaf().fullname

[Show source in tleaf.py:27](../../rootloader/tleaf.py#L27)

#### Signature

```python
@property
def fullname(self): ...
```

### tleaf().get_entry

[Show source in tleaf.py:21](../../rootloader/tleaf.py#L21)

#### Signature

```python
def get_entry(self, i): ...
```

### tleaf().leaftype

[Show source in tleaf.py:31](../../rootloader/tleaf.py#L31)

#### Signature

```python
@property
def leaftype(self): ...
```

### tleaf().len

[Show source in tleaf.py:33](../../rootloader/tleaf.py#L33)

#### Signature

```python
@property
def len(self): ...
```

### tleaf().name

[Show source in tleaf.py:29](../../rootloader/tleaf.py#L29)

#### Signature

```python
@property
def name(self): ...
```

### tleaf().value

[Show source in tleaf.py:35](../../rootloader/tleaf.py#L35)

#### Signature

```python
@property
def value(self): ...
```