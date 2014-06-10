#!/usr/bin/bash

   
if [ ${EUID} == 0 ]; then
    echo "Installing CLAP..."
else
    echo "fail: you must be root to do this!"
    exit 1
fi


if [ $1 == '']; then
    echo "fail: you have to give Python version (eg. 3.3 for python 3.3) as an argument."
else
    make tests
    make clean
    cp -Rv ./redclap/ /usr/lib/python$1/site-packages/
fi
