#!/usr/bin/env python3

import json
import os

from sys import argv

import clap

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
    err = None
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
    print('fatal: unhandled exception: {0}: {1}'.format(str(type(e))[8:-2], e))
    fail, err = True, e
finally:
    if fail:
        if err is not None: raise err
        else: exit()
    else: ui = parser.parse().ui().finalise()


if '--version' in ui:
    print('using clap (RedCLAP) version {0}'.format(clap.__version__))
    exit()

cui = ui
while True:
    if '--help' in cui:
        helper = clap.helper.Helper(filename, cui._mode).setmaxlen(n=70)
        if cui.up() is cui:
            helper.addUsage('--help')
            helper.addUsage('--version')
            helper.addUsage('--ok [opts...]')
            helper.addUsage('--ok [--verbose | --quiet] [opts...]')
        print(helper.gen(deep=('--verbose' in cui)).render())
        if '--verbose' not in cui: print('\nRun "{0} --help --verbose" to see full help message'.format(filename))
        exit(0)
    if cui.islast(): break
    cui = cui.down()
