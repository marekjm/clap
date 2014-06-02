"""RedCLAP parser module.
"""

from . import shared

try: from clap_typehandlers import TYPEHANDLERS
except ImportError: TYPEHANDLERS = {}
finally: pass


class Parser:
    """Object that, after being fed with command line arguments and mode,
    parses the arguments according to the mode.
    """
    def __init__(self, mode, argv=[]):
        self._args = argv
        self._mode, self._current = mode, mode
        self._parsed = {'options': {}, 'operands': []}
        self._breaker = False
        self._typehandlers = {'str': str, 'int': int, 'float': float}
        self._loadtypehandlers()

    def __contains__(self, option):
        """Checks if parser contains given option.
        """
        return option in self._parsed['options']

    def _loadtypehandlers(self):
        """Loads typehandlers from TYPEHANDLERS dict.
        """
        for name, callback in TYPEHANDLERS.items(): self._typehandlers[name] = callback

    def feed(self, argv):
        """Feed argv to parser.
        """
        self._args = argv
        return self

    def getargs(self):
        """Returns list of arguments.
        """
        return self._args

    def addTypeHandler(self, name, callback):
        """Registers type handler for custom type.
        """
        self._typehandlers[name] = callback
        return self

    def _getinput(self):
        """Returns list of options and arguments until '--' string or
        first non-option and non-option-argument string.
        Simple description: returns input without operands.
        """
        index, i = -1, 0
        input = []
        while i < len(self._args):
            item = self._args[i]
            #   if a breaker is encountered -> break
            if item == '--': break
            #   if non-option string is encountered and it's not an argument -> break
            if i == 0 and not shared.lookslikeopt(item): break
            if i > 0 and not shared.lookslikeopt(item) and not self._mode.params(self._args[i-1]): break
            #   if non-option string is encountered and it's an argument
            #   increase counter by the number of arguments the option requests and
            #   proceed further
            if i > 0 and not shared.lookslikeopt(item) and self._mode.params(self._args[i-1]):
                i += len(self._mode.params(self._args[i-1]))-1
            index = i
            i += 1
        if index >= 0:
            #   if index is at least equal to zero this means that some input was found
            input = self._args[:index+1]
        return input

    def _getoperands(self):
        """Returns list of operands passed.
        """
        n = len(self._getinput())
        operands = self._args[n:]
        if operands: self._breaker = (operands[0] == '--')
        if self._breaker and operands: operands.pop(0)
        operands = (operands[:operands.index('---')] if ('---' in operands and self._breaker) else operands[:])
        return operands

    def _getheuroperands(self):
        """Returns two-tuple: (operands-for-current-mode, items-for-child-mode).
        Uses simple algorithms to detect nested modes and split the operands.
        """

    def _ininput(self, option):
        """Check if given option is present in input.
        """
        is_in = False
        i = 0
        input = self._getinput()
        while i < len(input):
            s = input[i]
            if option.match(s):
                is_in = True
                break
            if shared.lookslikeopt(s) and self._mode.accepts(s): i += len(self._mode.getopt(s).params())
            i += 1
        return is_in

    def _strininput(self, string):
        """Check if given string is present in input.
        """
        is_in = False
        i = 0
        input = self._getinput()
        while i < len(input):
            s = input[i]
            if string == s:
                is_in = True
                break
            if shared.lookslikeopt(s) and self._mode.accepts(s): i += len(self._mode.getopt(s).params())
            i += 1
        return is_in

    def _whichaliasin(self, option):
        """Returns which variant of option (long or short) is present in input.
        Used internaly when checking input. Empty string indicates that no variant
        is present (option is not present).

        `option` takes precendence over `string`.

        :param option: option name
        :type option: str
        """
        input = self._getinput()
        #if string:
        #    name = string
        #    alias = self.alias(string)
        if option:
            name = str(option)
            alias = option.alias(name)
        variant = ''
        if name in input: variant = name
        if alias and (alias in input): variant = alias
        return variant

    def parse(self):
        """Parses given input.
        """
        options = []
        operands = []
        input = self._getinput()
        i = 0
        while i < len(input):
            item = input[i]
            if shared.lookslikeopt(item) and self._mode.accepts(item) and not self._mode.params(item):
                options.append( (item, None) )
                alias = self._mode.alias(item)
                if alias != item: options.append( (alias, None) )
            elif shared.lookslikeopt(item) and self._mode.accepts(item) and self._mode.params(item):
                n = len(self._mode.params(item))
                params = input[i+1:i+1+n]
                for j, callback in enumerate(self._mode.params(item)):
                    if type(callback) is str: callback = self._typehandlers[callback]
                    params[j] = callback(params[j])
                options.append( (item, params) )
                alias = self._mode.alias(item)
                if alias != item: options.append( (alias, params) )
                i += n
            else:
                break
            i += 1
        operands = self._args[i:]
        if operands and operands[0] == '--': operands.pop(0)
        for opt, args in options:
            if self._mode.getopt(opt)['plural'] and self._mode.getopt(opt).params():
                if opt not in self._parsed['options']: self._parsed['options'][opt] = []
                self._parsed['options'][opt].append(args)
            elif self._mode.getopt(opt)['plural'] and not self._mode.getopt(opt).params():
                if opt not in self._parsed['options']: self._parsed['options'][opt] = 0
                self._parsed['options'][opt] += 1
            else:
                self._parsed['options'][opt] = args
        self._parsed['operands'] = operands
        return self

    def get(self, key, tuplise=True):
        """Returns arguments passed to an option.
        - options that take no arguments return None,
        - options that are plural AND take no argument return number of times they were passed,
        - options that take exactly one argument return it directly,
        - options that take at least two arguments return tuple containing their arguments,
        - options that take at least one argument AND are plural return list of tuples containing arguments passed
          to each occurence of the option in input,
        
        Tuple-isation can be switched off by passing 'tuplise` parameter as false;
        in such case lists are returned for options that take at least two arguments and
        direct values for options taking one argumet or less.
        """
        option = self._mode.getopt(key)
        value = self._parsed['options'][key]
        if option.isplural() and not option.params(): return value
        if not option.params(): return None
        if len(option.params()) == 1 and not option.isplural(): return value[0]
        if tuplise: value = ([tuple(v) for v in value] if option.isplural() else tuple(value))
        return value

    def getoperands(self):
        """Returns list of operands.
        """
        return self._parsed['operands']
