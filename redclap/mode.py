"""Module containg mode implementation.
"""


from . import shared


class RedMode:
    """Mode implementation.
    """
    def __init__(self):
        self._options = {'local': [], 'global': []}
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
            for opt in self._options['global']: self._modes[mode].addGlobalOption(opt)
            self._modes[mode].propagate()
        return self
