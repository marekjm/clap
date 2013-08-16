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
        i = 0
        while i < len(input):
            opt = input[i]
            if base.lookslikeopt(opt) and self.type(opt):
                types = self.type(opt)
                if i+len(types) >= len(input):
                    raise errors.MissingArgumentError('{0} ({1})'.format(opt, ', '.join([str(t)[8:-2] for t in types])))
                if base.lookslikeopt(input[i+1]) and self.accepts(input[i+1]):
                    raise errors.MissingArgumentError(opt)
                for n, atype in enumerate(types):
                    i += 1
                    try:
                        atype(input[i])
                    except IndexError:
                        expected = ', '.join([str(t)[8:-2] for t in types])
                        got = ', '.join([str(t)[8:-2] for t in types[:n]])
                        raise errors.MissingArgumentError('{0} requires ({1}) but got only ({2})'.format(opt, expected, got))
                    except ValueError as e:
                        raise errors.InvalidArgumentTypeError('{0}: {1}: {2}'.format(opt, n, e))
            i += 1

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
                    if conflicting:
                        raise errors.ConflictingOptionsError('{0} | {1}'.format(conflicted, self._variantin(string=c)))

    def check(self):
        """Performs a check.
        """
        self._checkunrecognized()
        self._checkconflicts()
        self._checkarguments()
        self._checkrequired()
        self._checkrequires()
        self._checkneeds()
