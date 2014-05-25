"""RedCLAP parser module.
"""

from . import shared


class Parser:
    """
    """
    def __init__(self, mode, argv=[]):
        self._args = argv
        self._mode, self._current = mode, mode
        self._parsed = {'options': {}, 'operands': []}
        self._typehandlers = {'str': str,
                              'int': int,
                              'float': float,
                              }

    def __contains__(self, option):
        """Checks if parser contains given option.
        """
        return option in self._parsed['options']

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
            #   proceed futher
            if i > 0 and not shared.lookslikeopt(item) and self._mode.params(self._args[i-1]):
                i += len(self._mode.params(self._args[i-1]))-1
            index = i
            i += 1
        if index >= 0:
            #   if index is at least equal to zero this means that some input was found
            input = self._args[:index+1]
        return input

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
        self._parsed['options'] = dict(options)
        self._parsed['operands'] = operands
        return self

    def get(self, key, tuplise=True):
        """Returns tuple of arguments passed to an option.
        """
        value = self._parsed['options'][key]
        if value is not None and tuplise: value = tuple(value)
        if value is not None and len(value) == 1 and not tuplise: value = value.pop(0)
        return value

    def getoperands(self):
        """Returns list of operands.
        """
        return self._parsed['operands']
