"""Module containg mode implementation.
"""


from . import shared


class RedMode:
    """Mode implementation.
    """
    def __init__(self):
        self._options = {'local': [], 'global': []}
        self._modes = {}
        self._operands = []
        self._args = []

    def feedargs(self, args):
        """Pass arguments to mode.
        """
        self._args = args

    def getargs(self):
        """Return list of arguments.
        """
        return self._args

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
            if i > 0 and not shared.lookslikeopt(item) and not self.type(self._args[i-1]): break
            #   if non-option string is encountered and it's an argument
            #   increase counter by the number of arguments the option requests and
            #   proceed futher
            if i > 0 and not shared.lookslikeopt(item) and self.type(self._args[i-1]):
                i += len(self.type(self._args[i-1]))-1
            index = i
            i += 1
        if index >= 0:
            #   if index is at least equal to zero this means that some input was found
            input = self._args[:index+1]
        return input

    def operands(self):
        """Returns copy of list of operands.
        """
        return self._operands[:]

    def addMode(self, name, mode):
        """Adds child mode.
        """
        self._modes[name] = mode
        return self

    def hasmode(self, name):
        """Returns true if mode has a child mode with given name.
        """
        return name in self._modes

    def getmode(self, name):
        """Returns child mode with given name.
        """
        return self._modes[name]

    def modes(self):
        """Returns list of supported child modes.
        """
        return [i for i in self._modes]

    def addLocalOption(self, o):
        """Appends option ot eh list of local options.
        """
        self._options['local'].append(o)
        return self

    def addGlobalOption(self, o):
        """Appends option ot eh list of local options.
        """
        self._options['global'].append(o)
        return self

    def propagate(self):
        """Propagate global options to child modes.
        """
        for mode in self._modes:
            for opt in self._options['global']:
                self._modes[mode].addGlobalOption(opt)
            self._modes[mode].propagate()
        return self

    def getopt(self, name):
        """Returns option with given name.
        """
        opt = None
        for i in self.options():
            if i.match(name):
                opt = i
                break
        if opt is None: raise KeyError(name)
        return opt

    def accepts(self, opt):
        """Returns true if mode accepts 'opt' option.
        """
        accepts = False
        for i in self._options['local'] + self._options['global']:
            if i.match(opt):
                accepts = True
                break
        return accepts

    def options(self, group=''):
        """Group may be 'local', 'global' or empty string.
        Empty string means 'local and global'.
        """
        if group == '': opts = self._options['local'] + self._options['global']
        elif group == 'local': opts = self._options[group]
        elif group == 'global': opts = self._options[group]
        else: raise TypeError('invalid option group: "{0}"'.format(group))
        return opts
