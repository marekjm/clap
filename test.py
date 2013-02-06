#/usr/bin/env python3

import unittest
import clap

__version__ = "0.2.2"

class InitializationTest(unittest.TestCase):
    def testInitWithOnlyShortopts(self):
        p = clap.Parser(short="vV:")
        self.assertEqual(["-v", "-V:"], p.descript_short)
        self.assertEqual([], p.descript_long)

    def testInitWithOnlyLongopts(self):
        p = clap.Parser(short="", long=["verbose", "version"])
        self.assertEqual([], p.descript_short)
        self.assertEqual(["verbose", "version"], p.descript_long)

    def testInitWithShortoptsAndLongopts(self):
        p = clap.Parser(short="vV:", long=["verbose", "version:"])
        self.assertEqual(["-v", "-V:"], p.descript_short)
        self.assertEqual(["verbose", "version:"], p.descript_long)


class ParserTest(unittest.TestCase):
    def testParseWithShortOpts(self):
        """
        Tests general ability to understand short options.
        """
        p = clap.NewParser(short="vV:", argv=["-v", "-V", "0.0.1"])
        p.format()
        p.parse()
        self.assertEqual([("-v", ""), ("-V", "0.0.1")], p._options)

    def testParseWithConnectedShortOpts(self):
        """
        Tests the general ability to understand short options passed together. 
        """
        p = clap.NewParser(short="vfV:", argv=["-vf", "-V", "0.0.1"])
        p.format()
        p.parse()
        self.assertEqual([("-v", ""), ("-f", ""), ("-V", "0.0.1")], p._options)

    def testParseWithConnectedShortOptsAndLong(self):
        """
        Tests if _splitshorts() will correctly scan and parse short options mixed with long ones. 
        """
        p = clap.NewParser(short="vfV:op", long=["verbose"], argv=["-vf", "--verbose", "-V", "0.0.1", "-po"])
        p.format()
        p.parse()
        self.assertEqual([("-v", ""), ("-f", ""), ("--verbose", ""), ("-V", "0.0.1"), ("-p", ""), ("-o", "")], p._options)

    def testParseWithConnectedShortOptsAndLongAndArgs(self):
        """
        Tests if _splitshorts() will not take arguments as options.
        """
        p = clap.NewParser(short="vfV:op", long=["verbose"], argv=["-vf", "--verbose", "-V", "0.0.1", "-po", "foo", "bar"])
        p.format()
        p.parse()
        self.assertEqual([("-v", ""), ("-f", ""), ("--verbose", ""), ("-V", "0.0.1"), ("-p", ""), ("-o", "")], p._options)
        self.assertEqual(["foo", "bar"], p._arguments)

    def testParseWithConnectedShortOptsWithBreak(self):
        """
        Tests if _splitshorts() will not scan options-like strings (even valid) after finding a `break` sign. 
        """
        p = clap.NewParser(short="vfV:op", long=["verbose"], argv=["-vf", "--verbose", "-V", "0.0.1", "--", "-po"])
        p.format()
        p.parse()
        self.assertEqual([("-v", ""), ("-f", ""), ("--verbose", ""), ("-V", "0.0.1")], p._options)
        self.assertEqual(["-po"], p._arguments)

    def testParseWithConnectedShortOptsWithBreakMoreComplex(self):
        """
        Tests if _splitshorts() will not scan options-like strings (even valid) after finding a `break` sign.
        More complex test from the `NewParserTest.testParseWithConnectedShortOptsWithBreak()` test.
        """
        p = clap.NewParser(short="vfV:op", long=["verbose"], argv=["-vf", "--verbose", "-V", "0.0.1", "-po", "--", "-po"])
        p.format()
        p.parse()
        self.assertEqual([("-v", ""), ("-f", ""), ("--verbose", ""), ("-V", "0.0.1"), ("-p", ""), ("-o", "")], p._options)
        self.assertEqual(["-po"], p._arguments)

    def testParseWithLongOpts(self):
        """
        Tests general ability to understand long options.
        """
        p = clap.NewParser(short="", long=["verbose", "version:"], argv=["--verbose", "--version", "0.0.1"])
        p.format()
        p.parse()
        self.assertEqual([("--verbose", ""), ("--version", "0.0.1")], p._options)

    def testParseWithShortoptsAndLongopts(self):
        """
        Tests general ability to understand short and long options mixed together.
        """
        p = clap.NewParser(short="vV:", long=["verbose", "version:"], argv=["--verbose", "-V", "0.0.1", "-v", "foo"])
        p.format()
        p.parse()
        self.assertEqual([("--verbose", ""), ("-V", "0.0.1"), ("-v", "")], p._options)
        self.assertEqual(["foo"], p._arguments)


    def testParseWithBreakSign(self):
        """
        Tests if break sign (`--`) is understood correctly.
        """
        p = clap.NewParser(short="vV:", long=["verbose", "version:"], argv=["--verbose", "--", "-V", "0.0.1"])
        p.format()
        p.parse()
        self.assertEqual([("--verbose", "")], p._options)
        self.assertEqual(["-V", "0.0.1"], p._arguments)


    def testParseWithMissingSwitchAtTheEnd(self):
        """
        Tests if parser complains about missing switch in options that require it (only at the end).
        """
        p = clap.NewParser(short="v:V:", argv=["-V", "0.0.1", "-v"])
        p.format()  
        self.assertRaises(clap.ArgumentError, p.parse)


class GetoptTest(unittest.TestCase):
    def testGetopt(self):
        p = clap.Parser(short="vV:", argv=["-v", "-V", "0.0.1"])
        p.parse()
        self.assertEqual("0.0.1", p.getopt("-V"))

    def testGetoptRaisesOptionNotFoundError(self):
        p = clap.Parser(short="vV:", argv=["-v", "-V", "0.0.1"])
        p.parse()
        self.assertRaises(clap.OptionNotFoundError, p.getopt, "-o")


class IsoptTest(unittest.TestCase):
    def testIsoptBoth(self):
        p = clap.Parser(short="vV:", long=["verbose", "version:"])
        self.assertEqual(True, p.isopt("-v"))
        self.assertEqual(True, p.isopt("-V:"))
        self.assertEqual(False, p.isopt("-f"))
        self.assertEqual(False, p.isopt("-u:"))
        
        self.assertEqual(True, p.isopt("--verbose"))
        self.assertEqual(True, p.isopt("--version:"))
        self.assertEqual(False, p.isopt("--user:"))
        self.assertEqual(False, p.isopt("--force"))

    def testIsoptShort(self):
        p = clap.Parser(short="vV:", long=["verbose", "version:"])
        self.assertEqual(True, p.isopt("-v", mode="s"))
        self.assertEqual(True, p.isopt("-V:", mode="s"))
        self.assertEqual(False, p.isopt("-f", mode="s"))
        self.assertEqual(False, p.isopt("-u:", mode="s"))
        
        self.assertEqual(False, p.isopt("--verbose", mode="s"))
        self.assertEqual(False, p.isopt("--version:", mode="s"))
        self.assertEqual(False, p.isopt("--user:", mode="s"))
        self.assertEqual(False, p.isopt("--force", mode="s"))

    def testIsoptLong(self):
        p = clap.Parser(short="vV:", long=["verbose", "version:"])
        self.assertEqual(False, p.isopt("-v", mode="l"))
        self.assertEqual(False, p.isopt("-V:", mode="l"))
        self.assertEqual(False, p.isopt("-f", mode="l"))
        self.assertEqual(False, p.isopt("-u:", mode="l"))
        
        self.assertEqual(True, p.isopt("--verbose", mode="l"))
        self.assertEqual(True, p.isopt("--version:", mode="l"))
        self.assertEqual(False, p.isopt("--user:", mode="l"))
        self.assertEqual(False, p.isopt("--force", mode="l"))
    
    def testAreoptsShort(self):
        p = clap.Parser(short="vV:")
        self.assertEqual(True, p._areopts(["-v", "-V:"], mode="s"))
        self.assertEqual(False, p._areopts(["-v", "-o"], mode="s"))


class ListOptionsTest(unittest.TestCase):
    def testListPassed(self):
        p = clap.Parser(short="", long=[""], argv=["foo", "bar"])
        p.parse()
        self.assertEqual([], p.getpassed())

        q = clap.Parser(short="", long=["verbose"], argv=["--verbose", "foo", "bar"])
        q.parse()
        self.assertEqual(["--verbose"], q.getpassed())

        q = clap.Parser(short="v:", long=["verbose"], argv=["--verbose", "-v", "foo", "bar"])
        q.parse()
        self.assertEqual(["--verbose", "-v"], q.getpassed())

    def testListPassedRaisesErrorIfNotParsed(self):
        p = clap.Parser(short="", long=[""], argv=["foo", "bar"])
        self.assertRaises(clap.NotParsedError, p.getpassed)

    def testListAccepted(self):
        p = clap.Parser(short="", long=[""], argv=["foo", "bar"])
        p.parse()
        self.assertEqual([], p.listaccepted())

        q = clap.Parser(short="", argv=["foo", "bar"])
        q.parse()
        self.assertEqual([], q.listaccepted())

        r = clap.Parser(short="", long=["verbose"], argv=["--verbose", "foo", "bar"])
        r.parse()
        self.assertEqual(["--verbose"], r.listaccepted())

        s = clap.Parser(short="v:", long=["verbose"], argv=["--verbose", "-v", "foo", "bar"])
        s.parse()
        self.assertEqual(["-v:", "--verbose"], s.listaccepted())

    def testGetshorts(self):
        p = clap.Parser(short="vV:")
        self.assertEqual(["-v", "-V:"], p.getshorts())


    def testGetlongs(self):
        p = clap.Parser(long=["version", "verbose:"])
        self.assertEqual(["--version", "--verbose:"], p.getlongs())


class WaspassedTest(unittest.TestCase):
    def testIfOptionWasPassed(self):
        p = clap.Parser(short="V:o:f",long=["verbose:", "output:", "force"])
        p.setargv(["--verbose", "3", "-f", "--output", "foo.txt"])
        p.parse()
        
        self.assertEqual(True, p.waspassed("--verbose"))
        self.assertEqual(True, p.waspassed("-f"))
        self.assertEqual(True, p.waspassed("--output"))
        
        self.assertEqual(False, p.waspassed("-V"))
        self.assertEqual(False, p.waspassed("--force"))
        self.assertEqual(False, p.waspassed("-o"))

    def testIfOptionWasPassedMultiple(self):
        p = clap.Parser(short="V:o:f",long=["verbose:", "output:", "force"])
        p.setargv(["--verbose", "3", "-f", "--output", "foo.txt"])
        p.parse()
        
        self.assertEqual(True, p.waspassed("--verbose", "-V"))
        self.assertEqual(True, p.waspassed("-f", "--force"))

        self.assertEqual(False, p.waspassed("-V", "-o"))


#   tests for NewParser()
class ParserInitializationTests(unittest.TestCase):
    def testBlankInitialization(self):
        parser = clap.NewParser()
        self.assertEqual(parser._short, "")
        self.assertEqual(parser._long, [])
        self.assertEqual(parser._argv, [])
        self.assertEqual(parser._options, [])
        self.assertEqual(parser._arguments, [])

    def testFullInitialization(self):
        parser = clap.NewParser(short="fb", long=["foo", "bar"], argv=["-f", "--foo", "-b", "--bar"])
        self.assertEqual(parser._short, "fb")
        self.assertEqual(parser._long, ["foo", "bar"])
        self.assertEqual(parser._argv, ["-f", "--foo", "-b", "--bar"])
        self.assertEqual(parser._options, [])
        self.assertEqual(parser._arguments, [])
    
    def testFromattingShortOptionsDescription(self):
        parser = clap.NewParser(short="fb")
        parser._formatshorts()
        self.assertEqual(parser._short, ["-f", "-b"])

    def testFromattingShortOptionsRequestingArguments(self):
        parser = clap.NewParser(short="f:b")
        parser._formatshorts()
        self.assertEqual(parser._short, ["-f:", "-b"])

    def testPurging(self):
        parser = clap.NewParser(short="f:b", long=["foo=", "bar"], argv=["-f", "spam", "--bar", "spammer"])
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
        parser = clap.NewParser(short="f:b", long=["foo=", "bar"], argv=["-f", "spam", "--bar", "spammer"])
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
        parser = clap.NewParser()
        parser.format()
        parser.addshort("f")
        parser.addshort("b:")
        self.assertEqual(parser._short, ["-f", "-b:"])

    def testAddingShortOptionsDoesNotDuplicateOptions(self):
        parser = clap.NewParser()
        parser.format()
        parser.addshort("f")
        parser.addshort("f")
        self.assertEqual(parser._short, ["-f"])

    def testAddingShortOptionsDoesNotDuplicateOptionsWhenAddingArgument(self):
        parser = clap.NewParser()
        parser.format()
        parser.addshort("f")
        parser.addshort("f:")
        self.assertEqual(parser._short, ["-f:"])

    def testAddingShortOptionsDoesNotDuplicateOptionsWhenRemovingArgument(self):
        parser = clap.NewParser()
        parser.format()
        parser.addshort("f:")
        parser.addshort("f")
        self.assertEqual(parser._short, ["-f"])
    
    def testAddingLongOptions(self):
        parser = clap.NewParser()
        parser.format()
        parser.addlong("foo")
        self.assertEqual(parser._long, ["--foo"])

    def testAddingLongOptionsDoesNotDuplicateOptions(self):
        parser = clap.NewParser()
        parser.format()
        parser.addlong("foo")
        parser.addlong("foo")
        self.assertEqual(parser._long, ["--foo"])

    def testAddingLongOptionsDoesNotDuplicateOptionsWhenAddingArgument(self):
        parser = clap.NewParser()
        parser.format()
        parser.addlong("foo")
        parser.addlong("foo=")
        self.assertEqual(parser._long, ["--foo="])

    def testAddingLongOptionsDoesNotDuplicateOptionsWhenRemovingArgument(self):
        parser = clap.NewParser()
        parser.format()
        parser.addlong("foo")
        parser.addlong("foo=")
        self.assertEqual(parser._long, ["--foo="])
    
    def testRemovingShortOptions(self):
        parser = clap.NewParser()
        parser.format()
        parser.addshort("f")
        parser.rmshort("-f")
        self.assertEqual(parser._short, [])

    def testRemovingLongOptions(self):
        parser = clap.NewParser()
        parser.format()
        parser.addlong("foo")
        parser.rmlong("--foo")
        self.assertEqual(parser._long, [])
    
    def testPurging(self):
        parser = clap.NewParser(short="f:b", long=["foo=", "bar"], argv=["-f", "spam", "--bar", "spammer"])
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
        parser = clap.NewParser(short="f:b", long=["foo=", "bar"], argv=["-f", "spam", "--bar", "spammer"])
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


class NewParserTests(unittest.TestCase):
    def testValidOptionChecking(self):
        parser = clap.NewParser(short="f:b", long=["foo=", "bar"])
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
        parser = clap.NewParser(short="f:bz", long=["foo=", "bar"], argv=["-f", "spam0", "-bz", "--bar"])
        parser.format()
        parser._splitshorts()
        self.assertEqual(parser._argv, ["-f", "spam0", "-b", "-z", "--bar"])
    
    def testSplittingShortOptionsWhichRequireArgument(self):
        parser = clap.NewParser(short="f:bz", long=["foo=", "bar"], argv=["-bzf", "spam0", "--bar"])
        parser.format()
        parser._splitshorts()
        self.assertEqual(parser._argv, ["-b", "-z", "-f", "spam0", "--bar"])
    
    def testParseRaisesError(self):
        parser = clap.NewParser(short="f:b", long=["foo=", "bar"], argv=["-f", "spam0", "-v", "-b", "--foo", "spam1", "--bar"])
        parser.format()
        self.assertRaises(clap.UnexpectedOptionError, parser.parse)

    def testParseSimple(self):
        parser = clap.NewParser(short="f:b", long=["foo=", "bar"], argv=["-f", "spam0", "-b", "--foo", "spam1", "--bar"])
        parser.format()
        parser.parse()
        self.assertEqual(parser._options, [("-f", "spam0"), ("-b", ""), ("--foo", "spam1"), ("--bar", "")])
        self.assertEqual(parser._arguments, [])

    def testParseWithArguments(self):
        parser = clap.NewParser(short="f:b", long=["foo=", "bar"], argv=["-f", "spam0", "-b", "--foo", "spam1", "--bar", "arguments"])
        parser.format()
        parser.parse()
        self.assertEqual(parser._options, [("-f", "spam0"), ("-b", ""), ("--foo", "spam1"), ("--bar", "")])
        self.assertEqual(parser._arguments, ["arguments"])
    
    def testParseWithMissingArgument(self):
        parser = clap.NewParser(short="f:b", long=["foo=", "bar"], argv=["-f", "spam0", "-b", "--foo"])
        parser.format()
        self.assertRaises(clap.ArgumentError, parser.parse)
    
    def testParseWithBreaker(self):
        parser = clap.NewParser(short="f:b", long=["foo=", "bar"], argv=["-f", "spam0", "-b", "--", "--foo", "spam1", "--bar"])
        parser.format()
        parser.parse()
        self.assertEqual(parser._options, [("-f", "spam0"), ("-b", "")])
        self.assertEqual(parser._arguments, ["--foo", "spam1", "--bar"])

    def testParseWhenOptionsAreJoined(self):
        parser = clap.NewParser(short="f:bz", long=["foo=", "bar"], argv=["-bzf", "spam0", "--foo", "spam1", "--bar"])
        parser.format()
        parser.parse()
        self.assertEqual(parser._options, [("-b", ""), ("-z", ""), ("-f", "spam0"), ("--foo", "spam1"), ("--bar", "")])
        self.assertEqual(parser._arguments, [])


class InterfaceTests(unittest.TestCase):
    def testInitialization(self):
        interface = clap.Interface()
        self.assertEqual(type(interface._parser), clap.NewParser)
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