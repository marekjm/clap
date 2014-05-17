#!/usr/bin/env python3

"""This module contains implementation of the option representation.
"""


class Option():
    """Object representing an option.

    CLAP aims at being one of the most advanced libraries for parsing command line options for
    Python 3 language. To achieve this, each option has plenty of parameters which allows great
    customization of the behaviour of interfaces created with CLAP.

    Having lenghty list of parameters has its downsides of which one is that their functions are
    hard to remember. So, here is the explanation of what they do:

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

    requires:
        List of options that MUST be passed with this option. An excpetion is raised when EVEN ONE OF THEM
        is NOT found in `argv`.

    wants:
        Slightly different from `requires`.
        It's list of options which MAY be passed with this option. An exception is raised when NONE OF THEM
        is found in `argv`.

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
    def __init__(self, short='', long='', arguments=[], requires=[], wants=[], required=False, not_with=[], plural=False, conflicts=[], help=''):
        if not (short or long):
            raise TypeError('neither short nor long variant was specified')
        if len(long) < 2 and long:
            raise TypeError('long option name must be two or more characters, given: {0}'.format(long))
        if short: short = '-' + short
        if long: long = '--' + long
        self._meta = {'short': short,
                      'long': long,
                      'arguments': arguments,
                      'required': required,
                      'requires': requires,
                      'wants': wants,
                      'not_with': not_with,
                      'plural': plural,
                      'conflicts': conflicts,
                      'help': help,
                      }

    def __getitem__(self, key):
        return self.meta[key]

    def __iter__(self):
        return iter(self.meta)

    def __dict__(self):
        return self.meta

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

    def _alias(self, name):
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

    def type(self):
        """Returns list of types of arguments for this option.
        Empty list indocates that this option takes no argument.
        """
        t = self['arguments']
        return t
