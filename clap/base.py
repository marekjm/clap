#!/usr/bin/env python3


"""Functions, routines and regular expressions shared between CLAP modules.
"""


import warnings

from clap import option, checker, shared


#   special flag which will issue debug messages when True
DEBUG = False


class Base():
    """Base class for option and checker.
    """
    def __init__(self, argv=[]):
        self._argv = argv
        self._options = []
        self._parsed = {}
        self._operands = []

    def __eq__(self, sth):
        """Parsers are equal when they have the same:

            * options,
            * parsed options,
            * operands,

        Arguments given by user does not matter before they are parsed.
        So, if two bases are compared and have everything but argv equal
        this call will evaluate to True if the bases were not parsed and
        to False if they have been parsed.
        """
        options = self._options == sth._options
        parsed = self._parsed == sth._parsed
        operands = self._operands == self._operands
        return options and parsed and operands

    def __contains__(self, option):
        """Checks if Base contains given option object.
        """
        return option in self._options

    def _append(self, option):
        """Appends `Option()` object to options list.
        """
        self._options.append(option)

    def add(self, short='', long='', arguments=[], requires=[], wants=[], required=False, not_with=[], conflicts=[], help=''):
        """Adds an option to the list of options recognized by parser.
        Available types are: int, float and str.
        :returns: clap.option.Option
        """
        new = option.Option(short=short, long=long, arguments=arguments,
                            requires=requires, wants=wants,
                            required=required, not_with=not_with,
                            conflicts=conflicts,
                            help=help)
        self._append(new)
        return new

    def remove(self, short='', long=''):
        """Removes option from the list.

        :returns: non-negative integer indicates that some option was removed
        """
        index = -1
        for i, opt in enumerate(self._options):
            if opt.match(short) or opt.match(long):
                index = i
                break
        if index: self._options.pop(index)
        return index

    def accepts(self, option):
        """Returns True if Parser() accepts this option.
        """
        result = False
        for i in self._options:
            if i.match(option):
                result = True
                break
        return result

    def type(self, name):
        """Returns list of types of given option's arguments.
        Empty list indicates that option takes no additional argument.
        """
        t = []
        for o in self._options:
            if o.match(name):
                t = o.type()
                break
        return t

    def alias(self, name):
        """Returns alias string for given option.
        Returns empty string if no alias exist.
        """
        alias = ''
        for i in self._options:
            if i.match(name):
                alias = i._alias(name)
                break
        return alias

    def _getinput(self):
        """Returns list of options and arguments until '--' string or
        first non-option and non-option-argument string.
        Simple description: returns input without final arguments.
        """
        if DEBUG: warnings.warn('clap.base.Base._getinput() needs some optimization if possible')
        index, i = -1, 0
        input = []
        while i < len(self._argv):
            item = self._argv[i]
            #   if a breaker is encountered -> break
            if item == '--': break
            #   if non-option string is encountered and it's not an argument -> break
            if i == 0 and not shared.lookslikeopt(item): break
            if i > 0 and not shared.lookslikeopt(item) and not self.type(self._argv[i-1]): break
            #   if non-option string is encountered and it's an argument
            #   increase counter by the number of arguments the option requests and
            #   proceed futher
            if i > 0 and not shared.lookslikeopt(item) and self.type(self._argv[i-1]):
                i += len(self.type(self._argv[i-1]))-1
            index = i
            i += 1
        if index >= 0:
            #   if index is at least equal to zero this means that some input was found
            input = self._argv[:index+1]
        return input

    def _getarguments(self):
        """Returns list of all arguments passed to the program.
        """
        n = len(self._getinput())
        if '--' in self._argv: n += 1
        return self._argv[n:]

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

    def feed(self, argv):
        """Feeds input arguments list to parser.
        Feeding new data to resets `parsed` and
        `operands` variables.
        """
        self._argv = argv
        self.parsed = {}
        self.arguments = []

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
        self._parsed = parsed
        self._operands = self._getarguments()

    def get(self, key):
        """Returns None if given option does not request an argument.
        Returns tuple if option requests more than one argument.
        For programmers' convinience, returns object of given type if
        option requests one argument.
        """
        value = self._parsed[key]
        if len(value) == 0: value = None
        elif len(value) == 1: value = value[0]
        return value

    def getoperands(self):
        """Returns list of operands passed to the program.
        """
        return self._operands

    def getopts(self):
        """Returns options supported by this parser.
        """
        return self._options

    def check(self):
        """Checks if input list is valid for this instance of Parser().
        Run before `parse()` to check for errors in input list.
        """
        checker.Checker(self).check()
