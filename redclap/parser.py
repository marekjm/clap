#!/usr/bin/env python3

"""This module contains command line arguments parser which is the object needed to
actually convert input given to the program by the user to a usable form.
"""


from . import base, shared, option, checker


class Parser():
    """Object implementing modes functionality.
    """
    def __init__(self, argv=[], default=''):
        self._argv = argv
        self._modes = {'': base.Base()}
        self._mode = ''
        self._default = default
        self._parser = None
        self._operands = []

    def __contains__(self, option):
        """If you check whether Parser() contains an option or not, general one and every mode-parser
        is checked.
        """
        return option in self.parser

    def __str__(self):
        return self.mode

    def __eq__(self, sth):
        """Checks if given sth (something) is equal to current instance of parser.
        If two parsers are compared and they support the same set of modes and options but got different
        list of arguments you can experience two situations:

            0.  they will equal each other if not finalized,
            1.  they will not equal each other if finalized,

        This, possibly confusing, result is given because list of given arguments are not under control
        of the programmer, change very often and are given  by user.

        Here, we compare parsers from the functionality point of view and
        we don't care what user might have given to the parser before it's finalized - after the
        parser if finalized it's functionality is different.
        """
        default = self._default == sth._default
        parser = self._parser == sth._parser
        operands = self._operands == sth._operands
        modes = True
        for name in self._modes:
            modes = self._modes[name] == sth._modes[name]
            if not modes: break
        return default and parser and operands and modes

    def feed(self, argv):
        """Feeds input arguments list to parser.
        """
        self._argv = argv
        self.parser = None
        self.mode = ''

    def _append(self, option, local=False):
        """Appends option to sub-parsers.
        """
        if local:
            self._modes['']._append(option)
        else:
            for name in self._modes: self._modes[name]._append(option)

    def addOption(self, short='', long='', help='', arguments=[],
                  requires=[], wants=[],
                  required=False, not_with=[],
                  conflicts=[], local=False):
        """Adds an option to the list of options recognized by parser.
        Available types are: int, float and str.

        If you `addOption` it is added to the general parser and all mode-parsers unless
        `local` is passed.
        """
        new = option.Option(short=short, long=long, help='', arguments=arguments,
                            requires=requires, wants=wants,
                            required=required, not_with=not_with,
                            conflicts=conflicts)
        self._append(new, local)
        return self

    def addMode(self, name, parser):
        """Adds mode to Modes() or overwrites old definition.
        """
        self._modes[name] = parser

    def has(self, mode):
        """Returns True if Modes() has given mode.
        """
        return mode in self.modes

    def _modeindex(self):
        """Returns index of first non-option-like item in input list.
        Returns -1 if no mode was found but all input was scanned.

        Quits searching as soon as `--` breaker is found.
        """
        index, i = -1, 0
        while i < len(self._argv):
            item = self._argv[i]
            if item == '--': break
            if shared.lookslikeopt(item):
                # if item is an option get list of all its arguments and
                # increase the counter accordingly;
                # needed for support for options with multiple arguments because
                # otherwise _modeindex() would treat second argument as a mode
                args = self.type(item)
                if args is not None: n = len(self.type(item))
                else: n = 0
                i += n
            if not shared.lookslikeopt(item):
                if i == 0 or not self.type(self._argv[i-1]): index = i
                if index > -1: break
            i += 1
        return index

    def define(self):
        """Defines mode to use and sets correct parser.
        """
        index = self._modeindex()
        if index > -1:
            mode = self._argv[index]
            n = 1
        else:
            mode = self._default
            index = 0
            n = 0
        if mode not in self._modes: raise errors.UnrecognizedModeError(mode)
        self._parser = self._modes[mode]
        input = self._argv[:index] + self._argv[index+n:]
        self._parser.feed(input)
        self.mode = mode
        return mode

    def check(self):
        """Checks input list for errors.
        """
        self.define()
        self._parser.check()

    def parse(self):
        """Parses input list.
        """
        self._parser.parse()

    def finalize(self):
        """Commits all actions required to get a usable parser.
        """
        self.define()
        self.parse()
        return self

    def get(self, s):
        """Returns option's argument.
        """
        return self._parser.get(s)

    def getoperands(self):
        """Returns operands passed to the program.
        """
        return self._parser.getoperands()

    def getopts(self):
        """Returns list of options supported by this parser.
        """
        return self._parser.getopts()

    def type(self, s):
        """Returns information about type(s) given option takes as its arguments.
        """
        t = None
        if self._parser: t = self._parser.type(s)
        else:
            for m in self._modes:
                for o in self._modes[m]._options:
                    t = self._modes[m].type(s)
                    if t is not None: break
                if t is not None: break
        return t
