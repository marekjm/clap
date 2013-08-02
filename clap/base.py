#!/usr/bin/env python3


"""Functions, routines and regular expressions shared between CLAP modules.
"""


import re
import warnings

from clap import option


longopt_base = '--[a-zA-Z]+[a-zA-Z0-9]+(-[a-zA-Z0-9]+)*'

shortopt_regexp = re.compile('^-[a-zA-Z0-9]$')
longopt_regexp = re.compile('^' + longopt_base + '$')
longopt_with_equal_sign_regexp = re.compile('^' + longopt_base + '=.*$')
connected_shorts_regexp = re.compile('^-[a-zA-Z0-9][a-zA-Z0-9]+$')


def lookslikeopt(s):
    """Returns True if given string looks like option.
    """
    return bool(re.match(longopt_regexp, s) or
                re.match(longopt_with_equal_sign_regexp, s) or
                re.match(connected_shorts_regexp, s) or
                re.match(shortopt_regexp, s)
                )


class Base():
    """Base class for option and checker.
    """
    def __init__(self, argv=[]):
        self.argv = []
        self.options = []
        if argv: self._feed(argv)

    def __contains__(self, option):
        """Checks if Base contains given option object.
        """
        return option in self.options

    def _feed(self, argv):
        """Feeds list of input arguments to Base object.
        """
        self.argv = argv

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
            if opt.match(short) or opt.match(long):
                index = i
                break
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

    def type(self, name):
        """Returns type of given option.
        None indicates that option takes no additional argument.
        """
        t = None
        for o in self.options:
            if o.match(name):
                t = o.type()
                break
        return t

    def alias(self, name):
        """Returns alias string for given option.
        Returns empty string if no alias exist.
        """
        alias = ''
        for i in self.options:
            if i.match(name):
                alias = i._alias(name)
                break
        return alias

    def _getinput(self):
        """Returns list of options and arguments until '--' string or
        first non-option and non-option-argument string.
        """
        index = -1
        for i, item in enumerate(self.argv):
            if item == '--': break
            if i > 0 and not lookslikeopt(item) and self.type(self.argv[i-1]) is None: break
            index = i
        if index >= 0: input = self.argv[:index+1]
        else: input = self.argv
        return input

    def _ininput(self, option=None, string=''):
        """Checks if given option is present in input.
        Used internally when checking.

        `option` takes precendence over `string`.

        :param option: option object
        :type option: clap.option.Option
        :param string: option name
        :type string: str
        """
        input = self._getinput()
        if string:
            name = string
            alias = self.alias(string)
        if option is not None:
            if string: warnings.warn('got both option and string parameters')
            name = str(option)
            alias = option._alias(name)
        result = False
        if name in input or (alias and alias in input): result = True
        return result

    def _variantin(self, option=None, string=''):
        """Returns which variant of option (long or short) is present in input.
        Used internaly when checking input. Empty string indicates that no variant
        is present (option is not present).

        `option` takes precendence over `string`.

        :param option: option name
        :type option: str
        """
        input = self._getinput()
        if string:
            name = string
            alias = self.alias(string)
        if option is not None:
            name = str(option)
            alias = option._alias(name)
        variant = ''
        if name in input: variant = name
        if alias and (alias in input): variant = alias
        return variant
