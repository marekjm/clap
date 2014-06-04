"""Module containg mode implementation.
"""


from . import shared
from . import errors


class RedMode:
    """Mode implementation.
    """
    def __init__(self):
        self._options = {'local': [], 'global': []}
        self._operands = {'range': {'least': None, 'most': None}, 'types': []}
        self._modes = {}

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

    def removeLocalOption(self, name):
        """Remove local option matching the name given.
        """
        for i in self._options['local']:
            if i.match(name):
                self._options['local'].remove(i)
                break
        return self

    def removeGlobalOption(self, name):
        """Remove global option matching the name given.
        """
        for i in self._options['global']:
            if i.match(name):
                self._options['global'].remove(i)
                break

    def alias(self, o):
        """Returns alias (if found) for given option (string).
        """
        alias = ''
        for i in self.options():
            if i.match(o):
                alias = i.alias(o)
                break
        return alias

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

    def params(self, option):
        """Returns list of arguments (types) given option takes.
        """
        return self.getopt(option).params()

    def options(self, group=''):
        """Group may be 'local', 'global' or empty string.
        Empty string means 'local and global'.
        """
        if group == '': opts = self._options['local'] + self._options['global']
        elif group == 'local': opts = self._options[group]
        elif group == 'global': opts = self._options[group]
        else: raise TypeError('invalid option group: "{0}"'.format(group))
        return opts

    def propagate(self):
        """Propagate global options and
        type handlers to child modes.
        """
        for mode in self._modes:
            self._modes[mode]._options['global'] = []
            for opt in self._options['global']: self._modes[mode].addGlobalOption(opt)
            self._modes[mode].propagate()
        return self

    def _setoperandsrange(self, least, most):
        """Sets range of operands.
        Both arguments can be integers or None.
        None has different meaning in 
        """
        self._operands['range']['least'] = least
        self._operands['range']['most'] = most

    def setOperandsRange(self, no=()):
        """Sets range of operands.
        Valid `no` is a sequence - tuple or list - of zero, one, or two integers.
        """
        least, most = None, None
        if len(no) == 0:
            pass
        elif len(no) == 1 and no[0] >= 0:
            most = no[0]
        elif len(no) == 1 and no[0] < 0:
            least = -no[0]
        elif len(no) == 2 and no[0] >= 0 and no[1] >= 0:
            least, most = no[0], no[1]
        else:
            raise errors.InvalidOperandRangeError('provided sequence is invalid for operands range: {0}'.format(no))
        self._setoperandsrange(least, most)
        return self

    def getOperandsRange(self):
        """Returns operands range.
        """
        return (self._operands['range']['least'], self._operands['range']['most'])

    def setOperandsTypes(self, types):
        """Sets a list of operands types.
        Length of this list must be compatible with set range of operands.
        """
        self._operands['types'] = types
        return self

    def getOperandsTypes(self):
        """Return list of types of operands.
        """
        return self._operands['types']
