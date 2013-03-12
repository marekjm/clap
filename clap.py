#!/usr/bin/env python3

"""command line arguments parser"""

import sys

__version__ = "0.0.2"

class UnexpectedOptionError(Exception): pass
class MissingOptionError(Exception): pass
class SwitchValueError(Exception): pass
class ArgumentError(Exception):
    """
    Error raised when invalid argument was given to option or
    there was no argument when required.
    """
    pass

class NotParsedError(Exception): pass
class OptionNotFoundError(LookupError): pass


class Formatter():
    def __init__(self, short, long, argv):
        self.short = short
        self.long = long
        self.argv = argv

    def _formatshorts(self):
        """
        Method responsible for formatting short options list given to parser.
        """
        short, i = ([], 0)
        while i < len(self._short):
            option, n = ("-{0}", 1)
            try:
                if self._short[i+1] == ":":
                    n += 1
                    option += ":"
            except IndexError: 
                pass
            finally:
                short.append(option.format(self._short[i]))
            i += n
        self.short = short
    
    def _formatlongs(self):
        """
        Method responsible for formatting long options list given to parser.
        """
        self.long = [ "--{0}".format(opt) for opt in self.long ]
    
    def _islongopt(self, opt):
        """
        Checks if given string is a valid long option.
        """
        return (opt in self.long) or (opt+"=" in self.long)

    def splitequalsign(self):
        """
        Splits long options connected with their values by equal sign.
        """
        argv = []
        for a in self.argv:
            items = []
            if "=" in a:
                a = a.split("=", 1)
                if self._islongopt(a[0]):
                    items.append(a[0])
                    items.append(a[1])
                else:
                    items.append("=".join(a))
            else:
                items.append(a)
            argv.extend(items)
        self.argv = argv
    

class Parser():
    """
    Class utilizing methods used for parsing input from command line.
    """
    
    def __init__(self, short="", long=[], required=[], argv=[]):
        formatter = Formatter(short=short, long=long, argv=argv)
        formatter._formatshorts()
        formatter._formatlongs()
        formatter.splitequalsign()
        self._argv = formatter.argv
        self._short, self._long = (formatter.short, formatter.long)
        self._options, self._arguments = ([], [])
        self._required = required
    
    def _isopt(self, option, mode="b"):
        """
        Returns True if given option is accepted by thi instance of Parser().
        Modes are:
        'b' - for both types of options,
        's' - for short options,
        'l' - for long options,
        """
        if mode == "s": result = option in self._short
        elif mode == "l": result = option in self._long
        else: result = option in self._short or option in self._long
        return result

    def _passed(self, option):
        """
        Returns if at least one of given options have been passed. 
        False otherwise.
        """
        opts = [opt for opt, value in self._options]
        if option in opts: result = True
        else: result = False
        return result
    
    def format(self):
        """
        Formats options lists given to Parser().
        Has to be called before parse().
        """
        formatter = Formatter(short=self.short, long=self.long, argv=[])
        formatter._formatshorts()
        formatter._formatlongs()
        self._short, self._long = (formatter.short, formatter.long)
        
    def purge(self):
        """
        Resets *every* variable to empty state.
        """
        self._argv = []
        self._short, self._long = ("", [])
        self._options, self._arguments = ([], [])

    def clean(self):
        """
        Cleans parser - resets everything except `_argv`.
        """
        self._short, self._long = ("", [])
        self._options, self._arguments = ([], [])

    def addshort(self, option):
        """
        Appends option to list of recognized short options.
        """
        option = "-{0}".format(option)
        self.rmshort(option)
        self._short.append(option)

    def addlong(self, option):
        """
        Appends option to list of recognized short options.
        """
        option = "--{0}".format(option)
        self.rmlong(option)
        self._long.append(option)

    def rmshort(self, option):
        """
        Removes option from list of recognized short options.
        """
        if self._isopt(option): self._short.remove(option)
        elif self._isopt("{0}:".format(option)): self._short.remove("{0}:".format(option))
        elif self._isopt(option[:-1]): self._short.remove(option[:-1])

    def rmlong(self, option):
        """
        Removes option from list of recognized short options.
        """
        if self._isopt(option): self._long.remove(option)
        elif self._isopt("{0}=".format(option)): self._long.remove("{0}=".format(option))
        elif self._isopt(option[:-1]): self._long.remove(option[:-1])
    
    def _splitshorts(self):
        """
        Splits joined short options passed from the command line.
        '-lh' --> '-l -h'
        """
        argv, n = ([], 0)
        for i, arg in enumerate(self._argv):
            if arg[0] == "-" and arg[1] != "-": 
                arg = [ "-{0}".format(opt) for opt in list(arg)[1:] ]
            elif arg == "--":
                argv.append("--")
                n = i
                break
            else:
                arg = [arg]
            argv.extend(arg)
            n = i
        self._argv = argv + self._argv[n+1:]
    
    def parse(self):
        """
        Parses command line input to options and arguments.
        """
        self._splitshorts()
        options, arguments, i = ([], [], 0)
        while i < len(self._argv):
            option, argument = (self._argv[i], "")
            if self._isopt(option):
                pass
            elif self._isopt("{0}:".format(option)) or self._isopt("{0}=".format(option)):
                i += 1
                if i == len(self._argv): raise ArgumentError("option '{0}' requires argument".format(option))
                else: argument = self._argv[i]
            elif option == "--":
                arguments = self._argv[i+1:]
                break
            elif option[0] == "-" and option != "-":
                raise UnexpectedOptionError("unexpected option found: {0}".format(option))
            else:
                arguments = self._argv[i:]
                break
            options.append( (option, argument) )
            i += 1
        self._options = options
        self._arguments = arguments
        for o in self._required:
            if not self._passed(o): raise MissingOptionError("required option not found: {0}".format(o))


class Interface():
    """
    Clients should use this class as it provides an interface 
    to the internal methods and logic.
    """
    
    def __init__(self, short="", long=[], argv=[]):
        self._parser, self._parsed = (Parser(short=short, long=long, argv=argv), False)

    def parse(self):
        """
        Parses given command line input.
        """
        self._parser.format()
        self._parser.parse()
        self._options = dict(self._parser._options)
        self._arguments = self._parser._arguments
    
    def getopt(self, option):
        """
        Returns argument of given option or
        empty string if option does not accept arguments. 
        Raises KeyError when option was not passed.
        """
        return self._options[option]
    
    def getargs(self):
        """
        Returns list of arguments passed from command line.
        """
        return self._arguments

    def isopt(self, option, mode="b"):
        """
        Checks if given option is accepted in this instance.
        """
        return self._parser._isopt(option=option, mode=mode)
    
    def waspassed(self, option, *args):
        """
        Checks if given option have been passed.
        """
        args += (option,)
        result = True
        for o in args: 
            if not self._parser._passed(o):
                result = False
                break
        return result

    def listaccepted(self):
        """
        Returns sorted list of all options accepted by this interface.
        """
        options = []
        for opt in self._parser._short: options.append(opt)
        for opt in self._parser._long: options.append(opt)
        return sorted(options)
