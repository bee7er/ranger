#!/bin/bash

echo "Running copy from Code repository to Cinema 4D R20 runtime instance"

rsync -av /Users/brianetheridge/Code/ranger/ranger_plugin "/Users/brianetheridge/Library/Preferences/MAXON/Cinema 4D R20_7DE41E5A/plugins"

echo "Done"
