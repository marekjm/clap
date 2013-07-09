#!/usr/bin/env python3


from clap import formater, parser, errors, option


"""This is interface which enables use of modes.
It is basically a set of parsers from which one is chosen according
to the *mode-keyword* found in input list.

*mode-keyword* is first item in the list that does not look like option.
Example:

    foo bar --hello-world

Here, `bar` is mode of program `foo` called with option `--hello-world`.
A more sphisticated example could be:

    foo --verbose --log './foo.log' bar --hello-world

In this example a couple of options is passed before *mode-keyword* is found.
These are global options which are commin to all modes.

If using Modes() instead of simple Parser() remember to call `define()` method before
`check()` and `parse()`.
"""


class Modes():
    """Object implementing modes functionality.
    """
    def __init__(self, argv, default=''):
        self.argv = []
        self.modes = {'': parser.Parser()}
        self.mode = ''
        self.default = default
        self.parser = None
        self.feed(argv)

    def __contains__(self, option):
        """If you check whether Parser() contains an option or not, general one and every mode-parser
        is checked.
        """
        return option in self.parser

    def __str__(self):
        return self.mode

    def feed(self, argv):
        """Feeds input arguments list to parser.
        """
        self.argv = argv
        self.parser = None
        self.mode = ''

    def addOption(self, short='', long='', argument=None, required=False, not_with=[], conflicts=[], hint=''):
        """Adds an option to the list of options recognized by parser.
        Available types are: int, float and str.

        If you `addOption` it is added to the general parser and all mode-parsers so both following
        syntaxes are correct:
            
            foo --verbose print 'Hello World!'
            foo bar --verbose 'Hello World!'
        """
        new = option.Option(short=short, long=long, argument=argument, required=required, not_with=not_with, conflicts=conflicts, hint=hint)
        for name in self.modes: self.modes[name]._append(new)
        return new

    def addMode(self, name, parser):
        """Adds mode to Modes() or overwrites old definition.
        """
        self.modes[name] = parser

    def has(self, mode):
        """Returns True if Modes() has given mode.
        """
        return mode in self.modes

    def _modeindex(self):
        """Returns index of first non-option-like item in input list.
        Returns -1 if no mode is found.
        """
        index = -1
        for i, item in enumerate(self.argv):
            if not formater.lookslikeopt(item):
                index = i
                finish = True
                if i == 0: break
                else:
                    opt = self.argv[i-1]
                    for name in self.modes:
                        if self.modes[name].type(opt) is not None:
                            finish = False
                            break
                if finish: break
        return index

    def define(self):
        """Defines mode to use and sets correct parser.
        """
        index = self._modeindex()
        if index > -1:
            mode = self.argv[index]
            n = 1
        else:
            mode = self.default
            index = 0
            n = 0
        if mode not in self.modes: raise errors.UnrecognizedModeError(mode)
        self.parser = self.modes[mode]
        input = self.argv[:index] + self.argv[index+n:]
        self.parser.feed(input)
        self.mode = mode
        return mode

    def check(self):
        """Checks input list for errors.
        """
        self.parser.check()

    def parse(self):
        """Parses input list.
        """
        self.parser.parse()

    def get(self, s):
        """Returns option's argument.
        """
        return self.parser.get(s)

    def type(self, s):
        """Returns type of the option.
        """
        return self.parser.type(s)
