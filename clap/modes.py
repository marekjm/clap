#!/usr/bin/env python3


from clap import base, parser, errors, option


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


class Parser():
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

    @property
    def arguments(self):
        return self.parser.arguments

    def feed(self, argv):
        """Feeds input arguments list to parser.
        """
        self.argv = argv
        self.parser = None
        self.mode = ''

    def addOption(self, short='', long='', argument=None, requires=[], needs=[], required=False, not_with=[], conflicts=[]):
        """Adds an option to the list of options recognized by parser.
        Available types are: int, float and str.

        If you `addOption` it is added to the general parser and all mode-parsers.
        """
        new = option.Option(short=short, long=long, argument=argument,
                            requires=requires, needs=needs,
                            required=required, not_with=not_with,
                            conflicts=conflicts)
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
        Returns -1 if no mode is found (all input was scanned or `--` was
        found).
        """
        index = -1
        for i, item in enumerate(self.argv):
            if item == '--': break
            if not base.lookslikeopt(item):
                if i == 0 or self.type(self.argv[i-1]) is None: index = i
                if index > -1: break
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
        If mode is defined use self.parser.
        If not, interate over all modes and return first non-None
        type found.
        """
        t = None
        if self.parser: t = self.parser.type(s)
        else:
            for m in self.modes:
                for o in self.modes[m].options:
                    t = self.modes[m].type(s)
                    if t is not None: break
                if t is not None: break
        return t
