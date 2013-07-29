#!/usr/bin/env python3


from clap import base, option, errors


"""This module contains Parser() object.
"""


class Parser():
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

    def type(self, s):
        """Returns type of given option.
        None indicates that option takes no additional argument.
        """
        t = None
        for o in self.options:
            if o.match(s):
                t = o.type()
        return t

    def gethint(self, option):
        """Returns hint for given option.
        """
        for o in self.options:
            if o.match(option):
                hint = o['hint']
                break
        return hint

    def _getinput(self):
        """Returns list of options and arguments until '--' string or
        first non-option and non-option-argument string.
        """
        index = 0
        for i, item in enumerate(self.argv):
            if item == '--': break
            if i > 0 and not base.lookslikeopt(item) and self.type(self.argv[i-1]) is None: break
            index = i
        if index: input = self.argv[:index+1]
        else: input = self.argv
        return input

    def _ininput(self, option):
        """Checks if given option is present in input.
        Used internally when checking.

        :param option: option name
        :type option: str
        """
        input = self._getinput()
        alias = self.alias(option)
        result = False
        if option in input or (alias and alias in input): result = True
        return result

    def _variantin(self, option):
        """Returns which variant of option (long or short) is present in input.
        Used internaly when checking input. Empty string indicates that no variant
        is present (option is not present).

        :param option: option name
        :type option: str
        """
        input = self._getinput()
        alias = self.alias(option)
        variant = ''
        if option in input: variant = option
        if alias and (alias in input): variant = alias
        return variant

    def _checkunrecognized(self):
        """Checks if input list contains any unrecognized options.
        """
        for i in self._getinput():
            if i == '--': break
            if base.lookslikeopt(i) and not self.accepts(i): raise errors.UnrecognizedOptionError(i)

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
        input = self._getinput()
        for i, opt in enumerate(input):
            if i == '--': break
            if base.lookslikeopt(opt) and self.type(opt):
                if i+1 == len(input): raise errors.MissingArgumentError(opt)
                arg = input[i+1]
                try: self.type(opt)(arg)
                except ValueError as e: raise errors.InvalidArgumentTypeError('{0}: {1}'.format(opt, e))
                if deep and base.lookslikeopt(arg) and self.accepts(arg): raise errors.MissingArgumentError(opt)

    def _checkrequired(self):
        """Checks if all required options are present in input list.
        """
        for option in self.options:
            check = option['required']
            for n in option['not_with']:
                if not check: break
                check = not self._ininput(n)
            if not check: continue
            if not self._ininput(str(option)): raise errors.RequiredOptionNotFoundError(option)

    def _checkrequires(self):
        """Check if all options required by other options are present.
        """
        for o in self.options:
            option = str(o)
            if not self._ininput(option): continue
            for n in o['requires']:
                if not self._ininput(option):
                    if option in self._getinput(): needs = option
                    else: needs = self.alias(option)
                    raise errors.RequiredOptionNotFoundError('{0} -> {1}'.format(needs, n))

    def _checkneeds(self):
        """Check needed options.
        """
        for i in self.options:
            option = str(i)
            if not self._ininput(option): continue
            fail = True
            for n in i['needs']:
                if self._ininput(option):
                    fail = False
                    break
            if fail and i['needs']:
                needs = self._variantin(option)
                raise errors.NeededOptionNotFoundError('{0} -> {1}'.format(needs, ', '.join(i['needs'])))

    def _checkconflicts(self):
        """Check for conflicting options.
        """
        for i in self.options:
            option = str(i)
            if i['conflicts'] and self._ininput(option):
                conflicted = self._variantin(option)
                for c in i['conflicts']:
                    conflicting = self._variantin(c)
                    if conflicting: raise errors.ConflictingOptionsError('{0} | {1}'.format(conflicted, conflicting))

    def check(self, deep=True):
        """Checks if input list is valid for this instance of Parser().
        Run before `parse()` to check for errors in input list.
        """
        self._checkunrecognized()
        self._checkrequired()
        self._checkrequires()
        self._checkneeds()
        self._checkconflicts()
        self._checkarguments(deep=deep)

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
