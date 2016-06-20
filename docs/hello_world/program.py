#!/usr/bin/env python3

import json
import sys

import clap

# Empty model of the interface.
# It will later be loaded from the "ui.json" file.
# RedCLAP requires an interface model to analyze the
# command line input from the user.
model = {}

with open('./ui.json', 'r') as ifstream: model = json.loads(ifstream.read())


# Normalise command line arguments, preparing them for further processing.
# This command analyses the input without knowledge of the actual model and
# only according to "core guidelines" of how the CLI should behave, e.g.
# `-bar` can be split into `-b -a -r`, or
# `--with=spam` should be written as `--with spam`.
#
# Remember to remove the program name from formatter input!
args = list(clap.formatter.Formatter(sys.argv[1:]).format())

# Uncomment the print() line and try running the program with the following
# command lines to see how the formatter cuts the input up:
#
#   --foo
#   -bar
#   --foo -bar
#   --foo -bar --with=spam
#   -bar -- -xyz
#   -bar --with="spam ham"
#   -- --with="spam"
#print('original: ', sys.argv[1:])
#print('formatted:', args)
