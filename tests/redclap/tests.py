#/usr/bin/env python3

"""Unit testing suite for RedCLAP library.
"""

import shutil
import unittest
import warnings

import redclap as clap


# enable debugging output which is basically huge number of print() calls
DEBUG = True
# enable information about TODOs in code (if any)
TODOS = False


def getTestMode():
    mode = clap.mode.RedMode()
    mode.addLocalOption(clap.option.Option(short='f', long='foo'))
    mode.addLocalOption(clap.option.Option(short='b', long='bar'))
    mode.addLocalOption(clap.option.Option(short='B', long='baz'))
    return mode


class FormatterTests(unittest.TestCase):
    def testSplittingEqualSignedOptions(self):
        argv = ['--foo=bar', '--', '--baz=bax']
        f = clap.formatter.Formatter(argv)
        f._splitequal()
        self.assertEqual(list(f), ['--foo', 'bar', '--', '--baz=bax'])

    def testSplittingConnectedShortOptions(self):
        argv = ['-abc', '--', '-def']
        f = clap.formatter.Formatter(argv)
        f._splitshorts()
        self.assertEqual(list(f), ['-a', '-b', '-c', '--', '-def'])

    def testGeneralFormating(self):
        argv = ['-abc', 'eggs', '--bar', '--ham', 'good', '--food=spam', '--', '--bax=bay']
        f = clap.formatter.Formatter(argv)
        f.format()
        self.assertEqual(list(f), ['-a', '-b', '-c', 'eggs', '--bar', '--ham', 'good', '--food', 'spam', '--', '--bax=bay'])


class OptionTests(unittest.TestCase):
    def testOnlyShortName(self):
        o = clap.option.Option(short='f')
        self.assertEqual(o['short'], '-f')
        self.assertEqual(o['long'], '')
        self.assertEqual(str(o), '-f')

    def testOnlyLongName(self):
        o = clap.option.Option(long='foo')
        self.assertEqual(o['short'], '')
        self.assertEqual(o['long'], '--foo')
        self.assertEqual(str(o), '--foo')

    def testInvalidLongName(self):
        tests = ['a', 'A', '0', '-']
        for o in tests:
            if DEBUG: print(o)
            self.assertRaises(TypeError, clap.option.Option, long=o)

    def testBothNames(self):
        o = clap.option.Option(short='f', long='foo')
        self.assertEqual(o['short'], '-f')
        self.assertEqual(o['long'], '--foo')
        self.assertEqual(str(o), '--foo')

    def testNoName(self):
        self.assertRaises(TypeError, clap.option.Option)

    def testParams(self):
        o = clap.option.Option(short='f', arguments=[int])
        self.assertEqual([int], o.params())
        p = clap.option.Option(short='f')
        self.assertEqual([], p.params())

    def testMatching(self):
        o = clap.option.Option(short='f', long='foo')
        self.assertEqual(True, o.match('-f'))
        self.assertEqual(True, o.match('--foo'))

    def testAliases(self):
        o = clap.option.Option(short='f', long='foo')
        self.assertEqual('--foo', o.alias('-f'))
        self.assertEqual('-f', o.alias('--foo'))
        self.assertRaises(NameError, o.alias, '--bar')


class ModeTests(unittest.TestCase):
    def testAddingLocalOptions(self):
        mode = clap.mode.RedMode()
        mode.addLocalOption(clap.option.Option(short='a', long='all'))
        self.assertTrue(mode.accepts('-a'))
        self.assertTrue(mode.accepts('--all'))
        self.assertEqual('-a', mode.alias('--all'))
        self.assertEqual('--all', mode.alias('-a'))

    def testAddingGlobalOptions(self):
        mode = clap.mode.RedMode()
        mode.addMode('foo', clap.mode.RedMode())
        mode.addMode('bar', clap.mode.RedMode())
        mode.addGlobalOption(clap.option.Option(short='v', long='verbose')).propagate()
        self.assertTrue(mode.accepts('--verbose'))
        self.assertTrue(mode.getmode('foo').accepts('--verbose'))
        self.assertTrue(mode.getmode('bar').accepts('--verbose'))

    def testAddingModes(self):
        mode = clap.mode.RedMode()
        mode.addMode('foo', clap.mode.RedMode())
        mode.addMode('bar', clap.mode.RedMode())
        self.assertTrue(mode.hasmode('foo'))
        self.assertTrue(mode.hasmode('bar'))

    def testRemovingLocalOption(self):
        """Be careful when manually building interfaces and
        removing options.
        This may lead to UIDesignError-s being raised!
        """
        mode = clap.mode.RedMode()
        mode.addLocalOption(clap.option.Option(short='f', long='foo'))
        self.assertTrue(mode.accepts('--foo'))
        mode.removeLocalOption(name='--foo')
        self.assertFalse(mode.accepts('--foo'))

    def testRemovingGlobalOption(self):
        """Be careful when manually building interfaces and
        removing options.
        This may lead to UIDesignError-s being raised!
        """
        mode = clap.mode.RedMode()
        mode.addGlobalOption(clap.option.Option(short='f', long='foo'))
        self.assertTrue(mode.accepts('--foo'))
        mode.removeGlobalOption(name='--foo')
        self.assertFalse(mode.accepts('--foo'))


class RedParserGeneralTests(unittest.TestCase):
    def testGettingInputAndOperands(self):
        argvariants = [
                (['--', '--foo', '--bar', 'baz', 'bax'], [], ['--foo', '--bar', 'baz', 'bax']),
                (['spam', '--foo', '--bar'], [], None),
                (['42', '--foo', '--bar'], [], None),
                (['42', 'towels'], [], None),
                (['--foo', '--bar', '--baz'], None, []),
                (['--foo', '--bar', '--baz', '--'], ['--foo', '--bar', '--baz'], []),
                (['-f', '--bar', 'spam', '--baz'], ['-f', '--bar'], ['spam', '--baz']),
                ]
        mode = clap.mode.RedMode()
        mode.addLocalOption(clap.option.Option(short='f', long='foo'))
        mode.addLocalOption(clap.option.Option(short='b', long='bar'))
        mode.addLocalOption(clap.option.Option(short='B', long='baz'))
        parser = clap.parser.Parser(mode)
        for argv, input, operands in argvariants:
            if input is None: input = argv[:]
            if operands is None: operands = argv[:]
            parser.feed(argv)
            self.assertEqual(input, parser._getinput())
            self.assertEqual(operands, parser._getoperands())

    def testGettingInputAndOperandsWhenOptionRequestsArguments(self):
        argvariants = [
                (['--foo', '--point', '0', '1', '--bar'], None, []),
                (['--foo', '--point', '0', '1', '--', '42', 'towels'], ['--foo', '--point', '0', '1'], ['42', 'towels']),
                ]
        mode = clap.mode.RedMode()
        mode.addLocalOption(clap.option.Option(short='f', long='foo'))
        mode.addLocalOption(clap.option.Option(short='b', long='bar'))
        mode.addLocalOption(clap.option.Option(short='B', long='baz'))
        mode.addLocalOption(clap.option.Option(short='p', long='point', arguments=['int', 'int']))
        parser = clap.parser.Parser(mode)
        for argv, input, operands in argvariants:
            if input is None: input = argv[:]
            if operands is None: operands = argv[:]
            parser.feed(argv)
            self.assertEqual(input, parser._getinput())
            self.assertEqual(operands, parser._getoperands())

    def testCheckingIfOptionIsInInput(self):
        argvariants = [
                ['--foo', '--bar'],
                ['-f', '--bar', 'spam', '--baz'],
                ['-f', '--bar', '0', '--baz'],
                ['-f', '--bar', '--', '--baz'],
                ]
        mode = clap.mode.RedMode()
        foo = clap.option.Option(short='f', long='foo')
        bar = clap.option.Option(short='b', long='bar')
        baz = clap.option.Option(short='B', long='baz')
        mode.addLocalOption(foo).addLocalOption(bar).addLocalOption(baz)
        parser = clap.parser.Parser(mode)
        for argv in argvariants:
            parser.feed(argv)
            if DEBUG: print('checking argv "{0}" with input part: "{1}"'.format(' '.join(argv), ' '.join(parser._getinput())))
            self.assertTrue(parser._ininput(option=foo))
            self.assertTrue(parser._ininput(option=bar))
            self.assertFalse(parser._ininput(option=baz))

    def testOptionRecognition(self):
        tests = [('-a', True),
                 ('--foo', True),
                 ('--foo=bar', True),
                 ('-abc', True),
                 ('a', False),
                 ('foo', False),
                 ('--a', False),
                 ('-a=foo', False),
                 ('--', False),
                 ('-', False),
                 ]
        for opt, expected in tests:
            if DEBUG: print('string "{0}" should {1}be considered an option string'.format(opt, ('' if expected else 'not ')))
            self.assertEqual(clap.shared.lookslikeopt(opt), expected)


class RedParserParsingTests(unittest.TestCase):
    def testParsingNoModeNoOperands(self):
        mode = clap.mode.RedMode()
        mode.addLocalOption(clap.option.Option(short='t', long='test'))
        mode.addLocalOption(clap.option.Option(short='a', long='answer', arguments=['str', 'int']))
        argv = ['-a', 'is', '42', '--test']
        parser = clap.parser.Parser(mode).feed(argv)
        ui = parser.parse2().finalise().ui()
        self.assertEqual(('is', 42), ui.get('-a'))
        self.assertEqual(('is', 42), ui.get('--answer'))
        self.assertEqual(None, ui.get('-t'))
        self.assertEqual(None, ui.get('--test'))
        self.assertIn('-a', ui)
        self.assertIn('--answer', ui)
        self.assertIn('-t', ui)
        self.assertIn('--test', ui)
        self.assertEqual(0, len(ui))
        self.assertEqual([], ui.operands())

    def testParsingNoMode(self):
        mode = clap.mode.RedMode()
        mode.addLocalOption(clap.option.Option(short='t', long='test'))
        mode.addLocalOption(clap.option.Option(short='a', long='answer', arguments=['str', 'int']))
        mode.setOperandsRange(no=[2, 2])
        argv = ['-a', 'is', '42', '--test', 'foo', 'bar']
        parser = clap.parser.Parser(mode).feed(argv)
        ui = parser.parse2().finalise().ui()
        self.assertEqual(('is', 42), ui.get('-a'))
        self.assertEqual(('is', 42), ui.get('--answer'))
        self.assertEqual(None, ui.get('-t'))
        self.assertEqual(None, ui.get('--test'))
        self.assertIn('-a', ui)
        self.assertIn('--answer', ui)
        self.assertIn('-t', ui)
        self.assertIn('--test', ui)
        self.assertEqual(2, len(ui))
        self.assertEqual(['foo', 'bar'], ui.operands())


class RedParserOptionsTests(unittest.TestCase):
    def testFeedingArgsToParser(self):
        mode = clap.mode.RedMode()
        parser = clap.parser.Parser(mode)
        args = ['-a', '--foo', 'bar']
        parser.feed(args)
        self.assertEqual(args, parser.getargs())

    def testParsingBareOption(self):
        mode = clap.mode.RedMode()
        mode.addLocalOption(clap.option.Option(short='v', long='verbose'))
        parser = clap.parser.Parser(mode).feed(['--verbose']).parse()
        self.assertTrue('--verbose' in parser)
        self.assertTrue('-v' in parser)
        self.assertEqual(None, parser.get('--verbose'))
        self.assertEqual(None, parser.get('-v'))

    def testParsingBareOptions(self):
        mode = clap.mode.RedMode()
        mode.addLocalOption(clap.option.Option(short='v', long='verbose'))
        mode.addLocalOption(clap.option.Option(short='d', long='debug'))
        parser = clap.parser.Parser(mode).feed(['--verbose', '--debug']).parse()
        self.assertTrue('--verbose' in parser)
        self.assertTrue('-v' in parser)
        self.assertTrue('--debug' in parser)
        self.assertTrue('-d' in parser)
        self.assertEqual(None, parser.get('--verbose'))
        self.assertEqual(None, parser.get('-v'))
        self.assertEqual(None, parser.get('--debug'))
        self.assertEqual(None, parser.get('-d'))

    def testParsingPluralOptionsWithoutArguments(self):
        mode = clap.mode.RedMode()
        mode.addLocalOption(clap.option.Option(short='v', long='verbose', plural=True))
        parser = clap.parser.Parser(mode).feed(['--verbose', '--verbose', '-v']).parse()
        self.assertTrue('--verbose' in parser)
        self.assertTrue('-v' in parser)
        self.assertEqual(3, parser.get('--verbose'))
        self.assertEqual(3, parser.get('-v'))

    def testParsingPluralOptionsWithArguments(self):
        mode = clap.mode.RedMode()
        mode.addLocalOption(clap.option.Option(short='f', long='foo', plural=True, arguments=['int']))
        parser = clap.parser.Parser(mode).feed(['--foo', '0', '-f', '1']).parse()
        self.assertTrue('--foo' in parser)
        self.assertTrue('-f' in parser)
        self.assertEqual([(0,), (1,)], parser.get('--foo'))
        self.assertEqual([(0,), (1,)], parser.get('-f'))

    def testParsingOptionWithOneArgument(self):
        mode = clap.mode.RedMode()
        mode.addLocalOption(clap.option.Option(short='f', long='foo', arguments=['str']))
        parser = clap.parser.Parser(mode).feed(['--foo', 'spam']).parse()
        self.assertTrue('--foo' in parser)
        self.assertEqual('spam', parser.get('--foo'))
        self.assertEqual('spam', parser.get('-f'))

    def testParsingOptionWithMultipleArguments(self):
        mode = clap.mode.RedMode()
        mode.addLocalOption(clap.option.Option(short='f', long='foo', arguments=['str', 'str']))
        parser = clap.parser.Parser(mode).feed(['--foo', 'spam', 'eggs']).parse()
        self.assertTrue('--foo' in parser)
        self.assertEqual(('spam', 'eggs'), parser.get('--foo'))
        self.assertEqual(('spam', 'eggs'), parser.get('-f'))

    def testParsingStopsOnFirstNonOption(self):
        mode = clap.mode.RedMode()
        mode.addLocalOption(clap.option.Option(short='f', long='foo', arguments=['str', 'str']))
        parser = clap.parser.Parser(mode).feed(['spam', '--foo']).parse()
        self.assertTrue('--foo' not in parser)
        self.assertEqual(['spam', '--foo'], parser.getoperands())

    def testParsingStopsOnBreaker(self):
        mode = clap.mode.RedMode()
        mode.addLocalOption(clap.option.Option(short='f', long='foo', arguments=['str', 'str']))
        parser = clap.parser.Parser(mode).feed(['--', '--foo']).parse()
        self.assertTrue('--foo' not in parser)
        self.assertEqual(['--foo'], parser.getoperands())

    def testParsingShortOptions(self):
        args = ['-a', '-b', '-c', 'd', 'e', 'f']
        mode = clap.mode.RedMode()
        mode.addLocalOption(clap.option.Option(short='a'))
        mode.addLocalOption(clap.option.Option(short='b'))
        mode.addLocalOption(clap.option.Option(short='c'))
        parser = clap.parser.Parser(mode).feed(args).parse()
        self.assertEqual(None, parser.get('-a'))
        self.assertEqual(None, parser.get('-b'))
        self.assertEqual(None, parser.get('-c'))
        self.assertEqual(['d', 'e', 'f'], parser.getoperands())

    def testShortOptionsWithArguments(self):
        args = ['-s', 'eggs', '-i', '42', '-f', '4.2', '--', 'foo']
        mode = clap.mode.RedMode()
        mode.addLocalOption(clap.option.Option(short='s', arguments=[str]))
        mode.addLocalOption(clap.option.Option(short='i', arguments=[int]))
        mode.addLocalOption(clap.option.Option(short='f', arguments=[float]))
        parser = clap.parser.Parser(mode).feed(args).parse()
        self.assertEqual('eggs', parser.get('-s', tuplise=False))
        self.assertEqual(42, parser.get('-i', tuplise=False))
        self.assertEqual(4.2, parser.get('-f', tuplise=False))
        self.assertEqual(['foo'], parser.getoperands())


class RedCheckerOptionCheckingTests(unittest.TestCase):
    def testUnrecognizedOptions(self):
        argv = ['--foo', '--bar', '--baz']
        mode = clap.mode.RedMode()
        mode.addLocalOption(clap.option.Option(long='foo'))
        mode.addLocalOption(clap.option.Option(long='bar'))
        parser = clap.parser.Parser(mode).feed(argv)
        checker = clap.checker.RedChecker(parser)
        self.assertRaises(clap.errors.UnrecognizedOptionError, checker._checkunrecognized)
        self.assertRaises(clap.errors.UnrecognizedOptionError, checker.check)

    def testArgumentNotGivenAtTheEnd(self):
        argv = ['--bar', '--foo']
        mode = clap.mode.RedMode()
        mode.addLocalOption(clap.option.Option(long='foo', arguments=['str']))
        mode.addLocalOption(clap.option.Option(long='bar'))
        parser = clap.parser.Parser(mode).feed(argv)
        checker = clap.checker.RedChecker(parser)
        self.assertRaises(clap.errors.MissingArgumentError, checker._checkarguments)
        self.assertRaises(clap.errors.MissingArgumentError, checker.check)

    def testArgumentNotGivenAtTheEndBecauseOfBreaker(self):
        argv = ['--bar', '--foo', '--', 'baz']
        mode = clap.mode.RedMode()
        mode.addLocalOption(clap.option.Option(long='foo', arguments=['str']))
        mode.addLocalOption(clap.option.Option(long='bar'))
        parser = clap.parser.Parser(mode).feed(argv)
        checker = clap.checker.RedChecker(parser)
        self.assertRaises(clap.errors.MissingArgumentError, checker._checkarguments)
        self.assertRaises(clap.errors.MissingArgumentError, checker.check)

    def testInvalidArgumentType(self):
        argv = ['--bar', '--foo', 'baz']
        mode = clap.mode.RedMode()
        mode.addLocalOption(clap.option.Option(long='foo', arguments=['int']))
        mode.addLocalOption(clap.option.Option(long='bar'))
        parser = clap.parser.Parser(mode).feed(argv)
        checker = clap.checker.RedChecker(parser)
        self.assertRaises(clap.errors.InvalidArgumentTypeError, checker._checkarguments)
        self.assertRaises(clap.errors.InvalidArgumentTypeError, checker.check)

    def testInvalidArgumentTypeWhenMultipleArgumentsAreRequested(self):
        argv = ['--point', '0', 'y']
        mode = clap.mode.RedMode()
        mode.addLocalOption(clap.option.Option(long='point', arguments=['int', 'int']))
        parser = clap.parser.Parser(mode).feed(argv)
        checker = clap.checker.RedChecker(parser)
        self.assertRaises(clap.errors.InvalidArgumentTypeError, checker._checkarguments)
        self.assertRaises(clap.errors.InvalidArgumentTypeError, checker.check)

    def testAnotherOptionGivenAsArgument(self):
        argv = ['--foo', '--bar']
        mode = clap.mode.RedMode()
        mode.addLocalOption(clap.option.Option(long='foo', arguments=['int']))
        mode.addLocalOption(clap.option.Option(long='bar'))
        parser = clap.parser.Parser(mode).feed(argv)
        checker = clap.checker.RedChecker(parser)
        self.assertRaises(clap.errors.MissingArgumentError, checker._checkarguments)
        self.assertRaises(clap.errors.MissingArgumentError, checker.check)

    def testRequiredOptionNotFound(self):
        argv = ['--bar']
        mode = clap.mode.RedMode()
        mode.addLocalOption(clap.option.Option(long='foo', required=True))
        mode.addLocalOption(clap.option.Option(long='bar'))
        parser = clap.parser.Parser(mode).feed(argv)
        checker = clap.checker.RedChecker(parser)
        self.assertRaises(clap.errors.RequiredOptionNotFoundError, checker._checkrequired)
        self.assertRaises(clap.errors.RequiredOptionNotFoundError, checker.check)

    def testRequiredOptionNotFoundBecauseOfBreaker(self):
        argv = ['--bar', '--', '--foo']
        mode = clap.mode.RedMode()
        mode.addLocalOption(clap.option.Option(long='foo', required=True))
        mode.addLocalOption(clap.option.Option(long='bar'))
        parser = clap.parser.Parser(mode).feed(argv)
        checker = clap.checker.RedChecker(parser)
        self.assertRaises(clap.errors.RequiredOptionNotFoundError, checker._checkrequired)
        self.assertRaises(clap.errors.RequiredOptionNotFoundError, checker.check)

    def testRequiredOptionNotFoundBecauseMisusedAsAnArgumentToAnotherOption(self):
        argv = ['--bar', '--foo']
        mode = clap.mode.RedMode()
        mode.addLocalOption(clap.option.Option(long='foo', required=True))
        mode.addLocalOption(clap.option.Option(long='bar', arguments=['str']))
        parser = clap.parser.Parser(mode).feed(argv)
        checker = clap.checker.RedChecker(parser)
        self.assertRaises(clap.errors.RequiredOptionNotFoundError, checker._checkrequired)
        self.assertRaises(clap.errors.MissingArgumentError, checker.check)

    def testRequiredNotWithAnotherOption(self):
        argv = ['--bar']
        mode = clap.mode.RedMode()
        mode.addLocalOption(clap.option.Option(long='foo', required=True, not_with=['--bar']))
        mode.addLocalOption(clap.option.Option(short='b', long='bar'))
        parser = clap.parser.Parser(mode).feed(argv)
        checker = clap.checker.RedChecker(parser)
        checker._checkrequired()
        checker.check()

    def testRequiredNotWithAnotherOptionNotFoundBecauseOfBreaker(self):
        argv = ['--baz', '--', '-b']
        mode = clap.mode.RedMode()
        mode.addLocalOption(clap.option.Option(long='foo', required=True, not_with=['--bar']))
        mode.addLocalOption(clap.option.Option(short='b', long='bar'))
        mode.addLocalOption(clap.option.Option(short='B', long='baz'))
        parser = clap.parser.Parser(mode).feed(argv)
        checker = clap.checker.RedChecker(parser)
        self.assertRaises(clap.errors.RequiredOptionNotFoundError, checker._checkrequired)
        self.assertRaises(clap.errors.RequiredOptionNotFoundError, checker.check)

    def testOptionRequiredByAnotherOption(self):
        argvariants = [
                ['--foo', '--bar', '--baz'],
                ['-f', '--bar', '--baz'],
                ['--foo', '-b', '--baz'],
                ['--foo', '--bar', '-B'],
                ['-f', '-b', '--baz'],
                ['-f', '--bar', '-B'],
                ['--foo', '-b', '-B'],
                ['-f', '-b', '-B'],
                ]
        mode = clap.mode.RedMode()
        mode.addLocalOption(clap.option.Option(short='f', long='foo', requires=['--bar', '--baz']))
        mode.addLocalOption(clap.option.Option(short='b', long='bar'))
        mode.addLocalOption(clap.option.Option(short='B', long='baz'))
        for argv in argvariants:
            parser = clap.parser.Parser(mode).feed(argv)
            checker = clap.checker.RedChecker(parser)
            if DEBUG: print('checking:', ' '.join(argv))
            checker._checkrequires()
            checker.check()

    def testOptionRequiredByAnotherOptionNotFound(self):
        argv = ['--foo', '--bar']
        mode = clap.mode.RedMode()
        mode.addLocalOption(clap.option.Option(short='f', long='foo', requires=['--bar', '--baz']))
        mode.addLocalOption(clap.option.Option(short='b', long='bar'))
        mode.addLocalOption(clap.option.Option(short='B', long='baz'))
        parser = clap.parser.Parser(mode).feed(argv)
        checker = clap.checker.RedChecker(parser)
        self.assertRaises(clap.errors.RequiredOptionNotFoundError, checker._checkrequires)
        self.assertRaises(clap.errors.RequiredOptionNotFoundError, checker.check)

    def testOptionRequiredByAnotherOptionNotFoundBecauseOfBreaker(self):
        argv = ['--foo', '--bar', '--', '--baz']
        mode = clap.mode.RedMode()
        mode.addLocalOption(clap.option.Option(short='f', long='foo', requires=['--bar', '--baz']))
        mode.addLocalOption(clap.option.Option(short='b', long='bar'))
        mode.addLocalOption(clap.option.Option(short='B', long='baz'))
        parser = clap.parser.Parser(mode).feed(argv)
        checker = clap.checker.RedChecker(parser)
        self.assertRaises(clap.errors.RequiredOptionNotFoundError, checker._checkrequires)
        self.assertRaises(clap.errors.RequiredOptionNotFoundError, checker.check)

    def testOptionWantedByAnotherOption(self):
        argvariants = [
                ['--foo', '--bar', '42', '--baz'],  # both wanted present:: --bar and --baz
                ['--foo', '-b', '42', '--baz'],     # both wanted present:: --bar and --baz
                ['--foo', '--bar', '42', '-B'],     # both wanted present:: --bar and --baz
                ['--foo', '--bar', '42'],           # one wanted present: --bar
                ['--foo', '-b', '42'],              # one wanted present: --bar
                ['--foo', '--baz'],                 # one wanted present: --baz
                ['--foo', '-B'],                    # one wanted present: --baz
                ]
        mode = clap.mode.RedMode()
        mode.addLocalOption(clap.option.Option(short='f', long='foo', wants=['--bar', '--baz']))
        mode.addLocalOption(clap.option.Option(short='b', long='bar', arguments=['int']))
        mode.addLocalOption(clap.option.Option(short='B', long='baz'))
        for argv in argvariants:
            parser = clap.parser.Parser(mode).feed(argv)
            checker = clap.checker.RedChecker(parser)
            if DEBUG: print('checking:', ' '.join(argv))
            checker._checkwants()
            checker.check()

    def testOptionWantedByAnotherOptionNotFound(self):
        argv = ['--foo']
        mode = clap.mode.RedMode()
        mode.addLocalOption(clap.option.Option(short='f', long='foo', wants=['--bar', '--baz']))
        mode.addLocalOption(clap.option.Option(short='b', long='bar', arguments=['int']))
        mode.addLocalOption(clap.option.Option(short='B', long='baz'))
        parser = clap.parser.Parser(mode).feed(argv)
        checker = clap.checker.RedChecker(parser)
        self.assertRaises(clap.errors.WantedOptionNotFoundError, checker._checkwants)
        self.assertRaises(clap.errors.WantedOptionNotFoundError, checker.check)

    def testOptionWantedByAnotherOptionNotFoundBecauseOfBreaker(self):
        argv = ['--foo', '--', '--bar']
        mode = clap.mode.RedMode()
        mode.addLocalOption(clap.option.Option(short='f', long='foo', wants=['--bar', '--baz']))
        mode.addLocalOption(clap.option.Option(short='b', long='bar', arguments=['int']))
        mode.addLocalOption(clap.option.Option(short='B', long='baz'))
        parser = clap.parser.Parser(mode).feed(argv)
        checker = clap.checker.RedChecker(parser)
        self.assertRaises(clap.errors.WantedOptionNotFoundError, checker._checkwants)
        self.assertRaises(clap.errors.WantedOptionNotFoundError, checker.check)

    def testConflicts(self):
        argvariants = [
                ['--foo', '--bar'],
                ['-f', '--bar'],
                ['--foo', '-b'],
                ['-f', '-b'],
                ]
        mode = clap.mode.RedMode()
        mode.addLocalOption(clap.option.Option(short='f', long='foo', conflicts=['--bar']))
        mode.addLocalOption(clap.option.Option(short='b', long='bar'))
        for argv in argvariants:
            parser = clap.parser.Parser(mode).feed(argv)
            checker = clap.checker.RedChecker(parser)
            if DEBUG: print('checking:', ' '.join(argv))
            self.assertRaises(clap.errors.ConflictingOptionsError, checker._checkconflicts)
            self.assertRaises(clap.errors.ConflictingOptionsError, checker.check)

    def testConflictsNotRaisedBecauseOfBreaker(self):
        argvariants = [
                ['--foo', '--', '--bar'],
                ['-f', '--', '--bar'],
                ['--foo', '--', '-b'],
                ['-f', '--', '-b'],
                ]
        mode = clap.mode.RedMode()
        mode.addLocalOption(clap.option.Option(short='f', long='foo', conflicts=['--bar']))
        mode.addLocalOption(clap.option.Option(short='b', long='bar'))
        for argv in argvariants:
            parser = clap.parser.Parser(mode).feed(argv)
            checker = clap.checker.RedChecker(parser)
            if DEBUG: print('checking:', ' '.join(argv))
            checker._checkconflicts()
            checker.check()


class RedParserOperandsTests(unittest.TestCase):
    def testSettingRangeAny(self):
        mode = clap.mode.RedMode()
        mode.setOperandsRange(no=[])
        self.assertEqual((None, None), mode.getOperandsRange())
        mode.setOperandsRange()
        self.assertEqual((None, None), mode.getOperandsRange())

    def testSettingRangeBetween(self):
        mode = clap.mode.RedMode()
        mode.setOperandsRange(no=[1, 2])
        self.assertEqual((1, 2), mode.getOperandsRange())

    def testSettingRangeAtLeast(self):
        mode = clap.mode.RedMode()
        mode.setOperandsRange(no=[-2])
        self.assertEqual((2, None), mode.getOperandsRange())

    def testSettingRangeAtMost(self):
        mode = clap.mode.RedMode()
        mode.setOperandsRange(no=[2])
        self.assertEqual((None, 2), mode.getOperandsRange())

    def testSettingRangeInvalid(self):
        mode = clap.mode.RedMode()
        ranges = [
                [-1, -1],
                [1, 2, 3]
                ]
        for i in ranges:
            self.assertRaises(clap.errors.InvalidOperandRangeError, mode.setOperandsRange, i)

    def testSettingTypesForOperands(self):
        types = ['str', 'int', 'int', 'int']
        mode = clap.mode.RedMode()
        mode.setOperandsTypes(types)
        self.assertEqual(types, mode.getOperandsTypes())

    def testGettingOperandsEnclosed(self):
        argv = ['--foo', '--', '--bar', 'baz', '---', '--baz', 'this', 'is', 'discarded']
        mode = clap.mode.RedMode()
        mode.addLocalOption(clap.option.Option(short='f', long='foo'))
        mode.addLocalOption(clap.option.Option(short='b', long='bar'))
        mode.addLocalOption(clap.option.Option(short='B', long='baz'))
        parser = clap.parser.Parser(mode).feed(argv)
        self.assertEqual(['--bar', 'baz'], parser._getoperands())

    def testGettingOperandsEnclosingNotWorkingWhenThereIsNoTerminator(self):
        argv = ['--foo', '--bar', 'baz', '---', '--baz', 'this', 'is', 'not', 'discarded']
        mode = clap.mode.RedMode()
        mode.addLocalOption(clap.option.Option(short='f', long='foo'))
        mode.addLocalOption(clap.option.Option(short='b', long='bar'))
        mode.addLocalOption(clap.option.Option(short='B', long='baz'))
        parser = clap.parser.Parser(mode).feed(argv)
        self.assertEqual(['baz', '---', '--baz', 'this', 'is', 'not', 'discarded'], parser._getoperands())


class RedParserNestedModesTests(unittest.TestCase):
    def testSimpleChildMode(self):
        mode = clap.mode.RedMode()
        mode.addLocalOption(clap.option.Option(short='b', long='breakfast', arguments=['str']))
        mode.addLocalOption(clap.option.Option(short='w', long='what'))
        mode.setOperandsRange(no=[2, 2])
        mode.addMode(name='child', mode=clap.mode.RedMode().setOperandsRange(no=[2, 2]))
        argv = ['--breakfast', 'yes', '--what', 'spam', 'ham', 'child', 'foo', 'bar']
        operands = ['spam', 'ham']
        nested = ['child', 'foo', 'bar']
        parser = clap.parser.Parser(mode).feed(argv)
        got_operands, got_nested = parser._getheuroperands()
        self.assertEqual(operands, got_operands)
        self.assertEqual(nested, got_nested)

    def testGettingOperandsAndNestedModeItems(self):
        mode = getTestMode().setOperandsRange(no=[2, 2])
        child = clap.mode.RedMode().addLocalOption(clap.option.Option(short='a', long='answer', arguments=['int']))
        mode.addMode(name='child', mode=child)
        argv = ['--foo', '-b', '-B', 'spam', 'ham', 'child', '--answer', '42']
        parser = clap.parser.Parser(mode).feed(argv)
        self.assertEqual(['spam', 'ham'], parser._getheuroperands()[0])
        self.assertEqual(['child', '--answer', '42'], parser._getheuroperands()[1])


class RedCheckerNestedModesCheckingTests(unittest.TestCase):
    def testFixedRangeItemTreatedAsModeBecauseFollowedByOptionAcceptedByOneOfValidChildModes(self):
        mode = getTestMode().setOperandsRange(no=[2, 2])
        child = clap.mode.RedMode().addLocalOption(clap.option.Option(short='a', long='answer', arguments=['int']))
        mode.addMode(name='child', mode=child)
        argv = ['--foo', '-b', '-B', 'spam', 'ham', 'fake', '--answer', '42']
        parser = clap.parser.Parser(mode).feed(argv)
        checker = clap.checker.RedChecker(parser)
        self.assertRaises(clap.errors.UnrecognizedModeError, checker._checkchildmode)
        self.assertRaises(clap.errors.UnrecognizedModeError, checker.check)

    def testFixedRangeUnrecognizedOptionInNestedMode(self):
        mode = getTestMode().setOperandsRange(no=[2, 2])
        child = clap.mode.RedMode().addLocalOption(clap.option.Option(short='a', long='answer', arguments=['int']))
        mode.addMode(name='child', mode=child)
        argv = ['--foo', '-b', '-B', 'spam', 'ham', 'child', '--answer', '42', '--fake']
        parser = clap.parser.Parser(mode).feed(argv)
        checker = clap.checker.RedChecker(parser)
        self.assertRaises(clap.errors.UnrecognizedOptionError, checker._checkchildmode)
        self.assertRaises(clap.errors.UnrecognizedOptionError, checker.check)

    def testFixedRangeInvalidNumberOfOperandsBecauseModeIsGivenTooFast(self):
        mode = getTestMode().setOperandsRange(no=[2, 2])
        child = clap.mode.RedMode().addLocalOption(clap.option.Option(short='a', long='answer', arguments=['int']))
        mode.addMode(name='child', mode=child)
        argv = ['--foo', '-b', '-B', 'spam', 'child', '--answer', '42']
        parser = clap.parser.Parser(mode).feed(argv)
        checker = clap.checker.RedChecker(parser)
        checker._checkchildmode()
        self.assertRaises(clap.errors.InvalidOperandRangeError, checker._checkoperandsrange)
        self.assertRaises(clap.errors.InvalidOperandRangeError, checker.check)

    def testFixedRangeInvalidNumberOfOperandsRaisedBeforeInvalidMode(self):
        mode = getTestMode().setOperandsRange(no=[2, 2])
        child = clap.mode.RedMode().addLocalOption(clap.option.Option(short='a', long='answer', arguments=['int']))
        mode.addMode(name='child', mode=child)
        argv = ['--foo', '-b', '-B', 'spam', 'fake', '--answer', '42']
        parser = clap.parser.Parser(mode).feed(argv)
        checker = clap.checker.RedChecker(parser)
        self.assertRaises(clap.errors.UnrecognizedModeError, checker._checkchildmode)
        self.assertRaises(clap.errors.InvalidOperandRangeError, checker.check)

    def testFluidRangeItemTreatedAsModeBecauseFollowedByOptionAcceptedByOneOfValidChildModes(self):
        mode = getTestMode().setOperandsRange(no=[1, 4])
        child = clap.mode.RedMode().addLocalOption(clap.option.Option(short='a', long='answer', arguments=['int']))
        mode.addMode(name='child', mode=child)
        parser = clap.parser.Parser(mode)
        argvariants = [
                ['--foo', '-b', '-B', 'alpha', 'fake', '--answer', '42'],
                ['--foo', '-b', '-B', 'alpha', 'beta', 'fake', '--answer', '42'],
                ['--foo', '-b', '-B', 'alpha', 'beta', 'gamma', 'fake', '--answer', '42'],
                ['--foo', '-b', '-B', 'alpha', 'beta', 'gamma', 'delta', 'fake', '--answer', '42'],
                ]
        for argv in argvariants:
            parser.feed(argv)
            checker = clap.checker.RedChecker(parser)
            self.assertRaises(clap.errors.UnrecognizedModeError, checker._checkchildmode)
            self.assertRaises(clap.errors.UnrecognizedModeError, checker.check)

    def testFluiddRangeUnrecognizedOptionInNestedMode(self):
        mode = getTestMode().setOperandsRange(no=[1, 4])
        child = clap.mode.RedMode().addLocalOption(clap.option.Option(short='a', long='answer', arguments=['int']))
        mode.addMode(name='child', mode=child)
        parser = clap.parser.Parser(mode)
        argvariants = [
                ['--foo', '-b', '-B', 'alpha', 'child', '--answer', '42', '--fake'],
                ['--foo', '-b', '-B', 'alpha', 'beta', 'child', '--answer', '42', '--fake'],
                ['--foo', '-b', '-B', 'alpha', 'beta', 'gamma', 'child', '--answer', '42', '--fake'],
                ['--foo', '-b', '-B', 'alpha', 'beta', 'gamma', 'delta', 'child', '--answer', '42', '--fake'],
                ]
        for argv in argvariants:
            parser.feed(argv)
            checker = clap.checker.RedChecker(parser)
            self.assertRaises(clap.errors.UnrecognizedOptionError, checker._checkchildmode)
            self.assertRaises(clap.errors.UnrecognizedOptionError, checker.check)

    def testFluidRangeInvalidNumberOfOperandsBecauseModeIsGivenTooFast(self):
        mode = getTestMode().setOperandsRange(no=[1, 4])
        child = clap.mode.RedMode().addLocalOption(clap.option.Option(short='a', long='answer', arguments=['int']))
        mode.addMode(name='child', mode=child)
        argv = ['--foo', '-b', '-B', 'child', '--answer', '42']
        parser = clap.parser.Parser(mode).feed(argv)
        checker = clap.checker.RedChecker(parser)
        checker._checkchildmode()
        self.assertRaises(clap.errors.InvalidOperandRangeError, checker._checkoperandsrange)
        self.assertRaises(clap.errors.InvalidOperandRangeError, checker.check)

    def testFluidRangeInvalidNumberOfOperandsBecauseModeIsGivenTooLate(self):
        mode = getTestMode().setOperandsRange(no=[1, 4])
        child = clap.mode.RedMode().addLocalOption(clap.option.Option(short='a', long='answer', arguments=['int']))
        mode.addMode(name='child', mode=child)
        argv = ['--foo', '-b', '-B', 'alpha', 'beta', 'gamma', 'delta', 'epsilon', 'child', '--answer', '42']
        parser = clap.parser.Parser(mode).feed(argv)
        checker = clap.checker.RedChecker(parser)
        checker._checkchildmode()
        self.assertRaises(clap.errors.InvalidOperandRangeError, checker._checkoperandsrange)
        self.assertRaises(clap.errors.InvalidOperandRangeError, checker.check)

    def testFluidRangeInvalidNumberOfOperandsRaisedBeforeInvalidMode(self):
        mode = getTestMode().setOperandsRange(no=[1, 4])
        child = clap.mode.RedMode().addLocalOption(clap.option.Option(short='a', long='answer', arguments=['int']))
        mode.addMode(name='child', mode=child)
        parser = clap.parser.Parser(mode)
        argvariants = [
                ['--foo', '-b', '-B', 'fake', '--answer', '42'],
                ['--foo', '-b', '-B', 'alpha', 'beta', 'gamma', 'delta', 'epsilon', 'fake', '--answer', '42']
                ]
        for argv in argvariants:
            parser.feed(argv)
            checker = clap.checker.RedChecker(parser)
            self.assertRaises(clap.errors.UnrecognizedModeError, checker._checkchildmode)
            self.assertRaises(clap.errors.InvalidOperandRangeError, checker.check)


class RedCheckerOperandCheckingTests(unittest.TestCase):
    def testOperandRangeAny(self):
        argvariants = [
                ['--foo', '-b'],                    # no operands
                ['--foo', '-b', '0'],               # one operand
                ['--foo', '-b', '0', '1'],          # two operands
                ['--foo', '-b', '0', '1', '2'],     # more than two operands
                ]
        mode = clap.mode.RedMode()
        mode.addLocalOption(clap.option.Option(short='f', long='foo'))
        mode.addLocalOption(clap.option.Option(short='b', long='bar'))
        mode.setOperandsRange(no=[])
        parser = clap.parser.Parser(mode)
        for argv in argvariants:
            parser.feed(argv)
            if DEBUG: print('checking:', parser._getoperands())
            checker = clap.checker.RedChecker(parser)
            checker._checkoperandsrange()

    def testOperandRangeAtLeast(self):
        argvariants = [
                ['--foo', '-b', '0', '1'],
                ['--foo', '-b', '--', '0', '1', '2'],
                ['--foo', '-b', '--', '0', '1', '2', '3'],
                ]
        failvariants = [
                ['--foo', '-b'],
                ['--foo', '-b', '0'],
                ]
        mode = clap.mode.RedMode()
        mode.addLocalOption(clap.option.Option(short='f', long='foo'))
        mode.addLocalOption(clap.option.Option(short='b', long='bar'))
        ranges = [(-2,),]
        for r in ranges:
            mode.setOperandsRange(no=r)
            parser = clap.parser.Parser(mode)
            for argv in argvariants:
                parser.feed(argv)
                if DEBUG: print('checking range {0} with operands: {1} (argv: {2})'.format(r, parser._getoperands(), argv))
                checker = clap.checker.RedChecker(parser)
                checker._checkoperandsrange()
            for argv in failvariants:
                parser.feed(argv)
                if DEBUG: print('fail checking range {0} with operands: {1} (argv: {2})'.format(r, parser._getoperands(), argv))
                checker = clap.checker.RedChecker(parser)
                self.assertRaises(clap.errors.InvalidOperandRangeError, checker._checkoperandsrange)

    def testOperandRangeAtMost(self):
        argvariants = [
                ['--foo', '-b'],
                ['--foo', '-b', '0'],
                ['--foo', '-b', '0', '1'],
                ]
        failvariants = [
                ['--foo', '-b', '0', '1', '2'],
                ['--foo', '-b', '0', '1', '2', '3'],
                ['--foo', '-b', '0', '1', '2', '3', '4'],
                ]
        mode = clap.mode.RedMode()
        mode.addLocalOption(clap.option.Option(short='f', long='foo'))
        mode.addLocalOption(clap.option.Option(short='b', long='bar'))
        ranges = [(2,), (0, 2)]
        for r in ranges:
            mode.setOperandsRange(no=r)
            parser = clap.parser.Parser(mode)
            for argv in argvariants:
                parser.feed(argv)
                if DEBUG: print('checking range {0} with input: {1}'.format(r, parser._getoperands()))
                checker = clap.checker.RedChecker(parser)
                checker._checkoperandsrange()
            for argv in failvariants:
                parser.feed(argv)
                if DEBUG: print('fail checking range {0} with input: {1}'.format(r, parser._getoperands()))
                checker = clap.checker.RedChecker(parser)
                self.assertRaises(clap.errors.InvalidOperandRangeError, checker._checkoperandsrange)

    def testOperandRangeBetween(self):
        argvariants = [
                ['--foo', '-b', '0', '1'],
                ['--foo', '-b', '0', '1', '2'],
                ['--foo', '-b', '0', '1', '2', '3'],
                ]
        failvariants = [
                ['--foo', '-b'],
                ['--foo', '-b', '0'],
                ['--foo', '-b', '0', '1', '2', '3', '4'],
                ]
        mode = clap.mode.RedMode()
        mode.addLocalOption(clap.option.Option(short='f', long='foo'))
        mode.addLocalOption(clap.option.Option(short='b', long='bar'))
        ranges = [(2, 4)]
        for r in ranges:
            mode.setOperandsRange(no=r)
            parser = clap.parser.Parser(mode)
            for argv in argvariants:
                parser.feed(argv)
                if DEBUG: print('checking range {0} with input: {1}'.format(r, parser._getoperands()))
                checker = clap.checker.RedChecker(parser)
                checker._checkoperandsrange()
            for argv in failvariants:
                parser.feed(argv)
                if DEBUG: print('fail checking range {0} with input: {1}'.format(r, parser._getoperands()))
                checker = clap.checker.RedChecker(parser)
                self.assertRaises(clap.errors.InvalidOperandRangeError, checker._checkoperandsrange)

    def testOperandRangeZero(self):
        argvariants = [
                ['--foo', '-b'],
                ['--foo', '-b', '--'],
                ]
        failvariants = [
                ['--foo', '-b', '--', '0'],
                ['--foo', '-b', '--', '0', '1'],
                ['--foo', '-b', '0'],
                ['--foo', '-b', '0', '1'],
                ]
        mode = clap.mode.RedMode()
        mode.addLocalOption(clap.option.Option(short='f', long='foo'))
        mode.addLocalOption(clap.option.Option(short='b', long='bar'))
        ranges = [
                (0,),
                (0, 0)
                ]
        for r in ranges:
            mode.setOperandsRange(no=r)
            parser = clap.parser.Parser(mode)
            for argv in argvariants:
                parser.feed(argv)
                if DEBUG: print('checking range {0} with input: {1}'.format(r, parser._getoperands()))
                checker = clap.checker.RedChecker(parser)
                checker._checkoperandsrange()
            for argv in failvariants:
                parser.feed(argv)
                if DEBUG: print('fail checking range {0} with input: {1}'.format(r, parser._getoperands()))
                checker = clap.checker.RedChecker(parser)
                self.assertRaises(clap.errors.InvalidOperandRangeError, checker._checkoperandsrange)

    def testOperandsRangeNotCompatibleWithListOfTypesInvalidLeast(self):
        mode = clap.mode.RedMode()
        ranges = [
                (3, 4),
                (-3,),
                ]
        for r in ranges:
            mode.setOperandsRange(no=r)
            mode.setOperandsTypes(types=['int', 'int'])
            parser = clap.parser.Parser(mode).feed([])
            checker = clap.checker.RedChecker(parser)
            self.assertRaises(clap.errors.UIDesignError, checker._checkoperandscompat)

    def testOperandsRangeNotCompatibleWithListOfTypesInvalidMost(self):
        mode = clap.mode.RedMode()
        ranges = [
                (2, 5),
                (5,),
                ]
        for r in ranges:
            mode.setOperandsRange(no=r)
            mode.setOperandsTypes(types=['int', 'int'])
            parser = clap.parser.Parser(mode).feed([])
            checker = clap.checker.RedChecker(parser)
            self.assertRaises(clap.errors.UIDesignError, checker._checkoperandscompat)

    def testOperandsRangeNotCompatibleWithListOfTypesInvalidMostListOfTypesTooLong(self):
        mode = clap.mode.RedMode()
        mode.setOperandsRange(no=[2, 3])
        mode.setOperandsTypes(types=['int', 'int', 'int', 'int'])
        parser = clap.parser.Parser(mode).feed([])
        checker = clap.checker.RedChecker(parser)
        self.assertRaises(clap.errors.UIDesignError, checker._checkoperandscompat)

    def testOperandsRangeNotCompatibleWithListOfTypesInvalidExact(self):
        mode = clap.mode.RedMode()
        ranges = [
                (0, 0),
                (5, 5),
                ]
        for r in ranges:
            mode.setOperandsRange(no=r)
            mode.setOperandsTypes(types=['int', 'int', 'int', 'int'])
            parser = clap.parser.Parser(mode).feed([])
            checker = clap.checker.RedChecker(parser)
            self.assertRaises(clap.errors.UIDesignError, checker._checkoperandscompat)

    def testOperandsRangeCompatibleWithListOfTypes(self):
        mode = clap.mode.RedMode()
        mode.setOperandsRange(no=[2, 4])
        mode.setOperandsTypes(types=['int', 'int'])
        parser = clap.parser.Parser(mode).feed([])
        checker = clap.checker.RedChecker(parser)
        checker._checkoperandscompat()

    def testRangeBasedOnlyOnListOfTypes(self):
        argvariants = [
                ['--foo', '-b', '0', '1'],
                ['--foo', '-b', '0', '1', '2', '3'],
                ['--foo', '-b', '0', '1', '2', '3', '4', '5'],
                ]
        failvariants = [
                ['--foo', '-b'],
                ['--foo', '-b', '0'],
                ['--foo', '-b', '0', '1', '2'],
                ['--foo', '-b', '0', '1', '2', '3', '4'],
                ]
        mode = clap.mode.RedMode()
        mode.addLocalOption(clap.option.Option(short='f', long='foo'))
        mode.addLocalOption(clap.option.Option(short='b', long='bar'))
        mode.setOperandsTypes(types=['int', 'int'])
        parser = clap.parser.Parser(mode)
        for argv in argvariants:
            parser.feed(argv)
            if DEBUG: print('checking range based only on list of types ({0}) with input: {1}'.format(len(mode.getOperandsTypes()), parser._getoperands()))
            checker = clap.checker.RedChecker(parser)
            checker._checkoperandsrange()
        for argv in failvariants:
            parser.feed(argv)
            if DEBUG: print('fail checking range based only on list of types ({0}) with input: {1}'.format(len(mode.getOperandsTypes()), parser._getoperands()))
            checker = clap.checker.RedChecker(parser)
            self.assertRaises(clap.errors.InvalidOperandRangeError, checker._checkoperandsrange)


if __name__ == '__main__':
    unittest.main()
