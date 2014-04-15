#!/usr/bin/env python3


import random
import sys

import clap


f = clap.formater.Formater(sys.argv[1:])
f.format()

builder = clap.builder.Builder('./modes-parser-example.json', argv=list(f))
builder.build()

ui = builder.get()

print('checking...', end='\t')
try:
    ui.check()
    print('[  OK  ]')
except Exception as e:
    exit('[ FAIL: {0}: {1} ]'.format(str(type(e))[8:-2], e))
print('parsing...', end='\t')
ui.parse()
print('[  OK  ]')

print('ui.mode:', ui.mode)
print('ui.arguments:', ui.arguments)
print('ui.parsed:', ui.parsed)


print('\n----\n')


if '--version' in ui:
    print(clap.__version__)
    exit()

if str(ui) == 'print':
    if '--string' in ui: something = ui.get('-s')
    if '--integer' in ui: something = ui.get('-i')
    if '--float' in ui: something = ui.get('-f')

    if '--times' in ui: n = ui.get('-t')
    else: n = 1

    for i in range(n): print(something)
if str(ui) == 'stuff': pass
