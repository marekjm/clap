#!/usr/bin/env python3


from clap import formater, errors


"""This module contains Parser() object.
"""


class Parser():
    """Used for parsing options.
    """
    argv = []
    options = []
    parsed = {}
    arguments = []

    def __init__(self, argv=[]):
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

    def add(self, short='', long='', type=None, hint=''):
        """Adds an option to the list of options recognized by parser.
        Available types are: int, float and str.

        :returns: dict of new option
        """
        if not (short or long): raise TypeError('neither `short` nor `long` was specified')
        if short: short = '-{}'.format(short)
        if long: long = '--{}'.format(long)
        new = {'short': short,
               'long': long,
               'type': type,
               'hint': hint
               }
        self.options.append(new)
        return new

    def remove(self, short='', long=''):
        """Removes option from the list.

        :returns: non-negative integer indicates that some option was removed
        """
        index = -1
        short = '-{}'.format(short)
        long = '--{}'.format(long)
        for i, opt in enumerate(self.options):
            if short == opt['short']: index = i
            if long == opt['long']: index = i
            if index > -1: break
        if index: self.options.pop(index)
        return index

    def accepts(self, option):
        """Returns True if Parser() accepts this option.
        """
        result = False
        for i in self.options:
            if option == i['short'] or option == i['long']:
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

    def type(self, option):
        """Returns type of given option.
        None indicates that option takes no additional argument.
        """
        for o in self.options:
            if option == o['short'] or option == o['long']:
                opt_type = o['type']
                break
        return opt_type

    def check(self):
        """Checks if Parser() contains any unrecognized options.
        """
        for i in self.argv:
            if i == '--': break
            if formater.lookslikeopt(i) and not self.accepts(i):
                raise errors.UnrecognizedOptionError(i)

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
                try:
                    arg = self.type(string)(self.argv[i])
                except ValueError:
                    raise ValueError('invalid argument for option \'{0}\': expected {1} but got: {2}'
                                     .format(string, self.type(string), self.argv[i]))
            parsed[string] = arg
            if self.alias(string): parsed[self.alias(string)] = arg
            i += 1
        self.parsed = parsed
        self.arguments = self.argv[i:]

    def get(self, key):
        """Returns option value.
        Returns None if given option does not need an argument.
        """
        if type(key) is None and key in self: value = None
        else: value = self.parsed[key]
        return value
