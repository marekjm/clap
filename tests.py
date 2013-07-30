#/usr/bin/env python3

import unittest
import warnings

import clap


#   enable debugging output which is basically huge number of print() calls
DEBUG = False


class BaseTests(unittest.TestCase):
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


class ParserTests(unittest.TestCase):
    def test(self):
        warnings.warn('not implemented')


if __name__ == '__main__': unittest.main()
