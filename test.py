#/usr/bin/env python3

import unittest
import clap

__version__ = "0.0.2"

class FormatterTests(unittest.TestCase):
    def testSplittinEqualSignedOptions(self):
        f = clap.Formatter(short="", long=["foo="], argv=["eggs", "--foo=bar", "-s", "pam"])
        f.splitequalsign()
        self.assertEqual(f.argv, ["eggs", "--foo", "bar", "-s", "pam"])


class ParserInitializationTests(unittest.TestCase):
    def testBlankInitialization(self):
        parser = clap.Parser()
        self.assertEqual(parser._short, "")
        self.assertEqual(parser._long, [])
        self.assertEqual(parser._argv, [])
        self.assertEqual(parser._options, [])
        self.assertEqual(parser._arguments, [])
        self.assertEqual(parser._required, [])

    def testFullInitialization(self):
        parser = clap.Parser(short="fb", long=["foo", "bar"], required=["f", "foo"], argv=["-f", "--foo", "-b", "--bar"])
        self.assertEqual(parser._short, "fb")
        self.assertEqual(parser._long, ["foo", "bar"])
        self.assertEqual(parser._argv, ["-f", "--foo", "-b", "--bar"])
        self.assertEqual(parser._options, [])
        self.assertEqual(parser._arguments, [])
        self.assertEqual(parser._required, ["f", "foo"])
    
    def testFromattingShortOptionsDescription(self):
        parser = clap.Parser(short="fb")
        parser._formatshorts()
        self.assertEqual(parser._short, ["-f", "-b"])

    def testFromattingShortOptionsRequestingArguments(self):
        parser = clap.Parser(short="f:b")
        parser._formatshorts()
        self.assertEqual(parser._short, ["-f:", "-b"])

    def testSupportForEqualSignForLongOptions(self):
        p = clap.Parser(short="", long=["with"], argv=["eggs", "--with=spam"])
        self.assertEqual(p._argv, ["eggs", "--with", "spam"])

    def testPurging(self):
        parser = clap.Parser(short="f:b", long=["foo=", "bar"], argv=["-f", "spam", "--bar", "spammer"])
        self.assertEqual(parser._short, "f:b")
        self.assertEqual(parser._long, ["foo=", "bar"])
        self.assertEqual(parser._argv, ["-f", "spam", "--bar", "spammer"])
        self.assertEqual(parser._options, [])
        self.assertEqual(parser._arguments, [])
        parser.purge()
        self.assertEqual(parser._short, "")
        self.assertEqual(parser._long, [])
        self.assertEqual(parser._argv, [])
        self.assertEqual(parser._options, [])
        self.assertEqual(parser._arguments, [])

    def testCleaning(self):
        parser = clap.Parser(short="f:b", long=["foo=", "bar"], argv=["-f", "spam", "--bar", "spammer"])
        self.assertEqual(parser._short, "f:b")
        self.assertEqual(parser._long, ["foo=", "bar"])
        self.assertEqual(parser._argv, ["-f", "spam", "--bar", "spammer"])
        self.assertEqual(parser._options, [])
        self.assertEqual(parser._arguments, [])
        parser.clean()
        self.assertEqual(parser._short, "")
        self.assertEqual(parser._long, [])
        self.assertEqual(parser._argv, ["-f", "spam", "--bar", "spammer"])
        self.assertEqual(parser._options, [])
        self.assertEqual(parser._arguments, [])


class ParserManipulationTests(unittest.TestCase):
    def testAddingShortOptionsWithoutArgument(self):
        parser = clap.Parser()
        parser.format()
        parser.addshort("f")
        parser.addshort("b:")
        self.assertEqual(parser._short, ["-f", "-b:"])

    def testAddingShortOptionsDoesNotDuplicateOptions(self):
        parser = clap.Parser()
        parser.format()
        parser.addshort("f")
        parser.addshort("f")
        self.assertEqual(parser._short, ["-f"])

    def testAddingShortOptionsDoesNotDuplicateOptionsWhenAddingArgument(self):
        parser = clap.Parser()
        parser.format()
        parser.addshort("f")
        parser.addshort("f:")
        self.assertEqual(parser._short, ["-f:"])

    def testAddingShortOptionsDoesNotDuplicateOptionsWhenRemovingArgument(self):
        parser = clap.Parser()
        parser.format()
        parser.addshort("f:")
        parser.addshort("f")
        self.assertEqual(parser._short, ["-f"])
    
    def testAddingLongOptions(self):
        parser = clap.Parser()
        parser.format()
        parser.addlong("foo")
        self.assertEqual(parser._long, ["--foo"])

    def testAddingLongOptionsDoesNotDuplicateOptions(self):
        parser = clap.Parser()
        parser.format()
        parser.addlong("foo")
        parser.addlong("foo")
        self.assertEqual(parser._long, ["--foo"])

    def testAddingLongOptionsDoesNotDuplicateOptionsWhenAddingArgument(self):
        parser = clap.Parser()
        parser.format()
        parser.addlong("foo")
        parser.addlong("foo=")
        self.assertEqual(parser._long, ["--foo="])

    def testAddingLongOptionsDoesNotDuplicateOptionsWhenRemovingArgument(self):
        parser = clap.Parser()
        parser.format()
        parser.addlong("foo")
        parser.addlong("foo=")
        self.assertEqual(parser._long, ["--foo="])
    
    def testRemovingShortOptions(self):
        parser = clap.Parser()
        parser.format()
        parser.addshort("f")
        parser.rmshort("-f")
        self.assertEqual(parser._short, [])

    def testRemovingLongOptions(self):
        parser = clap.Parser()
        parser.format()
        parser.addlong("foo")
        parser.rmlong("--foo")
        self.assertEqual(parser._long, [])
    
    def testPurging(self):
        parser = clap.Parser(short="f:b", long=["foo=", "bar"], argv=["-f", "spam", "--bar", "spammer"])
        parser.format()
        parser.parse()
        self.assertEqual(parser._short, ["-f:", "-b"])
        self.assertEqual(parser._long, ["--foo=", "--bar"])
        self.assertEqual(parser._argv, ["-f", "spam", "--bar", "spammer"])
        self.assertEqual(parser._options, [("-f", "spam"), ("--bar", "")])
        self.assertEqual(parser._arguments, ["spammer"])
        parser.purge()
        self.assertEqual(parser._short, "")
        self.assertEqual(parser._long, [])
        self.assertEqual(parser._argv, [])
        self.assertEqual(parser._options, [])
        self.assertEqual(parser._arguments, [])

    def testCleaning(self):
        parser = clap.Parser(short="f:b", long=["foo=", "bar"], argv=["-f", "spam", "--bar", "spammer"])
        parser.format()
        parser.parse()
        self.assertEqual(parser._short, ["-f:", "-b"])
        self.assertEqual(parser._long, ["--foo=", "--bar"])
        self.assertEqual(parser._argv, ["-f", "spam", "--bar", "spammer"])
        self.assertEqual(parser._options, [("-f", "spam"), ("--bar", "")])
        self.assertEqual(parser._arguments, ["spammer"])
        parser.clean()
        self.assertEqual(parser._short, "")
        self.assertEqual(parser._long, [])
        self.assertEqual(parser._argv, ["-f", "spam", "--bar", "spammer"])
        self.assertEqual(parser._options, [])
        self.assertEqual(parser._arguments, [])


class ParserTests(unittest.TestCase):
    def testValidOptionChecking(self):
        parser = clap.Parser(short="f:b", long=["foo=", "bar"])
        parser.format()
        self.assertEqual(parser._isopt("-f"), False)
        self.assertEqual(parser._isopt("-f:"), True)
        self.assertEqual(parser._isopt("-b"), True)
        self.assertEqual(parser._isopt("-v"), False)

        self.assertEqual(parser._isopt("--foo"), False)
        self.assertEqual(parser._isopt("--foo="), True)
        self.assertEqual(parser._isopt("--bar"), True)
        self.assertEqual(parser._isopt("--verbose"), False)

    def testSplittingShortOptions(self):
        parser = clap.Parser(short="f:bz", long=["foo=", "bar"], argv=["-f", "spam0", "-bz", "--bar"])
        parser.format()
        parser._splitshorts()
        self.assertEqual(parser._argv, ["-f", "spam0", "-b", "-z", "--bar"])
    
    def testSplittingShortOptionsWhichRequireArgument(self):
        parser = clap.Parser(short="f:bz", long=["foo=", "bar"], argv=["-bzf", "spam0", "--bar"])
        parser.format()
        parser._splitshorts()
        self.assertEqual(parser._argv, ["-b", "-z", "-f", "spam0", "--bar"])
    
    def testParseRaisesError(self):
        parser = clap.Parser(short="f:b", long=["foo=", "bar"], argv=["-f", "spam0", "-v", "-b", "--foo", "spam1", "--bar"])
        parser.format()
        self.assertRaises(clap.UnexpectedOptionError, parser.parse)

    def testParseSimple(self):
        parser = clap.Parser(short="f:b", long=["foo=", "bar"], argv=["-f", "spam0", "-b", "--foo", "spam1", "--bar"])
        parser.format()
        parser.parse()
        self.assertEqual(parser._options, [("-f", "spam0"), ("-b", ""), ("--foo", "spam1"), ("--bar", "")])
        self.assertEqual(parser._arguments, [])

    def testParseWithArguments(self):
        parser = clap.Parser(short="f:b", long=["foo=", "bar"], argv=["-f", "spam0", "-b", "--foo", "spam1", "--bar", "arguments"])
        parser.format()
        parser.parse()
        self.assertEqual(parser._options, [("-f", "spam0"), ("-b", ""), ("--foo", "spam1"), ("--bar", "")])
        self.assertEqual(parser._arguments, ["arguments"])
    
    def testParseWithMissingArgument(self):
        parser = clap.Parser(short="f:b", long=["foo=", "bar"], argv=["-f", "spam0", "-b", "--foo"])
        parser.format()
        self.assertRaises(clap.ArgumentError, parser.parse)
    
    def testParseWithBreaker(self):
        parser = clap.Parser(short="f:b", long=["foo=", "bar"], argv=["-f", "spam0", "-b", "--", "--foo", "spam1", "--bar"])
        parser.format()
        parser.parse()
        self.assertEqual(parser._options, [("-f", "spam0"), ("-b", "")])
        self.assertEqual(parser._arguments, ["--foo", "spam1", "--bar"])

    def testParseWhenOptionsAreJoined(self):
        parser = clap.Parser(short="f:bz", long=["foo=", "bar"], argv=["-bzf", "spam0", "--foo", "spam1", "--bar"])
        parser.format()
        parser.parse()
        self.assertEqual(parser._options, [("-b", ""), ("-z", ""), ("-f", "spam0"), ("--foo", "spam1"), ("--bar", "")])
        self.assertEqual(parser._arguments, [])

    def testMissingOptionRaisesError(self):
        p = clap.Parser(short="ba:r", required=["-a", "-r"], argv=["-b", "-a", "spam", "eggs"])
        p.format()
        self.assertRaises(clap.MissingOptionError, p.parse)


class InterfaceTests(unittest.TestCase):
    def testInitialization(self):
        interface = clap.Interface()
        self.assertEqual(type(interface._parser), clap.Parser)
        self.assertEqual(interface._parsed, False)
    
    def testParseMethod(self):
        interface = clap.Interface()
        interface.parse()
        self.assertEqual(interface._options, {})
    
    def testParseWithDuplicates(self):
        parser = clap.Interface(short="f:b", long=["foo=", "bar"], argv=["-f", "spam0", "-b", "--foo", "spam1", "--bar", "--foo", "spam2"])
        parser.parse()
        self.assertEqual(parser._options, {"-f":"spam0", "-b":"", "--foo":"spam2", "--bar":""})
        self.assertEqual(parser._arguments, [])

    def testOptionGetter(self):
        interface = clap.Interface(short="vV:", argv=["-v", "-V", "0.0.1"])
        interface.parse()
        self.assertEqual("0.0.1", interface.getopt("-V"))
        self.assertEqual("", interface.getopt("-v"))

    def testOptionGetterRaisesKeyError(self):
        interface = clap.Interface(short="vV:", argv=["-V", "0.0.1"])
        interface.parse()
        self.assertRaises(KeyError, interface.getopt, "-v")

    def testIsoptWithEnabledModeBoth(self):
        p = clap.Interface(short="v", long=["version="])
        p.parse()
        self.assertEqual(True, p.isopt("-v"))
        self.assertEqual(False, p.isopt("-v:"))
        
        self.assertEqual(True, p.isopt("--version="))
        self.assertEqual(False, p.isopt("--version"))

    def testIsoptWithEnabledModeShort(self):
        p = clap.Interface(short="v", long=["version="])
        p.parse()
        self.assertEqual(True, p.isopt("-v", mode="s"))
        self.assertEqual(False, p.isopt("-v:", mode="s"))
        
        self.assertEqual(False, p.isopt("--version=", mode="s"))
        self.assertEqual(False, p.isopt("--version", mode="s"))

    def testIsoptWithEnabledModeLong(self):
        p = clap.Interface(short="v", long=["version="])
        p.parse()
        self.assertEqual(False, p.isopt("-v", mode="l"))
        self.assertEqual(False, p.isopt("-v:", mode="l"))
        
        self.assertEqual(True, p.isopt("--version=", mode="l"))
        self.assertEqual(False, p.isopt("--version", mode="l"))

    def testWasPassed(self):
        p = clap.Interface(short="v", argv=["-v", "foo"])
        p.parse()
        self.assertEqual(True, p.waspassed("-v"))

    def testWasPassedMultiple(self):
        p = clap.Interface(short="v", long=["verbose"], argv=["-v", "--verbose", "foo"])
        p.parse()
        self.assertEqual(True, p.waspassed("-v", "--verbose"))

    def testArgumentsGetter(self):
        interface = clap.Interface(short="f:b", argv=["-f", "foo", "-b", "bar"])
        interface.parse()
        self.assertEqual(interface.getargs(), ["bar"])
    
    def testGettingListOfAcceptedOptions(self):
        interface = clap.Interface(short="f:bo:", long=["foo=", "bar", "output="])
        interface.parse()
        self.assertEqual(interface.listaccepted(), ["--bar", "--foo=", "--output=", "-b", "-f:", "-o:"])


if __name__ == "__main__": unittest.main()
