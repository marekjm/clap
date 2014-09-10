#!/usr/bin/env python3

import json
import os
import sys

sys.path.insert(0, os.getcwd())

import clap

argv = sys.argv[:]

base, filename = os.path.split(argv.pop(0))
filename_ui = os.path.splitext(filename)[0] + '.json'

ifstream = open(os.path.join(base, filename_ui), 'r')
model = json.loads(ifstream.read())
ifstream.close()

args = list(clap.formatter.Formatter(argv).format())
mode = clap.builder.Builder(model).build().get()
parser = clap.parser.Parser(mode).feed(args)
checker = clap.checker.RedChecker(parser)


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
except clap.errors.UIDesignError as e:
    print('UI has design error: {0}'.format(e))
    fail = True
except Exception as e:
    print('fatal: unhandled exception: {0}'.format(e))
    fail = True
finally:
    if fail: exit()
    else: ui = parser.parse().ui().finalise()


if '--version' in ui:
    print('using clap (RedCLAP) version {0}'.format(clap.__version__))
    exit()

if '--help' in ui:
    helper = clap.helper.Helper(filename, mode)
    print(helper.full(deep=('--verbose' in ui)).render())
    exit(0)

if '--echo' in ui:
    print(ui.get('-e'))
    for msg in ui.get('-e'):
        print(msg[0])
