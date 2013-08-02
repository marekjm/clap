#/usr/bin/env python3

import unittest
import warnings

import clap


#   enable debugging output which is basically huge number of print() calls
DEBUG = False


class BaseTests(unittest.TestCase):
    def testAddingNewOption(self):
        base = clap.base.Base([])
        base.add(short='f', long='foo', argument=str,
                 required=True, not_with=['-s'],
                 requires=['--bar'], needs=['--baz', '--bax'],
                 conflicts=['--bay'])
        option0 = clap.option.Option(short='f', long='foo',
                                     argument=str, required=True, not_with=['-s'],
                                     requires=['--bar'], needs=['--baz', '--bax'],
                                     conflicts=['--bay'])
        option1 = clap.option.Option(short='b', long='bar',
                                     argument=int,
                                     needs=['--baz', '--bax'])
        self.assertIn(option0, base.options)
        self.assertNotIn(option1, base.options)

    def testRemovingOption(self):
        base = clap.base.Base([])
        base.add(short='f', long='foo', argument=str,
                 required=True, not_with=['-s'],
                 requires=['--bar'], needs=['--baz', '--bax'],
                 conflicts=['--bay'])
        option0 = clap.option.Option(short='f', long='foo',
                                     argument=str, required=True, not_with=['-s'],
                                     requires=['--bar'], needs=['--baz', '--bax'],
                                     conflicts=['--bay'])
        option1 = clap.option.Option(short='b', long='bar',
                                     argument=int,
                                     needs=['--baz', '--bax'])
        base.add(short='b', long='bar', argument=int, needs=['--baz', '--bax'])
        self.assertIn(option0, base.options)
        self.assertIn(option1, base.options)
        base.remove(short='b')
        self.assertIn(option0, base.options)
        self.assertNotIn(option1, base.options)

    def testGettingInput(self):
        argv = ['--foo', '--bar', 'baz', 'bax']
        base = clap.base.Base(argv)
        base.add(long='foo')
        base.add(long='bar', argument=str)
        self.assertEqual(['--foo', '--bar', 'baz'], base._getinput())

    def testGettingInputWithBreakerPresent(self):
        argv = ['--foo', '--', '--bar', 'baz', 'bax']
        base = clap.base.Base(argv)
        base.add(long='foo')
        base.add(long='bar', argument=str)
        self.assertEqual(['--foo'], base._getinput())

    def testCheckingIfOptionIsInInputUsingString(self):
        argv = ['--foo', '--bar', 'baz']
        base = clap.base.Base(argv)
        base.add(short='f', long='foo')
        base.add(short='b', long='bar', argument=str)
        self.assertEqual(True, base._ininput(string='--foo'))
        self.assertEqual(True, base._ininput(string='-b'))

    def testCheckingIfOptionIsInInputUsingOptionObject(self):
        argv = ['-f', '--bar', 'baz']
        base = clap.base.Base(argv)
        foo = clap.option.Option(short='f', long='foo')
        bar = clap.option.Option(short='b', long='bar', argument=str)
        base._append(foo)
        base._append(bar)
        self.assertEqual(True, base._ininput(option=foo))
        self.assertEqual(True, base._ininput(option=bar))

    def testCheckingIfOptionIsInInputWithBreaker(self):
        argv = ['--foo', '--', '--bar', 'baz']
        base = clap.base.Base(argv)
        base.add(long='foo')
        base.add(long='bar', argument=str)
        self.assertEqual(True, base._ininput(string='--foo'))
        self.assertEqual(False, base._ininput(string='--bar'))

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
        for opt, result in tests:
            if DEBUG: print(opt, result)
            self.assertEqual(clap.base.lookslikeopt(opt), result)


class FormatterTests(unittest.TestCase):
    def testSplittingEqualSignedOptions(self):
        argv = ['--foo=bar', '--', '--baz=bax']
        f = clap.formater.Formater(argv)
        f._splitequal()
        if DEBUG: print('\'{0}\' -> \'{1}\''.format(' '.join(argv), ' '.join(f.formated)))
        self.assertEqual(f.formated, ['--foo', 'bar', '--', '--baz=bax'])

    def testSplittingConnectedShortOptions(self):
        argv = ['-abc', '--', '-def']
        f = clap.formater.Formater(argv)
        f._splitshorts()
        if DEBUG: print('\'{0}\' -> \'{1}\''.format(' '.join(argv), ' '.join(f.formated)))
        self.assertEqual(f.formated, ['-a', '-b', '-c', '--', '-def'])

    def testGeneralFormating(self):
        argv = ['-abc', 'eggs', '--bar', '--ham', 'good', '--food=spam', '--', '--bax=bay']
        f = clap.formater.Formater(argv)
        f.format()
        if DEBUG: print('\'{0}\' -> \'{1}\''.format(' '.join(argv), ' '.join(f.formated)))
        self.assertEqual(f.formated,
                         ['-a', '-b', '-c', 'eggs', '--bar', '--ham', 'good', '--food', 'spam', '--', '--bax=bay'])


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

    def testTyping(self):
        o = clap.option.Option(short='f', argument=int)
        self.assertEqual(int, o.type())
        p = clap.option.Option(short='f')
        self.assertEqual(None, p.type())

    def testMatching(self):
        o = clap.option.Option(short='f', long='foo')
        self.assertEqual(True, o.match('-f'))
        self.assertEqual(True, o.match('--foo'))

    def testAliases(self):
        o = clap.option.Option(short='f', long='foo')
        self.assertEqual('--foo', o._alias('-f'))
        self.assertEqual('-f', o._alias('--foo'))
        self.assertRaises(NameError, o._alias, '--bar')


class CheckerTests(unittest.TestCase):
    def testUnrecognizedOptions(self):
        argv = ['--foo', '--bar', '--baz']
        parser = clap.base.Base(argv)
        parser.add(long='foo')
        parser.add(long='baz')
        checker = clap.checker.Checker(parser)
        self.assertRaises(clap.errors.UnrecognizedOptionError, checker._checkunrecognized)

    def testArgumentNotGivenAtTheEnd(self):
        argv = ['--bar', '--foo']
        parser = clap.base.Base(argv)
        parser.add(long='foo', argument=str)
        parser.add(long='bar')
        checker = clap.checker.Checker(parser)
        self.assertRaises(clap.errors.MissingArgumentError, checker._checkarguments)

    def testArgumentNotGivenAtTheEndBecauseOfBreaker(self):
        argv = ['--bar', '--foo', '--', 'baz']
        parser = clap.base.Base(argv)
        parser.add(long='foo', argument=str)
        parser.add(long='bar')
        checker = clap.checker.Checker(parser)
        self.assertRaises(clap.errors.MissingArgumentError, checker._checkarguments)

    def testInvalidArgumentType(self):
        argv = ['--bar', '--foo', 'baz']
        parser = clap.base.Base(argv)
        parser.add(long='foo', argument=int)
        parser.add(long='bar')
        checker = clap.checker.Checker(parser)
        self.assertRaises(clap.errors.InvalidArgumentTypeError, checker._checkarguments)

    def testAnotherOptionGivenAsArgument(self):
        argv = ['--foo', '--bar']
        parser = clap.base.Base(argv)
        parser.add(long='foo', argument=int)
        parser.add(long='bar')
        checker = clap.checker.Checker(parser)
        self.assertRaises(clap.errors.MissingArgumentError, checker._checkarguments)

    def testRequiredOptionNotFound(self):
        argv = ['--bar']
        parser = clap.base.Base(argv)
        parser.add(long='foo', required=True)
        parser.add(long='bar')
        checker = clap.checker.Checker(parser)
        self.assertRaises(clap.errors.RequiredOptionNotFoundError, checker._checkrequired)

    def testRequiredOptionNotFoundBecauseOfBreaker(self):
        argv = ['--bar', '--', '--foo']
        parser = clap.base.Base(argv)
        parser.add(long='foo', required=True)
        parser.add(long='bar')
        checker = clap.checker.Checker(parser)
        if DEBUG: print(parser._getinput())
        self.assertRaises(clap.errors.RequiredOptionNotFoundError, checker._checkrequired)

    def testRequiredNotWithAnotherOption(self):
        argv = ['--bar']
        parser = clap.base.Base(argv)
        parser.add(long='foo', required=True, not_with=['--bar'])
        parser.add(short='b', long='bar')
        checker = clap.checker.Checker(parser)
        checker._checkrequired()

    def testRequiredNotWithAnotherOptionNotFoundBecauseOfBreaker(self):
        argv = ['--baz', '--', '-b']
        parser = clap.base.Base(argv)
        parser.add(long='foo', required=True, not_with=['--bar'])
        parser.add(short='b', long='bar')
        parser.add(long='baz')
        checker = clap.checker.Checker(parser)
        if DEBUG: print(parser._getinput())
        self.assertRaises(clap.errors.RequiredOptionNotFoundError, checker._checkrequired)

    def testOptionRequiredByAnotherOption(self):
        argv = ['--foo', '--bar', '--baz']
        parser = clap.base.Base(argv)
        parser.add(long='foo', requires=['--bar', '--baz'])
        parser.add(long='bar')
        parser.add(long='baz')
        checker = clap.checker.Checker(parser)
        if DEBUG: print(parser._getinput())
        checker._checkrequires()

    def testOptionRequiredByAnotherOptionNotFound(self):
        argv = ['--foo', '--bar']
        parser = clap.base.Base(argv)
        parser.add(long='foo', requires=['--bar', '--baz'])
        parser.add(long='bar')
        parser.add(long='baz')
        checker = clap.checker.Checker(parser)
        if DEBUG: print(parser._getinput())
        self.assertRaises(clap.errors.RequiredOptionNotFoundError, checker._checkrequires)

    def testOptionRequiredByAnotherOptionNotFoundBecauseOfBreaker(self):
        argv = ['--foo', '--bar', '--', '--baz']
        parser = clap.base.Base(argv)
        parser.add(long='foo', requires=['--bar', '--baz'])
        parser.add(long='bar')
        parser.add(long='baz')
        checker = clap.checker.Checker(parser)
        if DEBUG: print(parser._getinput())
        self.assertRaises(clap.errors.RequiredOptionNotFoundError, checker._checkrequires)

    def testOptionNeededByAnotherOption(self):
        argv_both = ['--bar', '--foo', '--baz']
        argv_only_bar = ['--foo', '--bar', '42']
        argv_only_baz = ['--baz', '--foo']
        parser = clap.base.Base()
        parser.add(long='foo', needs=['--bar', '--baz'])
        parser.add(long='bar', argument=int)
        parser.add(long='baz')
        for argv in [argv_both, argv_only_bar, argv_only_baz]:
            parser._feed(argv)
            checker = clap.checker.Checker(parser)
            if DEBUG: print(parser._getinput())
            checker._checkneeds()

    def testOptionNeededByAnotherOptionNotFound(self):
        argv = ['--foo']
        parser = clap.base.Base()
        parser.add(long='foo', needs=['--bar', '--baz'])
        parser.add(long='bar', argument=int)
        parser.add(long='baz')
        parser._feed(argv)
        checker = clap.checker.Checker(parser)
        if DEBUG: print(parser._getinput())
        self.assertRaises(clap.errors.NeededOptionNotFoundError, checker._checkneeds)

    def testOptionNeededByAnotherOptionNotFoundBecauseOfBreaker(self):
        argv = ['--foo', '--', '--bar']
        parser = clap.base.Base()
        parser.add(long='foo', needs=['--bar', '--baz'])
        parser.add(long='bar', argument=int)
        parser.add(long='baz')
        parser._feed(argv)
        checker = clap.checker.Checker(parser)
        if DEBUG: print(parser._getinput())
        self.assertRaises(clap.errors.NeededOptionNotFoundError, checker._checkneeds)

    def testConflicts(self):
        argv = ['--foo', '--bar']
        parser = clap.base.Base(argv=argv)
        parser.add(long='foo', conflicts=['--bar'])
        parser.add(long='bar')
        checker = clap.checker.Checker(parser)
        if DEBUG: print(parser._getinput())
        self.assertRaises(clap.errors.ConflictingOptionsError, checker._checkconflicts)

    def testConflictsNotRaisedBecauseOfBreaker(self):
        argv = ['--foo', '--', '--bar']
        parser = clap.base.Base()
        parser.add(long='foo', conflicts=['--bar'])
        parser.add(long='bar')
        parser._feed(argv)
        checker = clap.checker.Checker(parser)
        if DEBUG: print(parser._getinput())
        checker._checkconflicts()


class ParserTests(unittest.TestCase):
    def testShortOptionsWithoutArguments(self):
        argv = ['-a', '-b', '-c', 'd', 'e', 'f']
        p = clap.parser.Parser(argv)
        p.add(short='a')
        p.add(short='b')
        p.add(short='c')
        p.parse()
        self.assertEqual({'-a': None, '-b': None, '-c': None}, p.parsed)
        self.assertEqual(['d', 'e', 'f'], p.arguments)

    def testShortOptionsWithArguments(self):
        argv = ['-s', 'eggs', '-i', '42', '-f', '4.2', 'foo']
        p = clap.parser.Parser(argv)
        p.add(short='s', argument=str)
        p.add(short='i', argument=int)
        p.add(short='f', argument=float)
        p.parse()
        self.assertEqual({'-s': 'eggs', '-i': 42, '-f': 4.2}, p.parsed)
        self.assertEqual(['foo'], p.arguments)

    def testLongOptionsWithoutArguments(self):
        argv = ['--foo', '--bar', '--baz', 'bax']
        p = clap.parser.Parser(argv)
        p.add(long='foo')
        p.add(long='bar')
        p.add(long='baz')
        p.parse()
        self.assertEqual(None, p.get('--foo'))
        self.assertEqual(None, p.get('--bar'))
        self.assertEqual(None, p.get('--baz'))
        self.assertEqual(['bax'], p.arguments)

    def testLongOptionsWithArguments(self):
        argv = ['--str', 'eggs', '--int', '42', '--float', '4.2']
        p = clap.parser.Parser(argv)
        p.add(long='str', argument=str)
        p.add(long='int', argument=int)
        p.add(long='float', argument=float)
        p.parse()
        self.assertEqual('eggs', p.get('--str'))
        self.assertEqual(42, p.get('--int'))
        self.assertEqual(4.2, p.get('--float'))

    @unittest.skip('will be implemented in version 0.6.4')
    def testOptionsWithMultipleArguments(self):
        argv = ['--foo', 'spam', '42', '3.14']
        p = clap.parser.Parser(argv)
        p.add(short='f', long='foo', argument=[str, int, float])
        p.parse()
        self.assertEqual(('spam', 42, 3.14), p.get('-f'))

    def testStopingAtBreaker(self):
        argv = ['--foo', '-s', 'eggs', '--int', '42', '--', '-f', '4.2']
        p = clap.parser.Parser(argv)
        p.add(long='foo')
        p.add(long='int', argument=int)
        p.add(short='s', argument=str)
        p.add(short='f', argument=float)
        p.parse()
        self.assertEqual({'--int': 42, '-s': 'eggs', '--foo': None}, p.parsed)
        self.assertEqual(['-f', '4.2'], p.arguments)


class ModesTests(unittest.TestCase):
    def test(self):
        warnings.warn('not implemented')


if __name__ == '__main__': unittest.main()
