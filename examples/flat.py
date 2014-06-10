#!/usr/bin/env python3

import json
import os

from sys import argv

import redclap as clap

base, filename = os.path.split(argv.pop(0))
filename_ui = os.path.splitext(filename)[0] + '.json'

ifstream = open(os.path.join(base, filename_ui), 'r')
model = json.loads(ifstream.read())
ifstream.close()

args = list(clap.formatter.Formatter(argv).format())
mode = clap.builder.Builder(model).build().get()
parser = clap.parser.Parser(mode).feed(args)
checker = clap.checker.RedChecker(parser)

print(argv, '->', args)
print(base, filename)
print(base, filename_ui)

try:
    checker.check()
    fail = False
except clap.errors.MissingArgumentError as e:
    print('missing argument for option: {0}'.format(e))
    fail = True
except clap.errors.UnrecognizedOptionError as e:
    print('unrecognized option found: {0}'.format(e))
    fail = True
except clap.errors.ConflictingOptionsError as e:
    print('conflicting options found: {0}'.format(e))
    fail = True
except clap.errors.RequiredOptionNotFoundError as e:
    fail = True
    print('required option not found: {0}'.format(e))
except clap.errors.InvalidOperandRangeError as e:
    print('invalid number of operands: {0}'.format(e))
    fail = True
except Exception as e:
    fail = True
    raise e
finally:
    if fail: exit()
    else: ui = parser.parse().ui().finalise()


if '--echo' in ui:
    print(ui.get('-e'))
    for msg in ui.get('-e'):
        print(msg[0])