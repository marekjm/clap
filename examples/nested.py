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
command = clap.builder.Builder(model).insertHelpCommand().build().get()
parser = clap.parser.Parser(command).feed(args)
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

if clap.helper.HelpRunner(ui=ui, program=filename).adjust(options=['-h', '--help']).run().displayed(): exit(0)
