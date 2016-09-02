"""Module containg CLAP command implementation.
"""


from . import shared
from . import errors


class RedCommand:
    """RedCLAP command implementation.
    This class represents a ginle command of a commandline program's UI.
    It may contain various options, and subcomand.
    """
    def __init__(self):
        self._options = {'local': [], 'global': []}
        self._operands = {'range': {'least': None, 'most': None}, 'types': []}
        self._altoperands = {}
        self._commands = {}
        self._doc = {'help': '', 'usage': []}

    def __eq__(self, other):
        """Compares two commands for equality.
        """
        opts = (self._options == other._options)
        operands = (self._operands == other._operands)
        commands = (self._commands == other._commands)
        doc = (self._doc == other._doc)
        return opts and operands and commands and doc

    def setdoc(self, help=None, usage=None, examples=None):
        """Set some basic doc about the command.
        """
        if help is not None: self._doc['help'] = help
        if usage is not None: self._doc['usage'] = usage
        if examples is not None: self._doc['examples'] = examples
        return self

    def addCommand(self, name, command):
        """Adds subcommand.
        """
        self._commands[name] = command
        return self

    def expandCommandName(self, name, missing=False):
        """Accepts a string and returns a command name it can be expanded to.
        Raises exceptions on ambiguous or unmatched strings.

        Examples:

            commands = ['foo', 'bar'] and name = 'f' -> command = 'foo'
            commands = ['foo', 'bar'] and name = 'x' -> UnrecognizedCommandError
            commands = ['foo', 'far'] and name = 'f' -> AmbiguousCommandError
        """
        candidates = []
        for cmd in self.commands():
            if cmd.startswith(name):
                if len(cmd) == len(name):
                    candidates = [cmd]
                    break
                candidates.append(cmd)
        if not candidates and not missing:
            raise errors.UnrecognizedCommandError(name)
        elif not candidates and missing:
            return None
        if len(candidates) > 1:
            raise errors.AmbiguousCommandError('{0}: {1}'.format(name, ', '.join(candidates)))
        return candidates[0]

    def hasCommand(self, name):
        """Returns true if command has a subcommand with given name.
        """
        return name in self.commands()

    def getCommand(self, name, expand=True):
        """Returns subcommand with given name.
        """
        return self._commands[(self.expandCommandName(name) if expand else name)]

    def commands(self):
        """Returns list of subcommand.
        """
        return [i for i in self._commands]

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
        for i in self.options():
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
        for mode in self._commands:
            # do not overwrite options defined directly in nested modes
            for opt in self._options['global']: (self._commands[mode].addGlobalOption(opt) if opt not in self._commands[mode]._options['global'] else None)
            self._commands[mode].propagate()
        return self

    def _setoperandsrange(self, least, most):
        """Sets range of operands.
        Both arguments can be integers or None.
        None has different meaning in
        """
        self._operands['range']['least'] = least
        self._operands['range']['most'] = most

    def _setaltoperandsrange(self, conf):
        """Sets alternative range of operands.
        Allows to configure operand settings based on what options were passed.
        """
        self._altoperands = conf

    def setOperandsRange(self, no=()):
        """Sets range of operands.
        Valid `no` is a sequence - tuple or list - of zero, one, or two integers.
        """
        least, most = None, None
        if no: no = ([0] + list(no[1:]) if no[0] is None else no)
        if len(no) == 0:
            pass
        elif len(no) == 1 and no[0] < 0:
            least, most = 0, -no[0]
        elif len(no) == 1 and no[0] >= 0:
            least = no[0]
        elif len(no) == 2 and no[0] >= 0 and no[1] is None:
            least = no[0]
        elif len(no) == 2 and no[0] >= 0 and no[1] >= 0 and no[0] <= no[1]:
            least, most = no[0], no[1]
        else:
            raise errors.InvalidOperandRangeError('provided sequence is invalid for operands range: {0}'.format(no))
        self._setoperandsrange(least, most)
        return self

    def setAlternativeOperandsRange(self, no):
        """Sets range of operands.
        Valid `no` is a sequence - tuple or list - of zero, one, or two integers.
        """
        self._setaltoperandsrange(no)
        return self

    def getOperandsRange(self):
        """Returns operands range.
        """
        return (self._operands['range']['least'], self._operands['range']['most'])

    def getAlternativeOperandsRange(self, with_option):
        """Returns alternative operands range.
        """
        return tuple(self._altoperands.get(with_option, (None, None)))

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
