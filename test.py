#/usr/bin/env python3

import unittest
import clap

class InitializationTest(unittest.TestCase):
    def testInitWithOnlyShortopts(self):
        p = clap.Parser(short="vV:")
        self.assertEqual(["-v", "-V:"], p.descript_short)
        self.assertEqual([], p.descript_long)

    def testInitWithOnlyLongopts(self):
        p = clap.Parser(short="", long=["--verbose", "--version"])
        self.assertEqual([], p.descript_short)
        self.assertEqual(["--verbose", "--version"], p.descript_long)

    def testInitWithShortoptsAndLongopts(self):
        p = clap.Parser(short="vV:", long=["--verbose", "--version:"])
        self.assertEqual(["-v", "-V:"], p.descript_short)
        self.assertEqual(["--verbose", "--version:"], p.descript_long)


class ParserTest(unittest.TestCase):
    def testParseWithShortOpts(self):
        p = clap.Parser(short="vV:", argv=["-v", "-V", "0.0.1"])
        p.parse()
        self.assertEqual([("-v", ""), ("-V", "0.0.1")], p.opts)
        p.translate()
        self.assertEqual({"-v": "", "-V": "0.0.1"}, p.opts)

    def testParseWithLongOpts(self):
        p = clap.Parser(short="", long=["--verbose", "--version:"], argv=["--verbose", "--version", "0.0.1"])
        p.parse()
        self.assertEqual([("--verbose", ""), ("--version", "0.0.1")], p.opts)
        p.translate()
        self.assertEqual({"--verbose": "", "--version": "0.0.1"}, p.opts)

    def testParseWithShortoptsAndLongopts(self):
        p = clap.Parser(short="vV:", long=["--verbose", "--version:"], argv=["--verbose", "-V", "0.0.1", "foo"])
        p.parse()
        self.assertEqual([("--verbose", ""), ("-V", "0.0.1")], p.opts)
        self.assertEqual(["foo"], p.args)
        p.translate()
        self.assertEqual({"--verbose": "", "-V": "0.0.1"}, p.opts)


    def testParseWithBreakSign(self):
        p = clap.Parser(short="vV:", long=["--verbose", "--version:"], argv=["--verbose", "--", "-V", "0.0.1"])
        p.parse()
        self.assertEqual([("--verbose", "")], p.opts)
        self.assertEqual(["-V", "0.0.1"], p.args)
        p.translate()
        self.assertEqual({"--verbose": ""}, p.opts)


    def testParseWithMissingSwitch(self):
        p = clap.Parser(short="vV:", argv=["-V", "-v", "0.0.1"])
        self.assertRaises(clap.SwitchNotFoundError, p.parse)
        
        q = clap.Parser(short="", long=["--verbose", "--version:"], argv=["--version", "--verbose", "0.0.1"])
        self.assertRaises(clap.SwitchNotFoundError, q.parse)
        
        r = clap.Parser(short="v", long=["--version:"], argv=["--version", "-v", "0.0.1"])
        self.assertRaises(clap.SwitchNotFoundError, r.parse)


class GetoptTest(unittest.TestCase):
    def testGetopt(self):
        p = clap.Parser(short="vV:", argv=["-v", "-V", "0.0.1"])
        p.parse()
        p.translate()
        self.assertEqual("0.0.1", p.getopt("-V"))

    def testGetoptRaisesNotTranslatedError(self):
        p = clap.Parser(short="vV:", argv=["-v", "-V", "0.0.1"])
        p.parse()
        self.assertRaises(clap.NotTranslatedError, p.getopt, "-V")

    def testGetoptRaisesNotTranslatedError(self):
        p = clap.Parser(short="vV:", argv=["-v", "-V", "0.0.1"])
        p.parse()
        self.assertRaises(clap.NotTranslatedError, p.getopt, "-V")

    def testGetoptRaisesOptionNotFoundError(self):
        p = clap.Parser(short="vV:", argv=["-v", "-V", "0.0.1"])
        p.parse()
        p.translate()
        self.assertRaises(clap.OptionNotFoundError, p.getopt, "-o")


if __name__ == "__main__": unittest.main()