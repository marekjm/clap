#!/usr/bin/env python3

import clap

import sys

b = clap.builder.Builder('./help.json')
#b.build(parser=True)
b.build()
ui = b.get()

helper = clap.helper.Helper(ui)
for l in helper.help(lines=True):
    print('    ' + l)
