# ROOTLOADER

Parse simple root files into memory as dictionaries or purpose-built objects. Convert objects into pandas DataFrames for ease of processing.

## Installation

Requires ROOT with pyroot installed.

Clone this repository and install

```bash
git clone git@github.com:ucn-triumf/rootloader.git
cd rootloader
pip install .
```

You will need to re-run the last line of the above upon every pull, unless you add the `-e` flag like this: `pip install -e .`
Note that this may not work on all systems, particularly windows systems.

## Documentation

[See here](docs/README.md).

## Example

```python
from rootloader import tfile

# read file
fid = tfile('myfile.root')

# key values can be accessed as attributes or as keys
# say there's a tree named "tree1". We can access it as
tr = fid.tree1

# or
tr = fid['tree1']

# get a pandas dataframe from the tree (the tree is left unaltered)
df = tr.to_dataframe()

# try to convert all file contents to pandas dataframes, and replace keys with these dataframes
fid.to_dataframe()
```