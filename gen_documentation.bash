#!/bin/bash
# generate documentation with working links
# Derek Fujimoto
# Nov 2024

# note: requires handsdown (https://github.com/vemel/handsdown)

# generate the documentation
# cd rootloader
handsdown -o docs --theme readthedocs

# fix the broken links
cd docs/rootloader
for file in *;
do
    if [ -f "$file" ];  then

        # replace bad empty parentheses
        sed -i 's/()././' $file

        # repace broken table of contents links
        name=$(basename $file .md)
        sed -i "s/#${name}()/#${name}/" $file
    fi
done