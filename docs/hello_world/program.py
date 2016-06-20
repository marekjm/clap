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

# This will create the top-most "command" of the program, that will later be
# matched to the input by the RedCLAP parser.
command = clap.builder.Builder(model).build().get()

# Create the parser that will analyse user input according to the command
# built in previous line.
# Immediately feed processed arguments to the parser.
parser = clap.parser.Parser(command).feed(args)

# Create a checker object that will check if the input matches the command.
# This requires already parser to be already fed with arguments (which we
# did when creating the parser).
# Splitting the responsibilities of validating and parsing input between two
# classes allows both of them to be simpler, and easier to extend and maintain.
# Checker's only job is to check if the input is valid, and parser's only job
# is to extract information from valid input.
# The fact that Parser can safely assume that the input is always valid greatly
# simplifies the code.
checker = clap.checker.RedChecker(parser)

try:
    # This may throw many different exceptions.
    # Each exception type conveys a precise message as to which part of the
    # input is not valid, so that the error can be presented to the user to
    # be corrected.
    fail = True
    checker.check()
    fail = False
except clap.errors.UnrecognizedOptionError as e:
    # This exception is raised when an unreconised option is passed to the UI.
    # It is triggered when a string that is looking like an option is given as
    # one of the command line arguments, but can't be matched to any valid option.
    print('unrecognized option found: {0}'.format(e))
except clap.errors.UIDesignError as e:
    # This exception is raised when RedCLAP detects a badly designed user interface.
    # There are several reasons for that, e.g. an option requires an unrecognised option
    # to be passed with it, an option conflicts with another option that requires it, etc.
    print('misdesigned interface: {0}'.format(e))
finally:
    if fail: exit(1)
    # Finally, if the input has been deemed valid, parse the command line
    # arguments and return a UI object that can be used later in code
    # to extract information about passed operands, options, and subcommands.
    ui = parser.parse().ui().finalise()


# The `X in Y` notation is used to check if an option was given to a command.
# Both short and long version may be checked, no matter which version of an
# option has actually been passed on the command line.
#
# Try running the program as:
#
#   python program.py
#   python program.py --verbose
#   python program.py -v
#
# to see the difference in results.
# The last two lines will be the same, the first will display just "Hello World!".
print(('Hello command line World!' if '--verbose' in ui else 'Hello World!'))
