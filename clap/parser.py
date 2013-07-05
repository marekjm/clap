#!/usr/bin/env python3


from clap import formater, option, errors


"""This module contains Parser() object.
"""


class Parser():
    """Used for parsing options.
    """
    argv = []
    parsed = {}
    options = []
    arguments = []

    def __init__(self, argv=[]):
        self.feed(argv)
        self.add(long='CLAP-deep-check', type=str)

    def __contains__(self, option):
        """Returns True if Parser() contains given option as parsed.
        Remeber to parse() the input before you will use this feature.
        """
        return option in self.parsed

    def _metahas(self, string):
        return string in self.argv

    def _metaget(self, string):
        if self.parsed: value = self.get(string)
        elif self.type(string) is not None: value = self.argv[self.argv.index(string)+1]
        else: value = None
        return value

    def feed(self, argv):
        """Feeds input arguments list to parser.
        Feeding new data to Parser() resets `parsed` and
        `arguments` variables.
        """
        self.argv = argv
        self.parsed = {}
        self.arguments = []

    def add(self, short='', long='', type=None, required=False, conflicts=[], hint=''):
        """Adds an option to the list of options recognized by parser.
        Available types are: int, float and str.

        :returns: dict of new option
        """
        if not (short or long): raise TypeError('neither `short` nor `long` was specified')
        new = option.Option(short=short, long=long, type=type, required=required, conflicts=conflicts, hint=hint)
        self.options.append(new)
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

    def type(self, option):
        """Returns type of given option.
        None indicates that option takes no additional argument.
        """
        type = None
        for o in self.options:
            if o.match(option):
                type = o.type()
                break
        return type

    def gethint(self, option):
        """Returns hint for given option.
        """
        for o in self.options:
            if o.match(option):
                hint = o['hint']
                break
        return hint

    def help(self):
        """Prints help for this instance of Parser().
        """
        for o in self.options:
            if o['short']: option = o['short']
            else: option = o['long']
            message = option
            if self.alias(option): message += ', {0}'.format(self.alias(option))
            message += ' ({0})'.format(self.type(option))
            if self.gethint(option): message += ': {0}'.format(self.gethint(option))
            print(message)

    def _checkunrecognized(self):
        """Checks if input list contains any unrecognized options.
        """
        for i in self.argv:
            if i == '--': break
            if formater.lookslikeopt(i) and not self.accepts(i): raise errors.UnrecognizedOptionError(i)

    def _checkarguments(self, deep=True):
        """Checks if arguments given to options which require them are valid.
        Raises `MissingArgumentError` when option which requires an argument is last item
        in input list.
        Raises `TypeError` when option is given argument of invalid type.
        Raises `MissingArgumentError` when option which requires an argument is followed by 
        another option accepted by this instance of parser.
        **Notice:** if you want to pass option-like argument wrap it in `"` or `'` and 
        escape first hyphen or double-escape first hyphen.
        Last check is done only when `deep` argument is True.
        """
        for i, opt in enumerate(self.argv):
            if i == '--': break
            if formater.lookslikeopt(opt) and self.type(opt):
                if i+1 == len(self.argv): raise errors.MissingArgumentError(opt)
                arg = self.argv[i+1]
                try: self.type(opt)(arg)
                except ValueError as e: raise TypeError(e)
                if deep and formater.lookslikeopt(arg) and self.accepts(arg): raise errors.MissingArgumentError(opt)

    def _checkrequired(self):
        """Checks if all required options are present in input list.
        """
        for i in self.options:
            if i['required']:
                if i['long']: option = i['long']
                else: option = i['short']
                alias = self.alias(option)
                fail = True
                if option in self.argv: fail = False
                if alias and alias in self.argv: fail = False
                if fail: raise errors.RequiredOptionNotFoundError(option)

    def _checkconflicts(self):
        """Check for conflicting options.
        """
        for i in self.options:
            if i['long']: o = i['long']
            else: o = i['short']
            if i['conflicts'] and o in self.argv:
                for c in i['conflicts']:
                    alias = self.alias(c)
                    conflicting = ''
                    if c in self.argv: conflicting = c
                    elif alias and alias in self.argv: conflicting = alias
                    if conflicting: raise errors.ConflictingOptionsError('{0} : {1}'.format(o, conflicting))

    def check(self, deep=True):
        """Checks if input list is valid for this instance of Parser().
        Run before `parse()` to check for errors in input list.
        """
        if self._metahas('--CLAP-deep-check'):
            if self._metaget('--CLAP-deep-check') == 'on': deep = True
            elif self._metaget('--CLAP-deep-check') == 'off': deep = False
        self._checkunrecognized()
        self._checkarguments(deep=deep)
        self._checkrequired()
        self._checkconflicts()

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
