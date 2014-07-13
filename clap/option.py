#!/usr/bin/env python3

"""This module contains implementation of the option representation.
"""


class Option:
    """Object representing an option.

    CLAP aims at being one of the most advanced libraries for parsing command line options for
    Python 3 language. To achieve this, each option has plenty of parameters which allows great
    customization of the behaviour of interfaces created with CLAP.
    """
    def __init__(self, short='', long='', arguments=[], defaults=[], requires=[], wants=[], implies=[], required=False, not_with=[], plural=False, conflicts=[], help=''):
        """Initialization method for Option object has plenty of arguments.
        The list being so long, it is pretty hard to remember what each of its paramters does.
        Here are provided short explanations of their functions and intended usage.

        short:
            This is short name for the option. Given WITHOUT preceding hyphen.

        long:
            This is long name for the option. MUST BE two or more characters. Given WITHOUT preceding hyphens.

        arguments:
            You can pass list containing these types: str, int or float. If you do so, CLAP will expect an argument of given
            type to be passed alongside the option. You can safely violate the rule about types as long as you pass
            one-argument callables to `argument`.
            CLAP will raise an exception when:
            * option is given no argument,
            * option is given argument of invalid type (argument is converted from string during parsing).

        defaults:
            A list of default values for arguments of this option.
            All items must be strings.
            This values are used when option is added by another option (i.e. is implied by another option) and
            was not passed by the user directly.
            They cannot, however be used to omit their arguments on command line.

        requires:
            List of options that MUST be passed with this option. An excpetion is raised when EVEN ONE OF THEM
            is NOT found in `argv`.

        wants:
            Slightly different from `requires`.
            It's list of options which MAY be passed with this option. An exception is raised when NONE OF THEM
            is found in `argv`.

        implies:
            List of options this option implies are used.
            If they are not present, they are appended to the list of options.
            For options that require arguments, default values are used.

            It is recommended to not overuse this feature; it is loop-safe,
            well documented and should work as intended but debugging problems caused
            by multiple implications can be challenging.

        required:
            Boolean. If `True` an exception is raised if option is not found in `argv`.

        not_with:
            List of options the option is not required with. If EVEN ONE OF THEM is found an evception is not
            raised even if the option itself is not found.

        conflicts:
            List of options this option CANNOT BE passed with. If EVEN ONE OF THEM is found in `argv` an exception
            is raised.

        plural:
            Option may be passed multiple times and each use should be accumulated.

        help:
            Description of the option. General help. You name it.
        """
        if not (short or long):
            raise TypeError('neither short nor long variant was specified')
        if len(long) < 2 and long:
            raise TypeError('long option name must be two or more characters, given: {0}'.format(long))
        if short: short = '-' + short
        if long: long = '--' + long
        self._meta = {'short': short,
                      'long': long,
                      'arguments': arguments,
                      'defaults': defaults,
                      'required': required,
                      'requires': requires,
                      'wants': wants,
                      'implies': implies,
                      'not_with': not_with,
                      'plural': plural,
                      'conflicts': conflicts,
                      'help': help,
                      }

    def __getitem__(self, key):
        return self._meta[key]

    def __iter__(self):
        return iter(self._meta)

    def __list__(self):
        return [(key, self.meta[key]) for key in self.meta]

    def __str__(self):
        string = ''
        if self['long']: string = self['long']
        if self['short'] and not string: string = self['short']
        return string

    def __eq__(self, option):
        result = True
        for key in self._meta:
            if self[key] != option[key]:
                result = False
                break
        return result

    def _export(self):
        """Exports dictionary required to build option.
        """
        default = Option(short=self['short'], long=self['long'])
        model = {}
        if self['short']: model['short'] = self['short'][1:]
        if self['long']: model['long'] = self['long'][2:]
        for k, v in self._meta.items():
            if k in ['short', 'long']: continue
            if v != default[k]: model[k] = v
        return model

    def alias(self, name):
        """Returns other name of the option (if any).
        If option has only one name returns empty string.

        :param name: name of the option
        """
        alias = ''
        if name == self['short']: alias = self['long']
        elif name == self['long']: alias = self['short']
        else: raise NameError('invalid name for this option: {0}'.format(name))
        return alias

    def _copy(self):
        """Returns copy of the option dict.
        :returns: dict
        """
        copy = {}
        for k in self._meta: copy[k] = self[k]
        return copy

    def match(self, s):
        """Returns True if given string matches one of option names.
        Options must be passed with one preceding hyphen for short and
        two hyphens for long options.
        If you pass an option without the hyphen, match will fail.
        """
        return s == self['short'] or s == self['long']

    def conflicts(self):
        """Returns list of options this option has conflicts with.
        """
        return self['conflicts']

    def params(self):
        """Returns list of types of arguments for this option.
        Empty list indocates that this option takes no argument.
        """
        t = self['arguments']
        return t

    def isplural(self):
        """Returns true if option is plural, false otherwise.
        """
        return self._meta['plural']
