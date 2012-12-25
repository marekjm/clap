#!/usr/bin/env python3

__version__ = "0.0.1"
__vertuple__ = tuple( int(i) for i in __version__.split(".") )

class UnexpectedOptionError(Exception): pass
class SwitchNotFoundError(Exception): pass
class NotTranslatedError(Exception): pass
class OptionNotFoundError(LookupError): pass

class Parser():
    def __init__(self, short, long=[], argv=[], synonyms=[]):
        self.descript_short = short
        self.descript_long = long
        self.synonyms = synonyms
        self.argv = argv
        self.opts = []
        self.args = []
        self.translated = False
        
        self._splitshorts()
    
    def _splitshorts(self):
        """
        This method extracts short options identifiers from string passed to Parser.
        """
        descript = []
        for i, opt in enumerate(self.descript_short):
            try:
                if self.descript_short[i+1] == ":": opt += ":"
            except IndexError: pass
            finally: descript.append("-{0}".format(opt))
        while "-:" in descript: descript.remove("-:")
        self.descript_short = descript

    def isopt(self, opt):
        """
        Checks if given string is a valid option for this parser.
        """
        case_two =  opt in self.descript_short or opt in self.descript_long
        case_one = "{0}:".format(opt) in self.descript_short or "{0}:".format(opt) in self.descript_long
        return case_one or case_two


    def _parseopts(self):
        """
        Parses options from the command line and assigns values to them if needed.
        """
        opts = []
        i = 0
        while i < len(self.argv):
            opt = self.argv[i]
            if opt in self.descript_short:
                value = ""
            elif "{0}:".format(opt) in self.descript_short:
                i += 1
                if self.isopt(self.argv[i]): raise SwitchNotFoundError("'{0}' option requires a switch".format(opt))
                value = self.argv[i]
            elif opt in self.descript_long:
                value = ""
            elif "{0}:".format(opt) in self.descript_long:
                i += 1
                if self.isopt(self.argv[i]): raise SwitchNotFoundError("'{0}' option requires a switch".format(opt))
                value = self.argv[i]
            elif opt == "--":
                i += 1
                break
            elif opt[0] == "-":
                raise UnexpectedOptionError("unexpected option found: '{0}'".format(opt))
            else:
                break
            opts.append( (opt, value) )
            i += 1
        self.opts = opts
        return i
    
    def parse(self):
        """
        Parses contents of `sys.argv` and splits them into options and arguments.
        """
        n = self._parseopts()
        self.args = self.argv[n:]
    
    def translate(self):
        """
        Translates `opts` from list of tuples to a dictionary.
        """
        self.opts = dict(self.opts)
        self.translated = True
    
    def getopt(self, opt):
        """
        Returns value of an option. 
        Raises KeyError if option has not been found.
        """
        if not self.translated: raise NotTranslatedError("you have to call `translate()` before using `getopt()`")
        if opt not in self.opts: raise OptionNotFoundError("'{0}' not found in passed options".format(opt))
        return self.opts[opt]

    def getargs(self):
        """
        Returns list of arguments passed from command line.
        """
        return self.args
