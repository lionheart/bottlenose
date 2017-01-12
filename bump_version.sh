#!/bin/bash

if [ "$1" != "" ]; then
  sed -i "" "s/\(__version__[ ]*=\).*/\1 \"$1\"/g" bottlenose/metadata.py
  git add .
  git commit -m "bump version to $1"
  git tag $1
  git push origin master
  git push --tags
  make
fi
