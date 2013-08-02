#!/usr/bin/env python3


from clap import base, errors


"""This module contains Checker() object which is used internaly, by
Parser() to check correctness of input.
"""


class Checker(base.Base):
    """This object is used for checking correctness of input.
    """
    def __init__(self, parser):
        self.argv = parser.argv
        self.options = parser.options

    def _checkunrecognized(self):
        """Checks if input list contains any unrecognized options.
        """
        for i in self._getinput():
            if i == '--': break
            if base.lookslikeopt(i) and not self.accepts(i): raise errors.UnrecognizedOptionError(i)

    def _checkarguments(self):
        """Checks if arguments given to options which require them are valid.
        Raises `MissingArgumentError` when option which requires an argument is last item
        in input list.
        Raises `InvalidArgumentTypeError` when option is given argument of invalid type.
        Raises `MissingArgumentError` when option which requires an argument is followed by
        another option accepted by this instance of parser.
        **Notice:** if you want to pass option-like argument wrap it in `"` or `'` and
        escape first hyphen or double-escape first hyphen.
        """
        input = self._getinput()
        for i, opt in enumerate(input):
            if i == '--': break
            if base.lookslikeopt(opt) and self.type(opt):
                if i+1 == len(input): raise errors.MissingArgumentError(opt)
                arg = input[i+1]
                if base.lookslikeopt(arg) and self.accepts(arg): raise errors.MissingArgumentError(opt)
                try: self.type(opt)(arg)
                except ValueError as e: raise errors.InvalidArgumentTypeError('{0}: {1}'.format(opt, e))

    def _checkrequired(self):
        """Checks if all required options are present in input list.
        """
        for option in self.options:
            check = option['required']
            for n in option['not_with']:
                if not check: break
                check = not self._ininput(string=n)
            if not check: continue
            if not self._ininput(option=option): raise errors.RequiredOptionNotFoundError(option)

    def _checkrequires(self):
        """Check if all options required by other options are present.
        """
        for option in self.options:
            if not self._ininput(option): continue
            for n in option['requires']:
                if not self._ininput(string=n):
                    needs = self._variantin(option)
                    raise errors.RequiredOptionNotFoundError('{0} -> {1}'.format(needs, n))

    def _checkneeds(self):
        """Check needed options.
        """
        for i in self.options:
            if not self._ininput(i) or not i['needs']: continue
            fail = True
            for n in i['needs']:
                if self._ininput(string=n):
                    fail = False
                    break
            if fail:
                needs = self._variantin(i)
                raise errors.NeededOptionNotFoundError('{0} -> {1}'.format(needs, ', '.join(i['needs'])))

    def _checkconflicts(self):
        """Check for conflicting options.
        """
        for i in self.options:
            if i['conflicts'] and self._ininput(i):
                conflicted = self._variantin(i)
                for c in i['conflicts']:
                    conflicting = self._ininput(string=c)
                    if conflicting: raise errors.ConflictingOptionsError('{0} | {1}'.format(conflicted, self._variantin(string=c)))

    def check(self):
        """Performs a check.
        """
        self._checkunrecognized()
        self._checkarguments()
        self._checkrequired()
        self._checkrequires()
        self._checkneeds()
        self._checkconflicts()
