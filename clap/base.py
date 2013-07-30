#!/usr/bin/env python3


"""Functions, routines and regular expressions shared between CLAP modules.
"""


import re


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
    def __init__(self, argv):
        self.argv = argv
        self.options = []

    def type(self, name):
        """Returns type of given option.
        None indicates that option takes no additional argument.
        """
        t = None
        for o in self.options:
            if o.match(s):
                t = o.type()
        return t

    def _getinput(self):
        """Returns list of options and arguments until '--' string or
        first non-option and non-option-argument string.
        """
        index = 0
        for i, item in enumerate(self.argv):
            if item == '--': break
            if i > 0 and not lookslikeopt(item) and self.type(self.argv[i-1]) is None: break
            index = i
        if index: input = self.argv[:index+1]
        else: input = self.argv
        return input

    def _ininput(self, option):
        """Checks if given option is present in input.
        Used internally when checking.

        :param option: option object
        :type option: clap.option.Option
        """
        input = self._getinput()
        name = str(option)
        alias = option._alias(name)
        result = False
        if name in input or (alias and alias in input): result = True
        return result

    def _variantin(self, option):
        """Returns which variant of option (long or short) is present in input.
        Used internaly when checking input. Empty string indicates that no variant
        is present (option is not present).

        :param option: option name
        :type option: str
        """
        input = self._getinput()
        name = str(option)
        alias = option.alias(name)
        variant = ''
        if name in input: variant = name
        if alias and (alias in input): variant = alias
        return variant


