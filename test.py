#/usr/bin/env python3

import unittest
import clap

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
        p = clap.Parser(short="vV:", argv=["-v", "-V", "0.0.1"])
        p.parse()
        self.assertEqual([("-v", ""), ("-V", "0.0.1")], p.opts)

    def testParseWithLongOpts(self):
        p = clap.Parser(short="", long=["verbose", "version:"], argv=["--verbose", "--version", "0.0.1"])
        p.parse()
        self.assertEqual([("--verbose", ""), ("--version", "0.0.1")], p.opts)

    def testParseWithShortoptsAndLongopts(self):
        p = clap.Parser(short="vV:", long=["verbose", "version:"], argv=["--verbose", "-V", "0.0.1", "foo"])
        p.parse()
        self.assertEqual([("--verbose", ""), ("-V", "0.0.1")], p.opts)
        self.assertEqual(["foo"], p.args)


    def testParseWithBreakSign(self):
        p = clap.Parser(short="vV:", long=["verbose", "version:"], argv=["--verbose", "--", "-V", "0.0.1"])
        p.parse()
        self.assertEqual([("--verbose", "")], p.opts)
        self.assertEqual(["-V", "0.0.1"], p.args)


    def testParseWithMissingSwitch(self):
        p = clap.Parser(short="vV:", argv=["-V", "-v", "0.0.1"])
        self.assertRaises(clap.SwitchValueNotFoundError, p.parse)
        
        q = clap.Parser(short="", long=["verbose", "version:"], argv=["--version", "--verbose", "0.0.1"])
        self.assertRaises(clap.SwitchValueNotFoundError, q.parse)
        
        r = clap.Parser(short="v", long=["version:"], argv=["--version", "-v", "0.0.1"])
        self.assertRaises(clap.SwitchValueNotFoundError, r.parse)


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
    def testIsopt(self):
        p = clap.Parser(short="vV:fu:", long=["verbose", "version:", "user:", "force"])
        self.assertEqual(True, p.isopt("-v"))
        self.assertEqual(True, p.isopt("-V:"))
        self.assertEqual(True, p.isopt("-f"))
        self.assertEqual(True, p.isopt("-u:"))
        
        self.assertEqual(True, p.isopt("--verbose"))
        self.assertEqual(True, p.isopt("--version:"))
        self.assertEqual(True, p.isopt("--user:"))
        self.assertEqual(True, p.isopt("--force"))


class ListOptionsTest(unittest.TestCase):
    def testListPassed(self):
        p = clap.Parser(short="", long=[""], argv=["foo", "bar"])
        p.parse()
        self.assertEqual([], p.listpassed())

        q = clap.Parser(short="", long=["verbose"], argv=["--verbose", "foo", "bar"])
        q.parse()
        self.assertEqual(["--verbose"], q.listpassed())

        q = clap.Parser(short="v:", long=["verbose"], argv=["--verbose", "-v", "foo", "bar"])
        q.parse()
        self.assertEqual(["--verbose", "-v"], q.listpassed())

    def testListPassedRaisesErrorIfNotParsed(self):
        p = clap.Parser(short="", long=[""], argv=["foo", "bar"])
        self.assertRaises(clap.NotParsedError, p.listpassed)

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

if __name__ == "__main__": unittest.main()