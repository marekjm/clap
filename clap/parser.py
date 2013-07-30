#!/usr/bin/env python3


from clap import base, option, errors


"""This module contains Parser() object.
"""


class Parser(base.Base):
    """Used for parsing options.
    """
    def __init__(self, argv=[]):
        self.argv = []
        self.options = []
        self.parsed = {}
        self.arguments = []
        self.feed(argv)

    def __contains__(self, option):
        """Returns True if Parser() contains given option as parsed.
        Remeber to parse() the input before you will use this feature.
        """
        return option in self.parsed

    def feed(self, argv):
        """Feeds input arguments list to parser.
        Feeding new data to Parser() resets `parsed` and
        `arguments` variables.
        """
        self.argv = argv
        self.parsed = {}
        self.arguments = []

    def _append(self, option):
        """Appends `Option()` object to options list.
        """
        self.options.append(option)

    def add(self, short='', long='', argument=None, requires=[], needs=[], required=False, not_with=[], conflicts=[]):
        """Adds an option to the list of options recognized by parser.
        Available types are: int, float and str.

        :param short: short, one character name for the option
        :type short: str
        :param long: long multiple-character name for option
        :type short: str
        :param type: type of argument for the option
        :type type: str, int, float
        :param required: whether this option is required or not
        :type required: bool
        :param not_with: list of options with which this option is not required (give only with `required`)
        :param not_with: list[str]
        :param conflicts: list of options with which this option must not be passed
        :type conflicts: list[str]
        :param hint: hint for the option
        :type short: str

        :returns: clap.option.Option
        """
        new = option.Option(short=short, long=long, argument=argument,
                            requires=requires, needs=needs,
                            required=required, not_with=not_with,
                            conflicts=conflicts)
        self._append(new)
        return new

    def remove(self, short='', long=''):
        """Removes option from the list.

        :returns: non-negative integer indicates that some option was removed
        """
        index = -1
        for i, opt in enumerate(self.options):
            if opt.match(short) or opt.match(long): index = i
            if index > -1: break
        if index: self.options.pop(index)
        return index

    def accepts(self, option):
        """Returns True if Parser() accepts this option.
        """
        result = False
        for i in self.options:
            if i.match(option):
                result = True
                break
        return result

    def alias(self, option):
        """Returns alias string for given option.
        Returns empty string if no alias exist.
        """
        alias = ''
        for i in self.options:
            if option == i['short']:
                alias = i['long']
                break
            if option == i['long']:
                alias = i['short']
                break
        return alias

    def gethint(self, option):
        """Returns hint for given option.
        """
        for o in self.options:
            if o.match(option):
                hint = o['hint']
                break
        return hint

    def check(self):
        """Checks if input list is valid for this instance of Parser().
        Run before `parse()` to check for errors in input list.
        """
        checker.Checher(self).check()

    def parse(self):
        """Parses input.
        """
        parsed = {}
        i = 0
        while i < len(self.argv):
            string = self.argv[i]
            arg = None
            if not self.accepts(string) or string == '--':
                break
            if self.type(string) is not None:
                i += 1
                arg = self.type(string)(self.argv[i])
            parsed[string] = arg
            if self.alias(string): parsed[self.alias(string)] = arg
            i += 1
        self.parsed = parsed
        self.arguments = self.argv[i:]

    def get(self, key):
        """Returns option value.
        Returns None if given option does not need an argument.
        """
        return self.parsed[key]
