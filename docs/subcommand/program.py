#!/usr/bin/env python3

import json
import sys

import clap

model = {}
with open('./ui.json', 'r') as ifstream: model = json.loads(ifstream.read())


args = list(clap.formatter.Formatter(sys.argv[1:]).format())

command = clap.builder.Builder(model).build().get()
parser = clap.parser.Parser(command).feed(args)
checker = clap.checker.RedChecker(parser)

try:
    fail = True
    checker.check()
    fail = False
except clap.errors.UnrecognizedOptionError as e:
    print('unrecognized option found: {0}'.format(e))
except clap.errors.UIDesignError as e:
    print('misdesigned interface: {0}'.format(e))
except clap.errors.MissingArgumentError as e:
    print('missing argument to an option: {}'.format(e))
except clap.errors.ConflictingOptionsError as e:
    print('conflicting options given: {}'.format(e))
except clap.errors.InvalidOperandRangeError as e:
    print('invalid number of operands: {}'.format(e))
except clap.errors.InvalidArgumentTypeError as e:
    print('invalid option argument: {}'.format(e))
except clap.errors.UnrecognizedCommandError as e:
    # This exception is raised when RedCLAP detects that an unrecognised subcommand
    # has been requested.
    # This is done using very simple heuristics: if there is a string that is not a
    # recognised subcommand followed by a string that is a recognised option in any
    # subcommand the exception is raised.
    #
    # Try running the program with following command lines to get a grasp of it:
    #
    #   python program.py spam
    #   python program.py spam -f   # -f is an option in foo
    #   python program.py spam -b   # -b is an option in bar
    print('unrecognised command: {}'.format(e))
except Exception as e:
    print('unhandled exception: {0}: {1}'.format(type(e), e))
finally:
    if fail: exit(1)
    ui = parser.parse().ui().finalise()

# The `.down()` subcommand descends one subcommand down the chain.
# It is usually the first method executed in any program.
# Calling `.down()` when there are no commands left returns the last command
# once again.
# So here it will return the main command if no subcommand was passed.
ui = ui.down()

# Name of the subcommand is accessed by stringifying the ui object.
if str(ui) == '':
    # The `--verbose` is a global option so can be accessed in the command it was defined in, and
    # in any later subcommands.
    print('OH NOES!' if '--verbose' in ui else 'Oh.')
elif str(ui) == 'foo':
    # The `--verbose` option is avilable here.
    # It may be passed either as:
    #
    #   python program.py --verbose foo
    #
    # or as:
    #
    #   python program.py foo --verbose
    #
    # due to the fact that it is global.
    print('You {}fool!'.format('bloody ' if '--verbose' in ui else ''))
elif str(ui) == 'bar':
    # We have to descend here, since yet another subcommand may have been passed.
    ui = ui.down()
    if str(ui) == 'bar':
        # Still in "bar" command.
        print('Go to a {}bar!'.format('good ' if '--verbose' in ui else ''))
    elif str(ui) == 'baz':
        # A more nested subcommand was passed.
        # The `--verbose` option is still available.
        print('Go home, you{} drunk!'.format(' are' if '--verbose' in ui else '\'re'))
