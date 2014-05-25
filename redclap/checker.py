#!/usr/bin/env python3


from . import shared, errors


"""This module contains Checker() object which is used internaly, by
Parser() to check correctness of input.
"""


class RedChecker():
    """This object is used for checking correctness of input.
    """
    def __init__(self, parser):
        self._parser = parser

    def _checkunrecognized(self):
        """Checks if input list contains any unrecognized options.
        """
        for i in self._parser._getinput():
            if shared.lookslikeopt(i) and not self._parser._mode.accepts(i): raise errors.UnrecognizedOptionError(i)

    def _checkarguments(self):
        """Checks if arguments given to options which require them are valid.
        **Notice:** if you want to pass option-like argument wrap it in `"` or `'` and
        escape first hyphen or double-escape first hyphen.
        """
        input = self._parser._getinput()
        i = 0
        while i < len(input):
            opt = input[i]
            if shared.lookslikeopt(opt) and self._parser._mode.getopt(opt).params():
                types = self._parser._mode.getopt(opt).params()
                if i+len(types) >= len(input):
                    # missing parameters at the end of input
                    raise errors.MissingArgumentError('{0} ({1})'.format(opt, ', '.join([str(t)[8:-2] for t in types])))
                if shared.lookslikeopt(input[i+1]) and self._parser._mode.accepts(input[i+1]):
                    # number of parameters too low before next option is passed
                    raise errors.MissingArgumentError(opt)
                for n, atype in enumerate(types):
                    i += 1
                    try:
                        (atype if type(atype) is not str else self._parser._typehandlers[atype])(input[i])
                    except KeyError:
                        raise errors.UIDesignError('missing type handler "{0}" for option: {1}'.format())
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
        for option in self._parser._mode.options():
            check = option['required']
            for n in option['not_with']:
                if not check: break
                check = not self._parser._strininput(string=n)
            if not check: continue
            if not self._parser._ininput(option=option): raise errors.RequiredOptionNotFoundError(option)

    def _checkrequires(self):
        """Check if all options required by other options are present.
        """
        for option in self._parser._options:
            if not self._parser._ininput(option): continue
            for n in option['requires']:
                if not self._parser._ininput(string=n):
                    needs = self._parser._variantin(option)
                    if not self._parser.accepts(n):
                        raise errors.UIDesignError('\'{0}\' requires unrecognized option \'{1}\''.format(needs, n))
                    raise errors.RequiredOptionNotFoundError('{0} -> {1}'.format(needs, n))

    def _checkwants(self):
        """Check for wanted options.
        """
        for i in self._parser._options:
            if not self._parser._ininput(i) or not i['wants']: continue
            fail = True
            for n in i['wants']:
                if self._parser._ininput(string=n):
                    fail = False
                    break
            if fail:
                needs = self._parser._variantin(i)
                raise errors.WantedOptionNotFoundError('{0} -> {1}'.format(needs, ', '.join(i['wants'])))

    def _checkconflicts(self):
        """Check for conflicting options.
        """
        for i in self._parser._options:
            if i['conflicts'] and self._parser._ininput(i):
                conflicted = self._parser._variantin(i)
                for c in i['conflicts']:
                    conflicting = self._parser._ininput(string=c)
                    if conflicting:
                        raise errors.ConflictingOptionsError('{0} | {1}'.format(conflicted, self._parser._variantin(string=c)))

    def check(self):
        """Performs a check.
        """
        self._checkunrecognized()
        self._checkconflicts()
        self._checkarguments()
        self._checkrequired()
        self._checkrequires()
        self._checkwants()


class Checker():
    """This object is used for checking correctness of input.
    """
    def __init__(self, parser):
        self._parser = parser

    def _checkunrecognized(self):
        """Checks if input list contains any unrecognized options.
        """
        for i in self._parser._getinput():
            if shared.lookslikeopt(i) and not self._parser.accepts(i): raise errors.UnrecognizedOptionError(i)

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
        input = self._parser._getinput()
        i = 0
        while i < len(input):
            opt = input[i]
            if shared.lookslikeopt(opt) and self._parser.type(opt):
                types = self._parser.type(opt)
                if i+len(types) >= len(input):
                    raise errors.MissingArgumentError('{0} ({1})'.format(opt, ', '.join([str(t)[8:-2] for t in types])))
                if shared.lookslikeopt(input[i+1]) and self._parser.accepts(input[i+1]):
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
        for option in self._parser._options:
            check = option['required']
            for n in option['not_with']:
                if not check: break
                check = not self._parser._ininput(string=n)
            if not check: continue
            if not self._parser._ininput(option=option): raise errors.RequiredOptionNotFoundError(option)

    def _checkrequires(self):
        """Check if all options required by other options are present.
        """
        for option in self._parser._options:
            if not self._parser._ininput(option): continue
            for n in option['requires']:
                if not self._parser._ininput(string=n):
                    needs = self._parser._variantin(option)
                    if not self._parser.accepts(n):
                        raise errors.UIDesignError('\'{0}\' requires unrecognized option \'{1}\''.format(needs, n))
                    raise errors.RequiredOptionNotFoundError('{0} -> {1}'.format(needs, n))

    def _checkwants(self):
        """Check for wanted options.
        """
        for i in self._parser._options:
            if not self._parser._ininput(i) or not i['wants']: continue
            fail = True
            for n in i['wants']:
                if self._parser._ininput(string=n):
                    fail = False
                    break
            if fail:
                needs = self._parser._variantin(i)
                raise errors.WantedOptionNotFoundError('{0} -> {1}'.format(needs, ', '.join(i['wants'])))

    def _checkconflicts(self):
        """Check for conflicting options.
        """
        for i in self._parser._options:
            if i['conflicts'] and self._parser._ininput(i):
                conflicted = self._parser._variantin(i)
                for c in i['conflicts']:
                    conflicting = self._parser._ininput(string=c)
                    if conflicting:
                        raise errors.ConflictingOptionsError('{0} | {1}'.format(conflicted, self._parser._variantin(string=c)))

    def check(self):
        """Performs a check.
        """
        self._checkunrecognized()
        self._checkconflicts()
        self._checkarguments()
        self._checkrequired()
        self._checkrequires()
        self._checkwants()
