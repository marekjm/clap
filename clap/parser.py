"""This module holds logic responsible for parsing arguments lists and
providing programming interface to interact with them.
"""

from . import shared, errors


class ParsedUI:
    """Object returned by parser, containing parsed commandline arguments in a usale form.
    """
    def __init__(self, command=None):
        self._options = {}
        self._operands = []
        self._name = ''
        self._command = command
        self._child, self._parent = None, None

    def __contains__(self, option):
        """Check if option is present.
        """
        return option in self._options

    def __iter__(self):
        """Return iterator over operands.
        """
        return iter(self._operands)

    def __str__(self):
        """Return name of current command.
        """
        return self._name

    def __len__(self):
        """Return number of operands.
        """
        return len(self._operands)

    def _appendcommand(self, command):
        """Append parsed subcommand.
        """
        command._parent = self
        self._child = command

    def down(self):
        """Go to nested mode.
        """
        return (self._child if self._child is not None else self)

    def up(self):
        """Go to parent mode.
        """
        return (self._parent if self._parent is not None else self)

    def top(self):
        """Go to top of command chain.
        """
        cherry = self
        while cherry._parent is not None: cherry = cherry._parent
        return cherry

    def islast(self):
        """Return true if current mode has no nested modes.
        """
        return self._child is None

    def finalise(self):
        """Perform needed finalisation.
        """
        if self._child is not None:
            for k, v in self._options.items():
                is_global, match = False, None
                for o in self._command.options(group='global'):
                    if o.match(k):
                        is_global, match = True, o
                        break
                if is_global:
                    if k in self._child._options and match.isplural() and not match.params(): self._child._options[k] += v
                    if k not in self._child._options: self._child._options[k] = v
            self._child.finalise()
        return self

    def get(self, key, tuplise=True, default=None):
        """Returns arguments passed to an option.
        - options that take no arguments and are not plural return None,
        - options that are plural AND take no argument return number of times they were passed,
        - options that take exactly one argument return it directly,
        - options that take at least two arguments return tuple containing their arguments,
        - options that take at least one argument AND are plural return list of tuples containing arguments passed
          to each occurence of the option in input,

        Tuple-isation can be switched off by passing 'tuplise` parameter as false;
        in such case lists are returned for options that take at least two arguments and
        direct values for options taking one argumet or less.
        """
        option = self._command.getopt(key)
        value = self._options.get(key, (default,))
        if option.isplural() and not option.params():
            # return 0 for not-passed plural options
            return (value if type(value) is int else 0)
        if not option.params(): return None
        if len(option.params()) == 1 and not option.isplural(): return value[0]
        if tuplise: return ([tuple(v) for v in value if v is not None] if option.isplural() else tuple(value))
        return value

    def operands(self):
        """Return copy of the list of operands.
        """
        return self._operands[:]


class Parser:
    """Object that, after being fed with command line arguments and mode,
    parses the arguments according to the mode.
    """
    def __init__(self, command, argv=[]):
        self._args = argv
        self._command, self._current = command, command
        self._parsed = {'options': {}, 'operands': []}
        self._implied_options = []
        self._breaker = False
        self._ui = None
        self._typehandlers = {'str': str, 'int': int, 'float': float}

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
        while i < len(self._args):
            item = self._args[i]
            if item == '--': break
            #   if non-option string is encountered and it's not an argument -> break
            if i == 0 and not shared.lookslikeopt(item): break
            if i > 0 and not shared.lookslikeopt(item) and not shared.lookslikeopt(self._args[i-1]): break
            if i > 0 and not shared.lookslikeopt(item) and shared.lookslikeopt(self._args[i-1]) and not self._command.params(self._args[i-1]): break
            #   if non-option string is encountered and it is an argument
            #   increase counter by the number of arguments the option requests and
            #   proceed further
            if i > 0 and not shared.lookslikeopt(item) and shared.lookslikeopt(self._args[i-1]) and self._command.params(self._args[i-1]):
                i += len(self._command.params(self._args[i-1]))-1
            index = i
            i += 1
        return (self._args[:index+1] if index >= 0 else []) # if index is at least equal to zero this means that some input was found

    def _getoperands(self, heur=True):
        """Returns list of operands passed.
        """
        if heur and self._command.commands() and self.getOperandsRange()[1] is not None: return self._getheuroperands()[0]
        n = len(self._getinput())
        operands = self._args[n:]
        if operands: self._breaker = (operands[0] == '--')
        if self._breaker and operands: operands.pop(0)
        operands = (operands[:operands.index('---')] if ('---' in operands and self._breaker) else operands[:])
        return operands

    def _isAcceptedInChildModes(self, option):
        """Return true if given option is accepted in at least one child mode.
        """
        accepted = False
        for m in self._command.commands():
            if self._command.getCommand(m).accepts(option):
                accepted = True
                break
        return accepted

    def _heuralgo(self, opers):
        """Algorithm for fixed ranges of operands.
        """
        operands, nested = [], []
        i = 0
        while i < len(opers):
            item = opers[i]
            command_name = item
            try:
                command_name = self._command.expandCommandName(command_name)
            except errors.UnrecognizedCommandError:
                # if an item does not expand as nested command name
                # assume that it is just an operand
                pass
            except errors.AmbiguousCommandError:
                # if an item could be expanded as nested command name, but
                # the expansion is ambiguous - reraise the exception to signal this
                # user can suppress false positives using the -- separator
                raise
            if self._command.hasCommand(command_name): break
            if shared.lookslikeopt(item):
                accepted = self._isAcceptedInChildModes(item)
                if accepted:
                    operands.pop(-1)
                    i -= 1
                    break
            operands.append(item)
            i += 1
        nested = opers[i:]
        return (operands, nested)

    def _getheuroperands(self):
        """Returns two-tuple: (operands-for-current-mode, items-for-child-mode).
        Uses simple algorithms to detect nested modes and split the operands.
        """
        n = len(self._getinput())
        operands = self._args[n:]
        breaker = ((operands[0] == '--') if operands else False)
        if breaker and operands: operands.pop(0)
        if not breaker:
            operands, nested = self._heuralgo(operands)
        else:
            nested = []
        return (operands, nested)

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
            if shared.lookslikeopt(s) and self._command.accepts(s): i += len(self._command.getopt(s).params())
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
            if shared.lookslikeopt(s) and self._command.accepts(s): i += len(self._command.getopt(s).params())
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
        if option:
            name = str(option)
            alias = option.alias(name)
        variant = ''
        if name in input: variant = name
        if alias and (alias in input): variant = alias
        return variant

    def _parseoptions(self, input):
        """Parse options part of input.
        """
        options = []
        i = 0
        while i < len(input):
            item = input[i]
            i += 1
            if not (shared.lookslikeopt(item) and self._command.accepts(item)): break
            n = len(self._command.params(item))
            params = (input[i:i+n] if n else None)  # if n(umber of parameters) is greater than 0, then extract parameters, else set them to None
            alias = self._command.alias(item)
            options.append( (item, params) )
            if alias and alias != item: options.append( (alias, params) )
            i += n
        return options

    def _composeoptions(self, options):
        """Compose options dictionary according to rules set by UI description, i.e.
        plural options shall be gathered, singular should be overwritten etc.
        """
        composed = {}
        for opt, args in options:
            if self._command.getopt(opt)['plural'] and self._command.getopt(opt).params():
                if opt not in composed: composed[opt] = []
                composed[opt].append(args)
            elif self._command.getopt(opt)['plural'] and not self._command.getopt(opt).params():
                if opt not in composed: composed[opt] = 0
                composed[opt] += 1
            else:
                composed[opt] = (tuple(args) if args is not None else args)
        return composed

    def _convertoptionstypes(self, options):
        """Convert options' parameters to their desired types.
        """
        converted = []
        for opt, params in options:
            for i, callback in enumerate(self._command.params(opt)):
                if type(callback) == str and ':' in callback:
                    callback = callback.split(':', 1)[1]
                if type(callback) is str: callback = self._typehandlers[callback]
                params[i] = callback(params[i])
            converted.append( (opt, params) )
        return converted

    def _checkImplicationConflicts(self, implying, present, implied, options):
        """Checks if the <implied> option conflicts with any option from <options> or
        if it is conflicted by an option already present.
        """
        # iterate over implied option's conflicts:
        # if any is found in the provided input, the option cannot be added -- raise an error
        for o in implied.conflicts():
            if o in options:
                raise errors.ConflictingOptionsError('option "{0}" implies option "{1}" which conflicts with already provided option "{2}"'.format(implying, present, o))
        # iterate over already provided options, get their conflicts:
        # if any of the already provided options says it has conflicts with the implied option, report it -- raise an error
        for o in options:
            if present in self._command.getopt(o).conflicts():
                raise errors.ConflictingOptionsError('option "{0}" implies option "{1}" which conflicts with already provided option "{2}"'.format(implying, present, o))
            implying

    def _checkImplication(self, implying, implied, options):
        """Checks if the <implied> option can be added to the input with
        the <options> dictionary already present.
        Returns list of strings which should be appended to input list.
        """
        ext = []
        if not self._command.accepts(implied): raise errors.UIDesignError('option "{0}" implies option "{1}" which is unknown to the parser'.format(implying, implied))
        # set name (present in the input list) of the option and get the object representing it
        present, implied = implied, self._command.getopt(implied)
        self._checkImplicationConflicts(implying, present, implied, options)
        if not self._ininput(implied):
            ext.append(present)
            self._implied_options.append(implied)
            if implied['arguments'] and not implied['defaults']:
                raise errors.UIDesignError('option "{0}" implies option "{1}" which requires arguments but provides no default values for them'.format(implying, present))
            if len(implied['arguments']) != len(implied['defaults']):
                reason = ('big' if len(implied['arguments']) > len(implied['defaults']) else 'small')
                raise errors.UIDesignError('option "{0}" implies option "{1}" which requires arguments but provides insufficient (too {2}) number of default values for them'.format(implying, present, reason))
            ext.extend(implied['defaults'])
        return ext

    def _addimplied(self, input, options):
        """Adds implied options to the input.
        Implications are costly as they cause whole UI to be reparsed.
        """
        new_input = input[:]
        for opt in options:
            opt = self._command.getopt(opt)
            for i in opt['implies']: new_input.extend(self._checkImplication(opt, i, options))
        return new_input

    def parse(self):
        """Parsing method for RedCLAP.
        """
        self._ui = ParsedUI(command=self._command)
        input = self._getinput()
        options = self._composeoptions(self._convertoptionstypes(self._parseoptions(input)))
        operands, nested = self._getheuroperands()
        self._parsed['options'], self._parsed['operands'] = options, operands
        self._ui._options, self._ui._operands = options, operands
        if nested:
            name = self._command.expandCommandName(nested.pop(0))
            command = self._command.getCommand(name, False)
            ui = Parser(command).feed(nested).parse().ui()
            ui._name = name
            self._ui._appendcommand(command=ui)
        new_input = self._addimplied(input, options)
        if new_input != input:
            new_args = new_input + self._getoperands(heur=False)
            self._args = new_args
            self.parse()
        return self

    def state(self):
        """Returns state of the parser's current command, i.e. current options and operands.
        Must be called **after** the `.parse()` method.
        """
        return self._parsed

    def ui(self):
        """Returns parsed UI.
        Must be called **after** the `.parse()` method.
        """
        return self._ui
