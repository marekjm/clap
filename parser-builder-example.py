#!/usr/bin/env python3

import os
import sys

import clap


f = clap.formater.Formater(sys.argv[1:])    # create Formater object
f.format()                                  # format input

try:
    # create builder form given file and add formated input to it
    builder = clap.builder.Builder('./parser-example.json', argv=list(f))
except ValueError as e:
    exit('fatal: malformed ui file: {0}'.format(e))

builder.build()     # build the interface

ui = builder.get()  # get built interface
print('ui.argv:', ui.argv)
ui.check()          # check for conflicts, mistyped arguments, missing but required options etc.
ui.parse()          # parse the input if everything is OK


if '--integer' in ui and '-p' not in ui:
    n = ui.get('--integer')
    print('{0} + 2 = {1}'.format(n, n+2))

if '--float' in ui and '-p' not in ui:
    n = ui.get('--float')
    print('{0} + 3.14 = {1}'.format(n, n+3.14))

if '--string' in ui and '-p' not in ui:
    print(ui.get('--string'))


if '--print' in ui:
    if '--integer' in ui: n = ui.get('--integer')
    else: n = int(ui.get('--float'))
    text = ui.get('--string')
    for i in range(n): print(i, text)
