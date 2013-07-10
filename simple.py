#!/usr/bin/env python3

import clap
import sys


args = sys.argv[1:]

formater = clap.formater.Formater(args)
parser = clap.parser.Parser(list(formater))
parser.add(long='verbose', short='v', conflicts=['--quiet'])
parser.add(long='quiet', short='q', conflicts=['--verbose'])
parser.add(short='n', argument=int, requires=['--text'], hint='how many times to print given text')
parser.add(long='text', short='t', argument=str, hint='text to print')

try:
    parser.check()
except clap.errors.UnrecognizedOptionError as e:
    print('fatal: unrecognized option: {0}'.format(e))
    exit()
except clap.errors.RequiredOptionNotFoundError as e:
    print('fatal: required option not found: {0}'.format(e))
    exit()
except clap.errors.MissingArgumentError as e:
    print('fatal: missing argument for option: {0}'.format(e))
    exit()

parser.parse()

if '-n' in parser: n = parser.get('-n')
else: n = 1

if '--quiet' not in parser and '--text' in parser:
    for i in range(n): print(parser.get('--text'))
if '--verbose' in parser and '--quiet' not in parser: print('What a nice day we have today.')
