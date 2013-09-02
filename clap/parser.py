#!/usr/bin/env python3


from clap import base, checker


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

    def check(self):
        """Checks if input list is valid for this instance of Parser().
        Run before `parse()` to check for errors in input list.
        """
        checker.Checker(self).check()

    def parse(self):
        """Parses input:
        * assigns option-arguments to the options requesting them,
        * separets options from operands,
        """
        parsed = {}
        i = 0
        input = self._getinput()
        while i < len(input):
            string = input[i]
            if self.type(string):
                arg = []
                for atype in self.type(string):
                    i += 1
                    arg.append(atype(input[i]))
            else:
                arg = []
            arg = tuple(arg)
            parsed[string] = arg
            if self.alias(string): parsed[self.alias(string)] = arg
            i += 1
        self.parsed = parsed
        self.arguments = self._getarguments()

    def get(self, key):
        """Returns None if given option does not request an argument.
        Returns tuple if option requests more than one argument.
        For programmers' convinience, returns object of given type if
        option requests one argument.
        """
        value = self.parsed[key]
        if len(value) == 0: value = None
        elif len(value) == 1: value = value[0]
        return value
