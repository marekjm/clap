#!/usr/bin/env python3


from clap import formater, option, errors


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

    def add(self, short='', long='', argument=None, required=False, not_with=[], conflicts=[], hint=''):
        """Adds an option to the list of options recognized by parser.
        Available types are: int, float and str.

        :param short: short, one character name for the option ( [a-zA-Z] )
        :type short: str
        :param long: long multiple-character name for option ( [a-zA-Z]+[a-zA-Z0-9]*(-[a-zA-Z0-9]+)* )
        :type short: str
        :param type: type of argument for the option
        :type type: str, int, float
        :param required: whether this option is required or not
        :type required: bool
        :param not_with: list of options with which this option is not required (give only with `required`)
        :param not_with: list[str]
        :param conflicts: list of options with which this option must not be passed (this can be manipulated by user
            using *backdoor-style* option `--CLAP-deep-check on|off`)
        :type conflicts: list[str]
        :param hint: hint for the option
        :type short: str

        :returns: clap.option.Option
        """
        new = option.Option(short=short, long=long, argument=argument, required=required, not_with=not_with, conflicts=conflicts, hint=hint)
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
                except ValueError as e: raise errors.InvalidArgumentTypeError('{0}: {1}'.format(opt, e))
                if deep and formater.lookslikeopt(arg) and self.accepts(arg): raise errors.MissingArgumentError(opt)

    def _checkrequired(self):
        """Checks if all required options are present in input list.
        """
        for i in self.options:
            check = True
            if not i['required']: continue
            if i['not_with']:
                for n in i['not_with']:
                    alias = self.alias(n)
                    if n in self.argv: check = False
                    if alias and alias in self.argv: check = False
                    if not check: break
            if not check: continue
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
            o = str(i)
            oalias = self.alias(o)
            if i['conflicts'] and (o in self.argv or (oalias and oalias in self.argv)):
                if o in self.argv: conflicted = o
                else: conflicted = oalias
                for c in i['conflicts']:
                    alias = self.alias(c)
                    conflicting = ''
                    if c in self.argv: conflicting = c
                    elif alias and alias in self.argv: conflicting = alias
                    if conflicting: raise errors.ConflictingOptionsError('{0} | {1}'.format(conflicted, conflicting))

    def check(self, deep=True):
        """Checks if input list is valid for this instance of Parser().
        Run before `parse()` to check for errors in input list.
        """
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
