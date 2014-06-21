#!/usr/bin/env python3


from . import shared, errors, parser


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
        try:
            input = self._parser._getinput()
        except KeyError as e:
            raise errors.UnrecognizedOptionError(e)
        for i in input:
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
                    raise errors.MissingArgumentError('{0}={1}'.format(opt, ', '.join(types)))
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
                if not self._parser._mode.accepts(n): raise errors.UIDesignError('option "{0}" is not required with an option that is not recognized by parser: {1}'.format(option, n))
                n = self._parser._mode.getopt(name=n)
                check = not self._parser._ininput(option=n)
            if not check: continue
            if not self._parser._ininput(option=option): raise errors.RequiredOptionNotFoundError(option)

    def _checkrequires(self):
        """Check if all options required by other options are present.
        """
        for option in self._parser._mode.options():
            if not self._parser._ininput(option): continue
            for n in option['requires']:
                if not self._parser._mode.accepts(n):
                    raise errors.UIDesignError('\'{0}\' requires unrecognized option \'{1}\''.format(needs, n))
                n = self._parser._mode.getopt(n)
                if not self._parser._ininput(option=n):
                    needs = self._parser._whichaliasin(option)
                    raise errors.RequiredOptionNotFoundError('{0} -> {1}'.format(needs, n))

    def _checkwants(self):
        """Check for wanted options.
        """
        for i in self._parser._mode.options():
            alias_present = self._parser._whichaliasin(i)
            if not self._parser._ininput(i) or not i['wants']: continue
            fail = True
            for n in i['wants']:
                if not self._parser._mode.accepts(str(n)):
                    raise errors.UIDesignError('\'{0}\' wants unrecognized option \'{1}\''.format(alias_present, n))
                if self._parser._ininput(option=self._parser._mode.getopt(n)):
                    fail = False
                    break
            if fail:
                raise errors.WantedOptionNotFoundError('{0} -> {1}'.format(alias_present, ', '.join(i['wants'])))

    def _checkconflicts(self):
        """Check for conflicting options.
        """
        for i in self._parser._mode.options():
            conflicted = self._parser._whichaliasin(i)
            if not self._parser._ininput(i) or not i['conflicts']: continue
            for c in i['conflicts']:
                if not self._parser._mode.accepts(str(c)):
                    raise errors.UIDesignError('\'{0}\' conflicts with unrecognized option \'{1}\''.format(conflicted, c))
                conflicting = self._parser._whichaliasin(self._parser._mode.getopt(c))
                if conflicting:
                    raise errors.ConflictingOptionsError('{0} | {1}'.format(conflicted, conflicting))

    def _checkoperandscompat(self):
        """Checks if operands types list length is compatible with specified range of operands.
        """
        types = self._parser._mode.getOperandsTypes()
        if not types: return
        least, most = self._parser._mode.getOperandsRange()
        if most is not None and most < len(types):
            raise errors.UIDesignError('upper range of operands not compatible with given list of operand types: list of types too long: expected at most {0} but got {1}'.format(most, len(types)))
        if least is not None and most is not None and least == most and (least % len(types)):
            raise errors.UIDesignError('requested fixed number of operands not compatible with given list of operand types: should be a number divisible by {0} but is {1}'.format(len(types), least))
        if least is not None and (least > len(types)) and (least % len(types)):
            raise errors.UIDesignError('lower range of operands not compatible with given list of operand types: should be a number divisible by {0} but is {1}'.format(len(types), least))
        if most is not None and (most > len(types)) and (most % len(types)):
            raise errors.UIDesignError('upper range of operands not compatible with given list of operand types: should be a number divisible by {0} but is {1}'.format(len(types), most))

    def _checkoperandsrange(self):
        """Checks whether operands given match specified range.
        """
        got = len(self._parser._getheuroperands()[0])
        least, most = self._parser._mode.getOperandsRange()
        fail = False
        if least is not None and least == most and got != least:
            msg = 'expected exactly {0} operands but got {1}'.format(least, got)
            raise errors.InvalidOperandRangeError(msg)
        if least is not None and got < least:
            msg = 'expected at least {0} operands but got {1}'.format(least, got)
            raise errors.InvalidOperandRangeError(msg)
        if most is not None and got > most:
            msg = 'expected at most {0} operands but got {1}'.format(most, got)
            raise errors.InvalidOperandRangeError(msg)
        if least is None and most is None and self._parser._mode.getOperandsTypes():
            typeslen = len(self._parser._mode.getOperandsTypes())
            if got % typeslen and got > typeslen:
                msg = 'expected number of operands divisible by {0} but got {1}'.format(typeslen, got)
                raise errors.InvalidOperandRangeError(msg)
            elif got < typeslen:
                msg = 'expected at least {0} operands but got {1}'.format(typeslen, got)
                raise errors.InvalidOperandRangeError(msg)

    def _checkchildmode(self, rangecompat=False):
        """Checks if provided nested mode is accepted and has valid input.
        """
        operands, nested = self._parser._getheuroperands()
        if not nested: return
        child = nested.pop(0)
        if not self._parser._mode.hasmode(child): raise errors.UnrecognizedModeError(child)
        else: RedChecker(parser.Parser(self._parser._mode._modes[child]).feed(nested)).check(rangecompat=rangecompat)

    def check(self, rangecompat=True):
        """Validates if the given input is correct for given UI and
        detects some errors with UI design.

        - `rangecompat`: pass as false to disable if list of types and range of opperands are mutually compatible,
            sometimes this check may not be needed,
        """
        self._checkunrecognized()
        self._checkconflicts()
        self._checkarguments()
        self._checkrequired()
        self._checkrequires()
        self._checkwants()
        if rangecompat: self._checkoperandscompat()
        self._checkoperandsrange()
        self._checkchildmode(rangecompat=rangecompat)
