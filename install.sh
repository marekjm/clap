#!/usr/bin/bash

   
if [ ${EUID} == 0 ]; then
    echo "Installing CLAP..."
else
    echo "You must be root to do this!"
    exit 1
fi


if [ $1 == '']; then
    echo "You have to give Python version (eg. 3.3 for python 3.3) as an argument."
else
    cp -Rv ./clap/ /usr/lib/python$1/site-packages/
fi
