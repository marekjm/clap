#/usr/bin/env python3

"""Unit testing suite for RedCLAP library.
"""

import os
import shutil
import sys
import unittest
import warnings

# ensure test always fetch CLAP from development directory
sys.path.insert(0, '.')

import clap


# enable debugging output which is basically huge number of print() calls
DEBUG = True
# enable information about TODOs in code (if any)
TODOS = False


def getTestCommand():
    command = clap.mode.RedCommand()
    command.addLocalOption(clap.option.Option(short='f', long='foo'))
    command.addLocalOption(clap.option.Option(short='b', long='bar'))
    command.addLocalOption(clap.option.Option(short='B', long='baz'))
    return command


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


class CommandTests(unittest.TestCase):
    def testAddingLocalOptions(self):
        command = clap.mode.RedCommand()
        command.addLocalOption(clap.option.Option(short='a', long='all'))
        self.assertTrue(command.accepts('-a'))
        self.assertTrue(command.accepts('--all'))
        self.assertEqual('-a', command.alias('--all'))
        self.assertEqual('--all', command.alias('-a'))

    def testAddingGlobalOptions(self):
        command = clap.mode.RedCommand()
        command.addCommand('foo', clap.mode.RedCommand())
        command.addCommand('bar', clap.mode.RedCommand())
        command.addGlobalOption(clap.option.Option(short='v', long='verbose')).propagate()
        self.assertTrue(command.accepts('--verbose'))
        self.assertTrue(command.getCommand('foo').accepts('--verbose'))
        self.assertTrue(command.getCommand('bar').accepts('--verbose'))

    def testAddingCommands(self):
        command = clap.mode.RedCommand()
        command.addCommand('foo', clap.mode.RedCommand())
        command.addCommand('bar', clap.mode.RedCommand())
        self.assertTrue(command.hasCommand('foo'))
        self.assertTrue(command.hasCommand('bar'))

    def testRemovingLocalOption(self):
        """Be careful when manually building interfaces and
        removing options.
        This may lead to UIDesignError-s being raised!
        """
        command = clap.mode.RedCommand()
        command.addLocalOption(clap.option.Option(short='f', long='foo'))
        self.assertTrue(command.accepts('--foo'))
        command.removeLocalOption(name='--foo')
        self.assertFalse(command.accepts('--foo'))

    def testRemovingGlobalOption(self):
        """Be careful when manually building interfaces and
        removing options.
        This may lead to UIDesignError-s being raised!
        """
        command = clap.mode.RedCommand()
        command.addGlobalOption(clap.option.Option(short='f', long='foo'))
        self.assertTrue(command.accepts('--foo'))
        command.removeGlobalOption(name='--foo')
        self.assertFalse(command.accepts('--foo'))

    def testAliases(self):
        command = clap.mode.RedCommand()
        command.addLocalOption(clap.option.Option(short='a'))
        command.addLocalOption(clap.option.Option(short='b', long='bar'))
        command.addLocalOption(clap.option.Option(long='baz'))
        self.assertEqual('', command.alias('-a'))
        self.assertEqual('-b', command.alias('--bar'))
        self.assertEqual('--bar', command.alias('-b'))
        self.assertEqual('', command.alias('--baz'))

    def testShortenedCommandNamesExpandProperly(self):
        command = clap.mode.RedCommand()
        command.addCommand('foo', clap.mode.RedCommand())
        command.addCommand('bar', clap.mode.RedCommand())
        self.assertTrue(command.hasCommand('foo'))
        self.assertTrue(command.hasCommand('bar'))
        self.assertEqual('foo', command.expandCommandName('f'))
        self.assertEqual('bar', command.expandCommandName('b'))
        self.assertTrue(command.hasCommand(command.expandCommandName('f')))
        self.assertTrue(command.hasCommand(command.expandCommandName('b')))

    def testShortenedCommandNamesExpandAmbiguously(self):
        command = clap.mode.RedCommand()
        command.addCommand('foo', clap.mode.RedCommand())
        command.addCommand('far', clap.mode.RedCommand())
        self.assertRaises(clap.errors.AmbiguousCommandError, command.expandCommandName, 'f')
        self.assertEqual('foo', command.expandCommandName('fo'))
        self.assertEqual('far', command.expandCommandName('fa'))

    def testShortenedCommandNamesNotFound(self):
        command = clap.mode.RedCommand()
        command.addCommand('foo', clap.mode.RedCommand())
        command.addCommand('far', clap.mode.RedCommand())
        self.assertRaises(clap.errors.UnrecognizedCommandError, command.expandCommandName, 'b')

    def testShortenedCommandNamesDoNotShadow(self):
        command = clap.mode.RedCommand()
        command.addCommand('foo', clap.mode.RedCommand())
        command.addCommand('foobar', clap.mode.RedCommand())
        self.assertEqual('foo', command.expandCommandName('foo'))
        self.assertEqual('foobar', command.expandCommandName('foob'))


class ParserGeneralTests(unittest.TestCase):
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
        command = clap.mode.RedCommand()
        command.addLocalOption(clap.option.Option(short='f', long='foo'))
        command.addLocalOption(clap.option.Option(short='b', long='bar'))
        command.addLocalOption(clap.option.Option(short='B', long='baz'))
        parser = clap.parser.Parser(command)
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
        command = clap.mode.RedCommand()
        command.addLocalOption(clap.option.Option(short='f', long='foo'))
        command.addLocalOption(clap.option.Option(short='b', long='bar'))
        command.addLocalOption(clap.option.Option(short='B', long='baz'))
        command.addLocalOption(clap.option.Option(short='p', long='point', arguments=['int', 'int']))
        parser = clap.parser.Parser(command)
        for argv, input, operands in argvariants:
            if input is None: input = argv[:]
            if operands is None: operands = argv[:]
            parser.feed(argv)
            self.assertEqual(input, parser._getinput())
            self.assertEqual(operands, parser._getoperands())

    def testGettingInputWithGlobalOption(self):
        command = clap.mode.RedCommand().setOperandsRange(no=[0, 0])
        command.addLocalOption(clap.option.Option(short='l', long='local'))
        command.addGlobalOption(clap.option.Option(short='g', long='global', arguments=['int']))
        child = clap.mode.RedCommand()
        command.addCommand(name='child', command=child)
        command.propagate()
        argv = ['--local', '--global', '42', 'child']
        parser = clap.parser.Parser(command).feed(argv)
        input = ['--local', '--global', '42']
        operands = []
        nested = ['child']
        self.assertEqual(input, parser._getinput())
        self.assertEqual(operands, parser._getheuroperands()[0])
        self.assertEqual(nested, parser._getheuroperands()[1])

    def testCheckingIfOptionIsInInput(self):
        argvariants = [
                ['--foo', '--bar'],
                ['-f', '--bar', 'spam', '--baz'],
                ['-f', '--bar', '0', '--baz'],
                ['-f', '--bar', '--', '--baz'],
                ]
        command = clap.mode.RedCommand()
        foo = clap.option.Option(short='f', long='foo')
        bar = clap.option.Option(short='b', long='bar')
        baz = clap.option.Option(short='B', long='baz')
        command.addLocalOption(foo).addLocalOption(bar).addLocalOption(baz)
        parser = clap.parser.Parser(command)
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


class ParserParsingTests(unittest.TestCase):
    def testParsingNoCommandNoOperands(self):
        command = clap.mode.RedCommand()
        command.addLocalOption(clap.option.Option(short='t', long='test'))
        command.addLocalOption(clap.option.Option(short='a', long='answer', arguments=['str', 'int']))
        argv = ['-a', 'is', '42', '--test']
        parser = clap.parser.Parser(command).feed(argv)
        ui = parser.parse().ui().finalise()
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
        self.assertEqual('', str(ui))

    def testParsingNoCommand(self):
        command = clap.mode.RedCommand()
        command.addLocalOption(clap.option.Option(short='t', long='test'))
        command.addLocalOption(clap.option.Option(short='a', long='answer', arguments=['str', 'int']))
        command.setOperandsRange(no=[2, 2])
        argv = ['-a', 'is', '42', '--test', 'foo', 'bar']
        parser = clap.parser.Parser(command).feed(argv)
        ui = parser.parse().ui().finalise()
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
        self.assertEqual('', str(ui))

    def testParsingNoOperandsCommand(self):
        command = clap.mode.RedCommand()
        command.addLocalOption(clap.option.Option(short='t', long='test'))
        command.addLocalOption(clap.option.Option(short='a', long='answer', arguments=['str', 'int']))
        child = clap.mode.RedCommand()
        child.addLocalOption(clap.option.Option(short='s', long='spam'))
        command.addCommand(name='child', command=child)
        argv = ['-a', 'is', '42', '--test', 'child', '--spam']
        parser = clap.parser.Parser(command).feed(argv)
        ui = parser.parse().ui().finalise()
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
        self.assertEqual('', str(ui))
        ui = ui.down()
        self.assertEqual(None, ui.get('-s'))
        self.assertEqual(None, ui.get('--spam'))
        self.assertIn('-s', ui)
        self.assertIn('--spam', ui)
        self.assertEqual(0, len(ui))
        self.assertEqual([], ui.operands())
        self.assertEqual('child', str(ui))

    def testParsingOperandsAndCommand(self):
        command = clap.mode.RedCommand()
        command.addLocalOption(clap.option.Option(short='t', long='test'))
        command.addLocalOption(clap.option.Option(short='a', long='answer', arguments=['str', 'int']))
        command.setOperandsRange(no=[1, 1])
        child = clap.mode.RedCommand()
        child.addLocalOption(clap.option.Option(short='s', long='spam'))
        command.addCommand(name='child', command=child)
        argv = ['-a', 'is', '42', '--test', 'alpha', 'child', '--spam']
        parser = clap.parser.Parser(command).feed(argv)
        ui = parser.parse().ui().finalise()
        self.assertEqual(('is', 42), ui.get('-a'))
        self.assertEqual(('is', 42), ui.get('--answer'))
        self.assertEqual(None, ui.get('-t'))
        self.assertEqual(None, ui.get('--test'))
        self.assertIn('-a', ui)
        self.assertIn('--answer', ui)
        self.assertIn('-t', ui)
        self.assertIn('--test', ui)
        self.assertEqual(1, len(ui))
        self.assertEqual(['alpha'], ui.operands())
        self.assertEqual('', str(ui))
        ui = ui.down()
        self.assertEqual(None, ui.get('-s'))
        self.assertEqual(None, ui.get('--spam'))
        self.assertIn('-s', ui)
        self.assertIn('--spam', ui)
        self.assertEqual(0, len(ui))
        self.assertEqual([], ui.operands())
        self.assertEqual('child', str(ui))

    def testParsingWithShortenedCommand(self):
        command = clap.mode.RedCommand()
        child = clap.mode.RedCommand()
        child.addLocalOption(clap.option.Option(short='s', long='spam'))
        command.addCommand(name='child', command=child)
        argv = ['ch', '--spam']
        parser = clap.parser.Parser(command).feed(argv)
        ui = parser.parse().ui().finalise()
        self.assertEqual('', str(ui))
        ui = ui.down()
        self.assertEqual(None, ui.get('-s'))
        self.assertEqual(None, ui.get('--spam'))
        self.assertIn('-s', ui)
        self.assertIn('--spam', ui)
        self.assertEqual(0, len(ui))
        self.assertEqual([], ui.operands())
        self.assertEqual('child', str(ui))


class ParserOptionsTests(unittest.TestCase):
    def testFeedingArgsToParser(self):
        command = clap.mode.RedCommand()
        parser = clap.parser.Parser(command)
        args = ['-a', '--foo', 'bar']
        parser.feed(args)
        self.assertEqual(args, parser.getargs())

    def testParsingBareOption(self):
        command = clap.mode.RedCommand()
        command.addLocalOption(clap.option.Option(short='v', long='verbose'))
        parser = clap.parser.Parser(command).feed(['--verbose']).parse()
        state, ui = parser.state(), parser.ui()
        check_opts = ['--verbose', '-v']
        for opt in check_opts:
            self.assertTrue(opt in state['options'])
            self.assertTrue(opt in ui)
            self.assertEqual(None, state['options'][opt])
            self.assertEqual(None, ui.get(opt))

    def testParsingBareOptions(self):
        command = clap.mode.RedCommand()
        command.addLocalOption(clap.option.Option(short='v', long='verbose'))
        command.addLocalOption(clap.option.Option(short='d', long='debug'))
        parser = clap.parser.Parser(command).feed(['--verbose', '--debug']).parse()
        state, ui = parser.state(), parser.ui()
        check_opts = ['--verbose', '-v', '--debug', '-d']
        for opt in check_opts:
            self.assertTrue(opt in state['options'])
            self.assertTrue(opt in ui)
            self.assertEqual(None, state['options'][opt])
            self.assertEqual(None, ui.get(opt))

    def testParsingPluralOptionsWithoutArguments(self):
        command = clap.mode.RedCommand()
        command.addLocalOption(clap.option.Option(short='v', long='verbose', plural=True))
        parser = clap.parser.Parser(command).feed(['--verbose', '--verbose', '-v']).parse()
        state, ui = parser.state(), parser.ui()
        check_opts = [
                ('--verbose', 3),
                ('-v', 3),
                ]
        for opt, value in check_opts:
            self.assertTrue(opt in state['options'])
            self.assertTrue(opt in ui)
            self.assertEqual(value, state['options'][opt])
            self.assertEqual(value, ui.get(opt))

    def testParsingPluralOptionsWithArguments(self):
        command = clap.mode.RedCommand()
        command.addLocalOption(clap.option.Option(short='f', long='foo', plural=True, arguments=['int']))
        parser = clap.parser.Parser(command).feed(['--foo', '0', '-f', '1']).parse()
        state, ui = parser.state(), parser.ui()
        for opt in ['-f', '--foo']:
            self.assertTrue(opt in state['options'])
            self.assertTrue(opt in ui)
            self.assertEqual([[0], [1]], state['options'][opt])
            self.assertEqual([(0,), (1,)], ui.get(opt))

    def testParsingOptionWithOneArgument(self):
        command = clap.mode.RedCommand()
        command.addLocalOption(clap.option.Option(short='f', long='foo', arguments=['str']))
        parser = clap.parser.Parser(command).feed(['--foo', 'spam']).parse()
        state, ui = parser.state(), parser.ui()
        for opt in ['-f', '--foo']:
            self.assertTrue(opt in state['options'])
            self.assertTrue(opt in ui)
            self.assertEqual(('spam',), state['options'][opt])
            self.assertEqual('spam', ui.get(opt))

    def testParsingOptionWithMultipleArguments(self):
        command = clap.mode.RedCommand()
        command.addLocalOption(clap.option.Option(short='f', long='foo', arguments=['str', 'str']))
        parser = clap.parser.Parser(command).feed(['--foo', 'spam', 'eggs']).parse()
        state, ui = parser.state(), parser.ui()
        for opt in ['-f', '--foo']:
            self.assertTrue(opt in state['options'])
            self.assertTrue(opt in ui)
            self.assertEqual(('spam', 'eggs'), state['options'][opt])
            self.assertEqual(('spam', 'eggs'), ui.get(opt))

    def testParsingStopsOnFirstNonOption(self):
        command = clap.mode.RedCommand()
        command.addLocalOption(clap.option.Option(short='f', long='foo', arguments=['str', 'str']))
        parser = clap.parser.Parser(command).feed(['spam', '--foo']).parse()
        state, ui = parser.state(), parser.ui()
        self.assertTrue('--foo' not in state['options'])
        self.assertTrue('--foo' not in ui)
        self.assertEqual(['spam', '--foo'], state['operands'])
        self.assertEqual(['spam', '--foo'], ui.operands())

    def testParsingStopsOnBreaker(self):
        command = clap.mode.RedCommand()
        command.addLocalOption(clap.option.Option(short='f', long='foo', arguments=['str', 'str']))
        parser = clap.parser.Parser(command).feed(['--', '--foo']).parse()
        state, ui = parser.state(), parser.ui()
        self.assertTrue('--foo' not in state['options'])
        self.assertTrue('--foo' not in ui)
        self.assertEqual(['--foo'], state['operands'])
        self.assertEqual(['--foo'], ui.operands())

    def testParsingShortOptions(self):
        args = ['-a', '-b', '-c', 'd', 'e', 'f']
        command = clap.mode.RedCommand()
        command.addLocalOption(clap.option.Option(short='a'))
        command.addLocalOption(clap.option.Option(short='b'))
        command.addLocalOption(clap.option.Option(short='c'))
        parser = clap.parser.Parser(command).feed(args).parse()
        state, ui = parser.state(), parser.ui()
        for opt in ['-a', '-b', '-c']:
            self.assertIn(opt, state['options'])
            self.assertIn(opt, ui)
            self.assertIs(None, state['options'][opt])
            self.assertIs(None, ui.get(opt))
        self.assertEqual(['d', 'e', 'f'], state['operands'])
        self.assertEqual(['d', 'e', 'f'], ui.operands())

    def testShortOptionsWithArguments(self):
        args = ['-s', 'eggs', '-i', '42', '-f', '4.2', '--', 'foo']
        command = clap.mode.RedCommand()
        command.addLocalOption(clap.option.Option(short='s', arguments=[str]))
        command.addLocalOption(clap.option.Option(short='i', arguments=[int]))
        command.addLocalOption(clap.option.Option(short='f', arguments=[float]))
        parser = clap.parser.Parser(command).feed(args).parse()
        state, ui = parser.state(), parser.ui()
        check_opts = [
                ('-s', 'eggs'),
                ('-i', 42),
                ('-f', 4.2),
                ]
        for opt, value in check_opts:
            self.assertEqual(value, ui.get(opt, tuplise=False))
            self.assertEqual((value,), state['options'][opt])
        self.assertEqual(['foo'], ui.operands())
        self.assertEqual(['foo'], state['operands'])


class ParserImpliedOptionsParsingTests(unittest.TestCase):
    def testOptionImplyingOptionWhichIsUnknownRaisesAnExceptionDuringParsing(self):
        args = ['--spam']
        command = clap.mode.RedCommand()
        command.addLocalOption(clap.option.Option(short='s', long='spam', implies=['--eggs']))
        self.assertRaises(clap.errors.UIDesignError, clap.parser.Parser(command).feed(args).parse)

    def testOptionImplyingOptionWhichRequiresArgumentsButDoesNotProvideDefaultsRaisesAnExceptionDuringParsing(self):
        args = ['--spam']
        command = clap.mode.RedCommand()
        command.addLocalOption(clap.option.Option(short='s', long='spam', implies=['--eggs']))
        command.addLocalOption(clap.option.Option(short='e', long='eggs', arguments=['int', 'int']))
        self.assertRaises(clap.errors.UIDesignError, clap.parser.Parser(command).feed(args).parse)

    def testOptionImplyingOptionWhichRequiresArgumentsButProvidesInsufficientTooBigNumberOfDefaultsRaisesAnExceptionDuringParsing(self):
        args = ['--spam']
        command = clap.mode.RedCommand()
        command.addLocalOption(clap.option.Option(short='s', long='spam', implies=['--eggs']))
        command.addLocalOption(clap.option.Option(short='e', long='eggs', arguments=['int', 'int'], defaults=['42', '24', '69']))
        self.assertRaises(clap.errors.UIDesignError, clap.parser.Parser(command).feed(args).parse)

    def testOptionImplyingOptionWhichRequiresArgumentsButProvidesInsufficientTooSmallNumberOfDefaultsRaisesAnExceptionDuringParsing(self):
        args = ['--spam']
        command = clap.mode.RedCommand()
        command.addLocalOption(clap.option.Option(short='s', long='spam', implies=['--eggs']))
        command.addLocalOption(clap.option.Option(short='e', long='eggs', arguments=['int', 'int'], defaults=['42']))
        self.assertRaises(clap.errors.UIDesignError, clap.parser.Parser(command).feed(args).parse)

    def testOptionImplyingOptionWhichConflictsWithAlreadyProvidedOptionRaisesAnExceptionDuringParsing(self):
        args = ['--no-spam', '--spam', ]
        command = clap.mode.RedCommand()
        command.addLocalOption(clap.option.Option(short='s', long='spam', implies=['--eggs']))
        command.addLocalOption(clap.option.Option(short='n', long='no-spam'))
        command.addLocalOption(clap.option.Option(short='e', long='eggs', conflicts=['--no-spam'], arguments=['int', 'int'], defaults=['42', '24']))
        self.assertRaises(clap.errors.ConflictingOptionsError, clap.parser.Parser(command).feed(args).parse)

    def testOptionImplyingOptionWhichIsConflictedWithAlreadyProvidedOptionRaisesAnExceptionDuringParsing(self):
        args = ['--spam', '--no-spam']
        command = clap.mode.RedCommand()
        command.addLocalOption(clap.option.Option(short='s', long='spam', implies=['--eggs']))
        command.addLocalOption(clap.option.Option(short='n', long='no-spam', conflicts=['--eggs']))
        command.addLocalOption(clap.option.Option(short='e', long='eggs', arguments=['int', 'int'], defaults=['42', '24']))
        self.assertRaises(clap.errors.ConflictingOptionsError, clap.parser.Parser(command).feed(args).parse)

    def testOptionImpliedByAnotherIsAddedToTheListDuringParsing(self):
        args = ['--spam']
        command = clap.mode.RedCommand()
        command.addLocalOption(clap.option.Option(short='s', long='spam', implies=['--eggs']))
        command.addLocalOption(clap.option.Option(short='e', long='eggs', arguments=['int', 'int'], defaults=['42', '24']))
        parser = clap.parser.Parser(command).feed(args).parse()
        state, ui = parser.state(), parser.ui()
        self.assertTrue('--spam' in state['options'])
        self.assertTrue('--eggs' in state['options'])
        self.assertTrue('--spam' in ui)
        self.assertTrue('--eggs' in ui)


class ParserNestedCommandsTests(unittest.TestCase):
    def testSimpleChildCommand(self):
        command = clap.mode.RedCommand()
        command.addLocalOption(clap.option.Option(short='b', long='breakfast', arguments=['str']))
        command.addLocalOption(clap.option.Option(short='w', long='what'))
        command.setOperandsRange(no=[2, 2])
        command.addCommand(name='child', command=clap.mode.RedCommand().setOperandsRange(no=[2, 2]))
        argv = ['--breakfast', 'yes', '--what', 'spam', 'ham', 'child', 'foo', 'bar']
        operands = ['spam', 'ham']
        nested = ['child', 'foo', 'bar']
        parser = clap.parser.Parser(command).feed(argv)
        got_operands, got_nested = parser._getheuroperands()
        self.assertEqual(operands, got_operands)
        self.assertEqual(nested, got_nested)

    def testGettingOperandsAndNestedCommandItems(self):
        command = getTestCommand().setOperandsRange(no=[2, 2])
        child = clap.mode.RedCommand().addLocalOption(clap.option.Option(short='a', long='answer', arguments=['int']))
        command.addCommand(name='child', command=child)
        argv = ['--foo', '-b', '-B', 'spam', 'ham', 'child', '--answer', '42']
        parser = clap.parser.Parser(command).feed(argv)
        self.assertEqual(['spam', 'ham'], parser._getheuroperands()[0])
        self.assertEqual(['child', '--answer', '42'], parser._getheuroperands()[1])

    def testNestedCommandsOptionsNotPropragatedToHigherLevelCommands(self):
        command = clap.mode.RedCommand()
        command.addLocalOption(clap.option.Option(short='a', long='answer', arguments=['int']))
        child = clap.mode.RedCommand().addLocalOption(clap.option.Option(short='a', long='answer', arguments=['int']))
        command.addCommand(name='child', command=child)
        argv = ['child', '--answer', '42']
        parser = clap.parser.Parser(command).feed(argv)
        self.assertEqual(['child', '--answer', '42'], parser._getheuroperands()[1])
        ui = parser.parse().ui()
        self.assertEqual('', str(ui))
        self.assertFalse('--answer' in ui)
        ui = ui.down()
        self.assertEqual('child', str(ui))
        self.assertTrue('--answer' in ui)

    def testPropagatingGlobalOptionsWithoutArgumentsToNestedCommands(self):
        command = clap.mode.RedCommand().setOperandsRange(no=[0, 0])
        command.addLocalOption(clap.option.Option(short='l', long='local'))
        command.addGlobalOption(clap.option.Option(short='g', long='global'))
        child = clap.mode.RedCommand()
        command.addCommand(name='child', command=child)
        command.propagate()
        argv = ['--local', '--global', 'child']
        ui = clap.parser.Parser(command).feed(argv).parse().ui().finalise()
        self.assertEqual('', str(ui))
        self.assertIn('-l', ui)
        self.assertIn('--local', ui)
        self.assertIn('-g', ui)
        self.assertIn('--global', ui)
        ui = ui.down()
        self.assertEqual('child', str(ui))
        self.assertNotIn('-l', ui)
        self.assertNotIn('--local', ui)
        self.assertIn('-g', ui)
        self.assertIn('--global', ui)

    def testPropagatingGlobalOptionsWithArgumentsToNestedCommands(self):
        command = clap.mode.RedCommand().setOperandsRange(no=[0, 0])
        command.addLocalOption(clap.option.Option(short='l', long='local'))
        command.addGlobalOption(clap.option.Option(short='g', long='global', arguments=['int']))
        child = clap.mode.RedCommand()
        command.addCommand(name='child', command=child)
        command.propagate()
        argv = ['--local', '--global', '42', 'child']
        ui = clap.parser.Parser(command).feed(argv).parse().ui().finalise()
        self.assertEqual('', str(ui))
        self.assertIn('-l', ui)
        self.assertIn('--local', ui)
        self.assertIn('-g', ui)
        self.assertIn('--global', ui)
        self.assertEqual(42, ui.get('-g'))
        self.assertEqual(42, ui.get('--global'))
        ui = ui.down()
        self.assertEqual('child', str(ui))
        self.assertNotIn('-l', ui)
        self.assertNotIn('--local', ui)
        self.assertIn('-g', ui)
        self.assertIn('--global', ui)
        self.assertEqual(42, ui.get('-g'))
        self.assertEqual(42, ui.get('--global'))

    def testPropagatingGlobalOptionsWithArgumentsToNestedCommandsDoesNotOverwriteArgumentsPassedInNestedCommand(self):
        command = clap.mode.RedCommand().setOperandsRange(no=[0, 0])
        command.addLocalOption(clap.option.Option(short='l', long='local'))
        command.addGlobalOption(clap.option.Option(short='g', long='global', arguments=['int']))
        child = clap.mode.RedCommand()
        command.addCommand(name='child', command=child)
        command.propagate()
        argv = ['--local', '--global', '42', 'child', '-g', '69']
        ui = clap.parser.Parser(command).feed(argv).parse().ui().finalise()
        self.assertEqual('', str(ui))
        self.assertIn('-l', ui)
        self.assertIn('--local', ui)
        self.assertIn('-g', ui)
        self.assertIn('--global', ui)
        self.assertEqual(42, ui.get('-g'))
        self.assertEqual(42, ui.get('--global'))
        ui = ui.down()
        self.assertEqual('child', str(ui))
        self.assertNotIn('-l', ui)
        self.assertNotIn('--local', ui)
        self.assertIn('-g', ui)
        self.assertIn('--global', ui)
        self.assertEqual(69, ui.get('-g'))
        self.assertEqual(69, ui.get('--global'))

    def testPropagatingGlobalPluralOptionsWithoutArguments(self):
        command = clap.mode.RedCommand().setOperandsRange(no=[0, 0])
        command.addLocalOption(clap.option.Option(short='l', long='local'))
        command.addGlobalOption(clap.option.Option(short='g', long='global', plural=True))
        child = clap.mode.RedCommand()
        command.addCommand(name='child', command=child)
        command.propagate()
        argv = ['--local', '--global', 'child']
        ui = clap.parser.Parser(command).feed(argv).parse().ui().finalise()
        self.assertEqual('', str(ui))
        self.assertIn('-l', ui)
        self.assertIn('--local', ui)
        self.assertIn('-g', ui)
        self.assertIn('--global', ui)
        self.assertEqual(1, ui.get('-g'))
        self.assertEqual(1, ui.get('--global'))
        ui = ui.down()
        self.assertEqual('child', str(ui))
        self.assertNotIn('-l', ui)
        self.assertNotIn('--local', ui)
        self.assertIn('-g', ui)
        self.assertIn('--global', ui)
        self.assertEqual(1, ui.get('-g'))
        self.assertEqual(1, ui.get('--global'))

    def testPropagatingGlobalPluralOptionsWithoutArgumentsIncreasesCountIfOptionIsFoundInNestedCommand(self):
        command = clap.mode.RedCommand().setOperandsRange(no=[0, 0])
        command.addLocalOption(clap.option.Option(short='l', long='local'))
        command.addGlobalOption(clap.option.Option(short='g', long='global', plural=True))
        child = clap.mode.RedCommand().addCommand(name='second', command=clap.mode.RedCommand())
        command.addCommand(name='child', command=child)
        command.propagate()
        argv = ['--local', '--global', 'child', '-g', '--global', 'second', '--global']
        ui = clap.parser.Parser(command).feed(argv).parse().ui().finalise()
        self.assertEqual('', str(ui))
        self.assertIn('-l', ui)
        self.assertIn('--local', ui)
        self.assertIn('-g', ui)
        self.assertIn('--global', ui)
        self.assertEqual(1, ui.get('-g'))
        self.assertEqual(1, ui.get('--global'))
        ui = ui.down()
        self.assertEqual('child', str(ui))
        self.assertNotIn('-l', ui)
        self.assertNotIn('--local', ui)
        self.assertIn('-g', ui)
        self.assertIn('--global', ui)
        self.assertEqual(3, ui.get('-g'))
        self.assertEqual(3, ui.get('--global'))
        ui = ui.down()
        self.assertEqual('second', str(ui))
        self.assertNotIn('-l', ui)
        self.assertNotIn('--local', ui)
        self.assertIn('-g', ui)
        self.assertIn('--global', ui)
        self.assertEqual(4, ui.get('-g'))
        self.assertEqual(4, ui.get('--global'))

    def testPropagatingGlobalOptionsThatStartAppearingInNonfirstCommand(self):
        command = clap.mode.RedCommand().setOperandsRange(no=[0, 0])
        command.addLocalOption(clap.option.Option(short='l', long='local'))
        child = clap.mode.RedCommand().setOperandsRange(no=[0, 0])
        child.addGlobalOption(clap.option.Option(short='g', long='global', plural=True))
        child.addCommand(name='second', command=clap.mode.RedCommand())
        command.addCommand(name='child', command=child)
        command.propagate()
        argv = ['--local', 'child', '-g', '--global', 'second', '--global']
        ui = clap.parser.Parser(command).feed(argv).parse().ui().finalise()
        self.assertEqual('', str(ui))
        self.assertIn('-l', ui)
        self.assertIn('--local', ui)
        self.assertNotIn('-g', ui)
        self.assertNotIn('--global', ui)
        ui = ui.down()
        self.assertEqual('child', str(ui))
        self.assertNotIn('-l', ui)
        self.assertNotIn('--local', ui)
        self.assertIn('-g', ui)
        self.assertIn('--global', ui)
        self.assertEqual(2, ui.get('-g'))
        self.assertEqual(2, ui.get('--global'))
        ui = ui.down()
        self.assertEqual('second', str(ui))
        self.assertNotIn('-l', ui)
        self.assertNotIn('--local', ui)
        self.assertIn('-g', ui)
        self.assertIn('--global', ui)
        self.assertEqual(3, ui.get('-g'))
        self.assertEqual(3, ui.get('--global'))

    def testFixedRangeOperandsNotNeededWhenCommandImmediatelyFollowedByNestedCommand(self):
        command = getTestCommand().setOperandsRange(no=[2, 2])
        child = clap.mode.RedCommand().addLocalOption(clap.option.Option(short='a', long='answer', arguments=['int']))
        command.addCommand(name='child', command=child)
        argv = ['--foo', '-b', '-B', 'child', '--answer', '42']
        parser = clap.parser.Parser(command).feed(argv)
        checker = clap.checker.RedChecker(parser)
        checker.check()
        parser.parse()
        ui = parser.ui()
        self.assertEqual('', str(ui))
        ui = ui.down()
        self.assertEqual('child', str(ui))


class ParserShortenedCommandNamesTests(unittest.TestCase):
    def testSimpleCommandNameExpansion(self):
        command = clap.mode.RedCommand()
        command.setOperandsRange(no=[2, 2])
        command.addCommand(name='foo', command=clap.mode.RedCommand())
        command.addCommand(name='bar', command=clap.mode.RedCommand())
        command.addCommand(name='far', command=clap.mode.RedCommand())
        argv = ['b']
        parser = clap.parser.Parser(command).feed(argv)
        checker = clap.checker.RedChecker(parser)
        self.assertIsNone(checker.check())
        ui = parser.parse().ui().down()
        self.assertEqual('bar', str(ui))
        self.assertEqual([], ui.operands())

    def testFalsePositivesSuppression(self):
        command = clap.mode.RedCommand()
        command.setOperandsRange(no=[2, 2])
        command.addCommand(name='foo', command=clap.mode.RedCommand())
        command.addCommand(name='bar', command=clap.mode.RedCommand())
        command.addCommand(name='far', command=clap.mode.RedCommand())
        argv = ['--', 'fa']
        parser = clap.parser.Parser(command).feed(argv)
        ui = parser.parse().ui().down()
        self.assertEqual('', str(ui))
        self.assertEqual(['fa'], ui.operands())

    def testNestedCommandNameExpansion(self):
        command = clap.mode.RedCommand()
        command.setOperandsRange(no=[2, 2])
        command.addCommand(name='foo', command=clap.mode.RedCommand().addCommand(name='bar', command=clap.mode.RedCommand().addCommand(name='baz', command=clap.mode.RedCommand())))
        argv = ['f', 'b', 'b']
        parser = clap.parser.Parser(command).feed(argv)
        checker = clap.checker.RedChecker(parser)
        self.assertIsNone(checker.check())
        ui = parser.parse().ui()
        ui = ui.down()
        self.assertEqual('foo', str(ui))
        self.assertEqual([], ui.operands())
        ui = ui.down()
        self.assertEqual('bar', str(ui))
        self.assertEqual([], ui.operands())
        ui = ui.down()
        self.assertEqual('baz', str(ui))
        self.assertEqual([], ui.operands())


class ParserOperandsTests(unittest.TestCase):
    def testSettingRangeAny(self):
        command = clap.mode.RedCommand()
        command.setOperandsRange(no=[])
        self.assertEqual((None, None), command.getOperandsRange())
        command.setOperandsRange()
        self.assertEqual((None, None), command.getOperandsRange())

    def testSettingRangeBetween(self):
        command = clap.mode.RedCommand()
        command.setOperandsRange(no=[1, 2])
        self.assertEqual((1, 2), command.getOperandsRange())

    def testSettingRangeAtLeast(self):
        command = clap.mode.RedCommand()
        command.setOperandsRange(no=[2])
        self.assertEqual((2, None), command.getOperandsRange())

    def testSettingRangeAtMost(self):
        command = clap.mode.RedCommand()
        command.setOperandsRange(no=[-2])
        self.assertEqual((0, 2), command.getOperandsRange())

    def testSettingAlternativeRange(self):
        command = clap.mode.RedCommand()
        command.setOperandsRange(no=[-2])
        command.setAlternativeOperandsRange(no={
            '--foo': [0, 0]
        })
        self.assertEqual((0, 2), command.getOperandsRange())
        self.assertEqual((0, 0), command.getAlternativeOperandsRange('--foo'))

    def testSettingRangeInvalid(self):
        command = clap.mode.RedCommand()
        ranges = [
                [-1, -1],
                [1, 2, 3],
                [4, 2],
                ]
        for i in ranges:
            self.assertRaises(clap.errors.InvalidOperandRangeError, command.setOperandsRange, i)

    def testSettingTypesForOperands(self):
        types = ['str', 'int', 'int', 'int']
        command = clap.mode.RedCommand()
        command.setOperandsTypes(types)
        self.assertEqual(types, command.getOperandsTypes())

    def testGettingOperandsEnclosed(self):
        argv = ['--foo', '--', '--bar', 'baz', '---', '--baz', 'this', 'is', 'discarded']
        command = clap.mode.RedCommand()
        command.addLocalOption(clap.option.Option(short='f', long='foo'))
        command.addLocalOption(clap.option.Option(short='b', long='bar'))
        command.addLocalOption(clap.option.Option(short='B', long='baz'))
        parser = clap.parser.Parser(command).feed(argv)
        self.assertEqual(['--bar', 'baz'], parser._getoperands())

    def testGettingOperandsEnclosingNotWorkingWhenThereIsNoTerminator(self):
        argv = ['--foo', '--bar', 'baz', '---', '--baz', 'this', 'is', 'not', 'discarded']
        command = clap.mode.RedCommand()
        command.addLocalOption(clap.option.Option(short='f', long='foo'))
        command.addLocalOption(clap.option.Option(short='b', long='bar'))
        command.addLocalOption(clap.option.Option(short='B', long='baz'))
        parser = clap.parser.Parser(command).feed(argv)
        self.assertEqual(['baz', '---', '--baz', 'this', 'is', 'not', 'discarded'], parser._getoperands())


class CheckerOptionCheckingTests(unittest.TestCase):
    def testUnrecognizedOptions(self):
        argv = ['--foo', '--bar', '--baz']
        command = clap.mode.RedCommand()
        command.addLocalOption(clap.option.Option(long='foo'))
        command.addLocalOption(clap.option.Option(long='bar'))
        parser = clap.parser.Parser(command).feed(argv)
        checker = clap.checker.RedChecker(parser)
        self.assertRaises(clap.errors.UnrecognizedOptionError, checker._checkunrecognized)
        self.assertRaises(clap.errors.UnrecognizedOptionError, checker.check)

    def testUnrecognizedOptions(self):
        argv = ['--hello', 'world']
        command = clap.mode.RedCommand()
        parser = clap.parser.Parser(command).feed(argv)
        checker = clap.checker.RedChecker(parser)
        self.assertRaises(clap.errors.UnrecognizedOptionError, checker._checkunrecognized)
        self.assertRaises(clap.errors.UnrecognizedOptionError, checker.check)

    def testArgumentNotGivenAtTheEnd(self):
        argv = ['--bar', '--foo']
        command = clap.mode.RedCommand()
        command.addLocalOption(clap.option.Option(long='foo', arguments=['str']))
        command.addLocalOption(clap.option.Option(long='bar'))
        parser = clap.parser.Parser(command).feed(argv)
        checker = clap.checker.RedChecker(parser)
        self.assertRaises(clap.errors.MissingArgumentError, checker._checkarguments)
        self.assertRaises(clap.errors.MissingArgumentError, checker.check)

    def testArgumentNotGivenAtTheEndBecauseOfBreaker(self):
        argv = ['--bar', '--foo', '--', 'baz']
        command = clap.mode.RedCommand()
        command.addLocalOption(clap.option.Option(long='foo', arguments=['str']))
        command.addLocalOption(clap.option.Option(long='bar'))
        parser = clap.parser.Parser(command).feed(argv)
        checker = clap.checker.RedChecker(parser)
        self.assertRaises(clap.errors.MissingArgumentError, checker._checkarguments)
        self.assertRaises(clap.errors.MissingArgumentError, checker.check)

    def testInvalidArgumentType(self):
        argv = ['--bar', '--foo', 'baz']
        command = clap.mode.RedCommand()
        command.addLocalOption(clap.option.Option(long='foo', arguments=['int']))
        command.addLocalOption(clap.option.Option(long='bar'))
        parser = clap.parser.Parser(command).feed(argv)
        checker = clap.checker.RedChecker(parser)
        self.assertRaises(clap.errors.InvalidArgumentTypeError, checker._checkarguments)
        self.assertRaises(clap.errors.InvalidArgumentTypeError, checker.check)

    def testInvalidArgumentTypeWhenMultipleArgumentsAreRequested(self):
        argv = ['--point', '0', 'y']
        command = clap.mode.RedCommand()
        command.addLocalOption(clap.option.Option(long='point', arguments=['int', 'int']))
        parser = clap.parser.Parser(command).feed(argv)
        checker = clap.checker.RedChecker(parser)
        self.assertRaises(clap.errors.InvalidArgumentTypeError, checker._checkarguments)
        self.assertRaises(clap.errors.InvalidArgumentTypeError, checker.check)

    def testAnotherOptionGivenAsArgument(self):
        argv = ['--foo', '--bar']
        command = clap.mode.RedCommand()
        command.addLocalOption(clap.option.Option(long='foo', arguments=['int']))
        command.addLocalOption(clap.option.Option(long='bar'))
        parser = clap.parser.Parser(command).feed(argv)
        checker = clap.checker.RedChecker(parser)
        self.assertRaises(clap.errors.MissingArgumentError, checker._checkarguments)
        self.assertRaises(clap.errors.MissingArgumentError, checker.check)

    def testAnotherOptionGivenAsArgumentWhenMultipleArgumentsAreRequested(self):
        argv = ['--foo', '42', '--bar']
        command = clap.mode.RedCommand()
        command.addLocalOption(clap.option.Option(long='foo', arguments=['int', 'int']))
        command.addLocalOption(clap.option.Option(long='bar'))
        parser = clap.parser.Parser(command).feed(argv)
        checker = clap.checker.RedChecker(parser)
        self.assertRaises(clap.errors.MissingArgumentError, checker._checkarguments)
        self.assertRaises(clap.errors.MissingArgumentError, checker.check)

    def testRequiredOptionNotFound(self):
        argv = ['--bar']
        command = clap.mode.RedCommand()
        command.addLocalOption(clap.option.Option(long='foo', required=True))
        command.addLocalOption(clap.option.Option(long='bar'))
        parser = clap.parser.Parser(command).feed(argv)
        checker = clap.checker.RedChecker(parser)
        self.assertRaises(clap.errors.RequiredOptionNotFoundError, checker._checkrequired)
        self.assertRaises(clap.errors.RequiredOptionNotFoundError, checker.check)

    def testRequiredOptionNotFoundBecauseOfBreaker(self):
        argv = ['--bar', '--', '--foo']
        command = clap.mode.RedCommand()
        command.addLocalOption(clap.option.Option(long='foo', required=True))
        command.addLocalOption(clap.option.Option(long='bar'))
        parser = clap.parser.Parser(command).feed(argv)
        checker = clap.checker.RedChecker(parser)
        self.assertRaises(clap.errors.RequiredOptionNotFoundError, checker._checkrequired)
        self.assertRaises(clap.errors.RequiredOptionNotFoundError, checker.check)

    def testRequiredOptionNotFoundBecauseMisusedAsAnArgumentToAnotherOption(self):
        argv = ['--bar', '--foo']
        command = clap.mode.RedCommand()
        command.addLocalOption(clap.option.Option(long='foo', required=True))
        command.addLocalOption(clap.option.Option(long='bar', arguments=['str']))
        parser = clap.parser.Parser(command).feed(argv)
        checker = clap.checker.RedChecker(parser)
        self.assertRaises(clap.errors.RequiredOptionNotFoundError, checker._checkrequired)
        self.assertRaises(clap.errors.MissingArgumentError, checker.check)

    def testRequiredNotWithAnotherOption(self):
        argvariants = [
                ['--bar'],
                ['-b'],
                ]
        command = clap.mode.RedCommand()
        command.addLocalOption(clap.option.Option(long='foo', required=True, not_with=['--bar', '--fail']))
        command.addLocalOption(clap.option.Option(short='b', long='bar'))
        for argv in argvariants:
            parser = clap.parser.Parser(command).feed(argv)
            checker = clap.checker.RedChecker(parser)
            checker._checkrequired()
            checker.check()

    def testRequiredNotWithAnotherOptionNotFoundBecauseOfBreaker(self):
        argv = ['--baz', '--', '-b']
        command = clap.mode.RedCommand()
        command.addLocalOption(clap.option.Option(long='foo', required=True, not_with=['--bar']))
        command.addLocalOption(clap.option.Option(short='b', long='bar'))
        command.addLocalOption(clap.option.Option(short='B', long='baz'))
        parser = clap.parser.Parser(command).feed(argv)
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
        command = clap.mode.RedCommand()
        command.addLocalOption(clap.option.Option(short='f', long='foo', requires=['--bar', '--baz']))
        command.addLocalOption(clap.option.Option(short='b', long='bar'))
        command.addLocalOption(clap.option.Option(short='B', long='baz'))
        for argv in argvariants:
            parser = clap.parser.Parser(command).feed(argv)
            checker = clap.checker.RedChecker(parser)
            if DEBUG: print('checking:', ' '.join(argv))
            checker._checkrequires()
            checker.check()

    def testOptionRequiredByAnotherOptionNotFound(self):
        argv = ['--foo', '--bar']
        command = clap.mode.RedCommand()
        command.addLocalOption(clap.option.Option(short='f', long='foo', requires=['--bar', '--baz']))
        command.addLocalOption(clap.option.Option(short='b', long='bar'))
        command.addLocalOption(clap.option.Option(short='B', long='baz'))
        parser = clap.parser.Parser(command).feed(argv)
        checker = clap.checker.RedChecker(parser)
        self.assertRaises(clap.errors.RequiredOptionNotFoundError, checker._checkrequires)
        self.assertRaises(clap.errors.RequiredOptionNotFoundError, checker.check)

    def testOptionRequiredByAnotherOptionNotFoundBecauseOfBreaker(self):
        argv = ['--foo', '--bar', '--', '--baz']
        command = clap.mode.RedCommand()
        command.addLocalOption(clap.option.Option(short='f', long='foo', requires=['--bar', '--baz']))
        command.addLocalOption(clap.option.Option(short='b', long='bar'))
        command.addLocalOption(clap.option.Option(short='B', long='baz'))
        parser = clap.parser.Parser(command).feed(argv)
        checker = clap.checker.RedChecker(parser)
        self.assertRaises(clap.errors.RequiredOptionNotFoundError, checker._checkrequires)
        self.assertRaises(clap.errors.RequiredOptionNotFoundError, checker.check)

    def testOptionWantedByAnotherOption(self):
        argvariants = [
                ['--foo', '--bar', '42', '--baz'],  # both wanted present:: --bar and --baz
                ['--foo', '-b', '42', '--baz'],     # both wanted present:: --bar and --baz
                ['--foo', '--bar', '42', '-B'],     # both wanted present:: --bar and --baz
                ['--foo', '-b', '42', '-B'],     # both wanted present:: --bar and --baz
                ['--foo', '--bar', '42'],           # one wanted present: --bar
                ['--foo', '-b', '42'],              # one wanted present: --bar
                ['--foo', '--baz'],                 # one wanted present: --baz
                ['--foo', '-B'],                    # one wanted present: --baz
                ]
        command = clap.mode.RedCommand()
        command.addLocalOption(clap.option.Option(short='f', long='foo', wants=['--bar', '--baz']))
        command.addLocalOption(clap.option.Option(short='b', long='bar', arguments=['int']))
        command.addLocalOption(clap.option.Option(short='B', long='baz'))
        for argv in argvariants:
            parser = clap.parser.Parser(command).feed(argv)
            checker = clap.checker.RedChecker(parser)
            if DEBUG: print('checking:', ' '.join(argv))
            checker._checkwants()
            checker.check()

    def testOptionWantedByAnotherOptionNotFound(self):
        argv = ['--foo']
        command = clap.mode.RedCommand()
        command.addLocalOption(clap.option.Option(short='f', long='foo', wants=['--bar', '--baz']))
        command.addLocalOption(clap.option.Option(short='b', long='bar', arguments=['int']))
        command.addLocalOption(clap.option.Option(short='B', long='baz'))
        parser = clap.parser.Parser(command).feed(argv)
        checker = clap.checker.RedChecker(parser)
        self.assertRaises(clap.errors.WantedOptionNotFoundError, checker._checkwants)
        self.assertRaises(clap.errors.WantedOptionNotFoundError, checker.check)

    def testOptionWantedByAnotherOptionNotFoundBecauseOfBreaker(self):
        argv = ['--foo', '--', '--bar']
        command = clap.mode.RedCommand()
        command.addLocalOption(clap.option.Option(short='f', long='foo', wants=['--bar', '--baz']))
        command.addLocalOption(clap.option.Option(short='b', long='bar', arguments=['int']))
        command.addLocalOption(clap.option.Option(short='B', long='baz'))
        parser = clap.parser.Parser(command).feed(argv)
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
        command = clap.mode.RedCommand()
        command.addLocalOption(clap.option.Option(short='f', long='foo', conflicts=['--bar']))
        command.addLocalOption(clap.option.Option(short='b', long='bar'))
        for argv in argvariants:
            parser = clap.parser.Parser(command).feed(argv)
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
        command = clap.mode.RedCommand()
        command.addLocalOption(clap.option.Option(short='f', long='foo', conflicts=['--bar']))
        command.addLocalOption(clap.option.Option(short='b', long='bar'))
        for argv in argvariants:
            parser = clap.parser.Parser(command).feed(argv)
            checker = clap.checker.RedChecker(parser)
            if DEBUG: print('checking:', ' '.join(argv))
            checker._checkconflicts()
            checker.check()


class CheckerOperandCheckingTests(unittest.TestCase):
    def testOperandRangeAny(self):
        argvariants = [
                ['--foo', '-b'],                    # no operands
                ['--foo', '-b', '0'],               # one operand
                ['--foo', '-b', '0', '1'],          # two operands
                ['--foo', '-b', '0', '1', '2'],     # more than two operands
                ]
        command = clap.mode.RedCommand()
        command.addLocalOption(clap.option.Option(short='f', long='foo'))
        command.addLocalOption(clap.option.Option(short='b', long='bar'))
        command.setOperandsRange(no=[])
        parser = clap.parser.Parser(command)
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
        command = clap.mode.RedCommand()
        command.addLocalOption(clap.option.Option(short='f', long='foo'))
        command.addLocalOption(clap.option.Option(short='b', long='bar'))
        ranges = [
                (2,),
                (2, None),
                ]
        for r in ranges:
            command.setOperandsRange(no=r)
            parser = clap.parser.Parser(command)
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
        command = clap.mode.RedCommand()
        command.addLocalOption(clap.option.Option(short='f', long='foo'))
        command.addLocalOption(clap.option.Option(short='b', long='bar'))
        ranges = [(-2,), (0, 2), (None, 2)]
        for r in ranges:
            command.setOperandsRange(no=r)
            parser = clap.parser.Parser(command)
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
        command = clap.mode.RedCommand()
        command.addLocalOption(clap.option.Option(short='f', long='foo'))
        command.addLocalOption(clap.option.Option(short='b', long='bar'))
        ranges = [(2, 4)]
        for r in ranges:
            command.setOperandsRange(no=r)
            parser = clap.parser.Parser(command)
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
        command = clap.mode.RedCommand()
        command.addLocalOption(clap.option.Option(short='f', long='foo'))
        command.addLocalOption(clap.option.Option(short='b', long='bar'))
        ranges = [
                (0, 0)
                ]
        for r in ranges:
            command.setOperandsRange(no=r)
            parser = clap.parser.Parser(command)
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

    def testOperandRangeAlternative(self):
        argvariants = [
                ['--foo'],
                ['a', 'b'],
                ['--foo', '--'],
                ['--', 'a', 'b'],
        ]
        failvariants = [
                ['--foo', 'a'],
                [],
                ['--foo', '--', 'a', 'b'],
                ['--',],
        ]
        command = clap.mode.RedCommand()
        command.addLocalOption(clap.option.Option(short='f', long='foo'))
        command.addLocalOption(clap.option.Option(short='b', long='bar'))
        command.setAlternativeOperandsRange(no={
            '--foo': [0, 0]
        })
        command.setOperandsRange(no=(1, 2))
        parser = clap.parser.Parser(command)
        for argv in argvariants:
            parser.feed(argv)
            checker = clap.checker.RedChecker(parser)
            checker._checkoperandsrange()
        for argv in failvariants:
            parser.feed(argv)
            checker = clap.checker.RedChecker(parser)
            self.assertRaises(clap.errors.InvalidOperandRangeError, checker._checkoperandsrange)

    def testOperandsRangeNotCompatibleWithListOfTypesInvalidLeast(self):
        command = clap.mode.RedCommand()
        ranges = [
                (3, 4),
                (-3,),
                (3,),
                ]
        for r in ranges:
            command.setOperandsRange(no=r)
            command.setOperandsTypes(types=['int', 'int'])
            parser = clap.parser.Parser(command).feed([])
            checker = clap.checker.RedChecker(parser)
            self.assertRaises(clap.errors.UIDesignError, checker._checkoperandscompat)

    def testOperandsRangeNotCompatibleWithListOfTypesInvalidMost(self):
        command = clap.mode.RedCommand()
        ranges = [
                (2, 5),
                (5,),
                (-5,),
                ]
        for r in ranges:
            command.setOperandsRange(no=r)
            command.setOperandsTypes(types=['int', 'int'])
            parser = clap.parser.Parser(command).feed([])
            checker = clap.checker.RedChecker(parser)
            self.assertRaises(clap.errors.UIDesignError, checker._checkoperandscompat)

    def testOperandsRangeNotCompatibleWithListOfTypesInvalidMostListOfTypesTooLong(self):
        command = clap.mode.RedCommand()
        command.setOperandsRange(no=[2, 3])
        command.setOperandsTypes(types=['int', 'int', 'int', 'int'])
        parser = clap.parser.Parser(command).feed([])
        checker = clap.checker.RedChecker(parser)
        self.assertRaises(clap.errors.UIDesignError, checker._checkoperandscompat)

    def testOperandsRangeNotCompatibleWithListOfTypesInvalidExact(self):
        command = clap.mode.RedCommand()
        ranges = [
                (0, 0),
                (5, 5),
                ]
        for r in ranges:
            command.setOperandsRange(no=r)
            command.setOperandsTypes(types=['int', 'int', 'int', 'int'])
            parser = clap.parser.Parser(command).feed([])
            checker = clap.checker.RedChecker(parser)
            self.assertRaises(clap.errors.UIDesignError, checker._checkoperandscompat)

    def testOperandsRangeCompatibleWithListOfTypes(self):
        command = clap.mode.RedCommand()
        command.setOperandsRange(no=[2, 4])
        command.setOperandsTypes(types=['int', 'int'])
        parser = clap.parser.Parser(command).feed([])
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
        command = clap.mode.RedCommand()
        command.addLocalOption(clap.option.Option(short='f', long='foo'))
        command.addLocalOption(clap.option.Option(short='b', long='bar'))
        command.setOperandsTypes(types=['int', 'int'])
        parser = clap.parser.Parser(command)
        for argv in argvariants:
            parser.feed(argv)
            if DEBUG: print('checking range based only on list of types ({0}) with input: {1}'.format(len(command.getOperandsTypes()), parser._getoperands()))
            checker = clap.checker.RedChecker(parser)
            checker._checkoperandsrange()
        for argv in failvariants:
            parser.feed(argv)
            if DEBUG: print('fail checking range based only on list of types ({0}) with input: {1}'.format(len(command.getOperandsTypes()), parser._getoperands()))
            checker = clap.checker.RedChecker(parser)
            self.assertRaises(clap.errors.InvalidOperandRangeError, checker._checkoperandsrange)


class CheckerNestedCommandsCheckingTests(unittest.TestCase):
    def testFixedRangeItemTreatedAsCommandBecauseFollowedByOptionAcceptedByOneOfValidChildCommands(self):
        command = getTestCommand().setOperandsRange(no=[2, 2])
        child = clap.mode.RedCommand().addLocalOption(clap.option.Option(short='a', long='answer', arguments=['int']))
        command.addCommand(name='child', command=child)
        argv = ['--foo', '-b', '-B', 'spam', 'ham', 'fake', '--answer', '42']
        parser = clap.parser.Parser(command).feed(argv)
        checker = clap.checker.RedChecker(parser)
        self.assertRaises(clap.errors.UnrecognizedCommandError, checker._checksubcommand)
        self.assertRaises(clap.errors.UnrecognizedCommandError, checker.check)

    def testFixedRangeUnrecognizedOptionInNestedCommand(self):
        command = getTestCommand().setOperandsRange(no=[2, 2])
        child = clap.mode.RedCommand().addLocalOption(clap.option.Option(short='a', long='answer', arguments=['int']))
        command.addCommand(name='child', command=child)
        argv = ['--foo', '-b', '-B', 'spam', 'ham', 'child', '--answer', '42', '--fake']
        parser = clap.parser.Parser(command).feed(argv)
        checker = clap.checker.RedChecker(parser)
        self.assertRaises(clap.errors.UnrecognizedOptionError, checker._checksubcommand)
        self.assertRaises(clap.errors.UnrecognizedOptionError, checker.check)

    def testFixedRangeInvalidNumberOfOperandsBecauseCommandIsGivenTooFast(self):
        command = getTestCommand().setOperandsRange(no=[2, 2])
        child = clap.mode.RedCommand().addLocalOption(clap.option.Option(short='a', long='answer', arguments=['int']))
        command.addCommand(name='child', command=child)
        argv = ['--foo', '-b', '-B', 'spam', 'child', '--answer', '42']
        parser = clap.parser.Parser(command).feed(argv)
        checker = clap.checker.RedChecker(parser)
        checker._checksubcommand()
        self.assertRaises(clap.errors.InvalidOperandRangeError, checker._checkoperandsrange)
        self.assertRaises(clap.errors.InvalidOperandRangeError, checker.check)

    def testFixedRangeInvalidNumberOfOperandsRaisedBeforeInvalidCommand(self):
        command = getTestCommand().setOperandsRange(no=[2, 2])
        child = clap.mode.RedCommand().addLocalOption(clap.option.Option(short='a', long='answer', arguments=['int']))
        command.addCommand(name='child', command=child)
        argv = ['--foo', '-b', '-B', 'spam', 'fake', '--answer', '42']
        parser = clap.parser.Parser(command).feed(argv)
        checker = clap.checker.RedChecker(parser)
        self.assertRaises(clap.errors.UnrecognizedCommandError, checker._checksubcommand)
        self.assertRaises(clap.errors.InvalidOperandRangeError, checker.check)

    def testFluidRangeItemTreatedAsCommandBecauseFollowedByOptionAcceptedByOneOfValidChildCommands(self):
        command = getTestCommand().setOperandsRange(no=[1, 4])
        child = clap.mode.RedCommand().addLocalOption(clap.option.Option(short='a', long='answer', arguments=['int']))
        command.addCommand(name='child', command=child)
        parser = clap.parser.Parser(command)
        argvariants = [
                ['--foo', '-b', '-B', 'alpha', 'fake', '--answer', '42'],
                ['--foo', '-b', '-B', 'alpha', 'beta', 'fake', '--answer', '42'],
                ['--foo', '-b', '-B', 'alpha', 'beta', 'gamma', 'fake', '--answer', '42'],
                ['--foo', '-b', '-B', 'alpha', 'beta', 'gamma', 'delta', 'fake', '--answer', '42'],
                ]
        for argv in argvariants:
            parser.feed(argv)
            checker = clap.checker.RedChecker(parser)
            self.assertRaises(clap.errors.UnrecognizedCommandError, checker._checksubcommand)
            self.assertRaises(clap.errors.UnrecognizedCommandError, checker.check)

    def testFluidRangeUnrecognizedOptionInNestedCommand(self):
        command = getTestCommand().setOperandsRange(no=[1, 4])
        child = clap.mode.RedCommand().addLocalOption(clap.option.Option(short='a', long='answer', arguments=['int']))
        command.addCommand(name='child', command=child)
        parser = clap.parser.Parser(command)
        argvariants = [
                ['--foo', '-b', '-B', 'alpha', 'child', '--answer', '42', '--fake'],
                ['--foo', '-b', '-B', 'alpha', 'beta', 'child', '--answer', '42', '--fake'],
                ['--foo', '-b', '-B', 'alpha', 'beta', 'gamma', 'child', '--answer', '42', '--fake'],
                ['--foo', '-b', '-B', 'alpha', 'beta', 'gamma', 'delta', 'child', '--answer', '42', '--fake'],
                ]
        for argv in argvariants:
            parser.feed(argv)
            checker = clap.checker.RedChecker(parser)
            self.assertRaises(clap.errors.UnrecognizedOptionError, checker._checksubcommand)
            self.assertRaises(clap.errors.UnrecognizedOptionError, checker.check)

    @unittest.skip('FIXME: maybe provide an option to force users to give operands even to non-top commands?')
    def testFluidRangeInvalidNumberOfOperandsBecauseCommandIsGivenTooFast(self):
        command = getTestCommand().setOperandsRange(no=[1, 4])
        child = clap.mode.RedCommand().addLocalOption(clap.option.Option(short='a', long='answer', arguments=['int']))
        command.addCommand(name='child', command=child)
        argv = ['--foo', '-b', '-B', 'child', '--answer', '42']
        parser = clap.parser.Parser(command).feed(argv)
        checker = clap.checker.RedChecker(parser)
        checker._checksubcommand()
        self.assertRaises(clap.errors.InvalidOperandRangeError, checker._checkoperandsrange)
        self.assertRaises(clap.errors.InvalidOperandRangeError, checker.check)

    def testFluidRangeInvalidNumberOfOperandsBecauseCommandIsGivenTooLate(self):
        command = getTestCommand().setOperandsRange(no=[1, 4])
        child = clap.mode.RedCommand().addLocalOption(clap.option.Option(short='a', long='answer', arguments=['int']))
        command.addCommand(name='child', command=child)
        argv = ['--foo', '-b', '-B', 'alpha', 'beta', 'gamma', 'delta', 'epsilon', 'child', '--answer', '42']
        parser = clap.parser.Parser(command).feed(argv)
        checker = clap.checker.RedChecker(parser)
        checker._checksubcommand()
        self.assertRaises(clap.errors.InvalidOperandRangeError, checker._checkoperandsrange)
        self.assertRaises(clap.errors.InvalidOperandRangeError, checker.check)

    def testFluidRangeInvalidNumberOfOperandsRaisedBeforeInvalidCommand(self):
        command = getTestCommand().setOperandsRange(no=[1, 4])
        child = clap.mode.RedCommand().addLocalOption(clap.option.Option(short='a', long='answer', arguments=['int']))
        command.addCommand(name='child', command=child)
        parser = clap.parser.Parser(command)
        argvariants = [
                ['--foo', '-b', '-B', 'fake', '--answer', '42'],
                ['--foo', '-b', '-B', 'alpha', 'beta', 'gamma', 'delta', 'epsilon', 'fake', '--answer', '42']
                ]
        for argv in argvariants:
            parser.feed(argv)
            checker = clap.checker.RedChecker(parser)
            self.assertRaises(clap.errors.UnrecognizedCommandError, checker._checksubcommand)
            self.assertRaises(clap.errors.InvalidOperandRangeError, checker.check)


if __name__ == '__main__':
    unittest.main()
