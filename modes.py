#!/usr/bin/env python3


import sys
import re
import clap


__help__ = """Help for modescheck.py

This is script explaining usage of Modes from the `clap` library.

SYNTAX:
    python modescheck.py [OPTIONS] [MODE] [MODE-OPTIONS]

OPTIONS:
    -v, --verbose       - be verbose
    -h, --help          - display this help
    -L, --log           - log file


MODEs:
    echo                - print text on screen
    blank               - do nothing


MODE-OPTIONS:
    echo:
    -t, --text TEXT     - text to print
    -n, --number INT    - how many times the text should be printed


    calc:
    -e STR              - expression to calculate


    blank:
    'blank' mode has no options.



This is reference software and does not serve any purpose.
It is published under GNU GPL 3+ license.

Copyright Marek Marecki (c) 2013"""


formater = clap.formater.Formater(sys.argv[1:])
formater.format()


echo = clap.parser.Parser()
blank = clap.parser.Parser()
calc = clap.parser.Parser()

echo.add(short='t', long='text', argument=str, required=True, not_with=['-h'])
echo.add(short='n', long='number', argument=int)

calc.add(short='e', argument=str, required=True)


options = clap.modes.Modes(list(formater), default='blank')
options.addMode('echo', echo)
options.addMode('blank', blank)
options.addMode('calc', calc)
options.addOption(short='h', long='help')
options.addOption(short='v', long='verbose', conflicts=['--quiet'])
options.addOption(short='q', long='quiet', conflicts=['--verbose'])
options.addOption(short='L', long='log', argument=str)
options.addOption(long='bar', requires=['--foo'])
options.addOption(long='foo', requires=['--bar'], argument=str)


try:
    options.define()
    options.check()
except clap.errors.UnrecognizedOptionError as e:
    print('modescheck: fatal: unrecognized option: {0}'.format(e))
    exit()
except clap.errors.UnrecognizedModeError as e:
    print('modescheck: fatal: unrecognized mode: {0}'.format(e))
    exit()
except clap.errors.MissingArgumentError as e:
    print('modescheck: fatal: missing argument for option: {0}'.format(e))
    exit()
except clap.errors.InvalidArgumentTypeError as e:
    print('modescheck: fatal: invalid argument for option: {0}'.format(e))
    exit()
except clap.errors.ConflictingOptionsError as e:
    print('modescheck: fatal: conflicting options: {0}'.format(e))
    exit()
except clap.errors.RequiredOptionNotFoundError as e:
    print('modescheck: fatal: required option not found: {0}'.format(e))
    exit()

options.parse()

#### Finished parsing options


#### Here begins program's code

def calc(s):
    safe = re.compile('^[0-9.()*/+ -]+$')
    if re.match(safe, s) is None: return 0
    else: return eval(s)


message = ''
if str(options) == 'echo' and '--help' not in options:
    message = options.get('--text')
    if '--verbose' in options: message += '\nHey! I am verbose! See?'
elif str(options) == 'calc' and '--help' not in options:
    message = calc(options.get('-e'))

if '--help' in options:
    message = __help__


if '--log' in options:
    if '--verbose' in options: print('Output logged to {0}'.format(options.get('--log')))
    log = open(options.get('--log'), 'a')
    log.write(message)
    log.write('\n')
    log.write('-'*16)
    log.write('\n')
    log.close()
else:
    if message: print(message)
