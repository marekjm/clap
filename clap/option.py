#!/usr/bin/env python3

"""This module contains Option() object.
"""


class Option():
    """Object representing an option.

    CLAP aims at being one of the most advanced libraries for parsing command line options for
    Python 3 language. To achieve this, each option has plenty of parameters which allows great
    customization of the behaviour of interfaces created with CLAP.

    Having lenghty list of parameters has its downsides of which one is that their functions are
    hard to remember. So, here is the explanation of what they do:

    short:
        This is short name for the option

    long:
        This is long name for the option

    argument:
        You can pass one of these: str, int or float. If you do so, CLAP will expect an argument of given
        type to be passed alongside the option.
        CLAP will raise an exception when:
        * option is given no argument,
        * option is given argument of invalid type (argument is converted from string during parsing).
        In fact, `argument` should just be a one-parameter callback taking string.

    requires:
        List of options that MUST be passed with this option. An excpetion is raised when EVEN ONE OF THEM
        is NOT found in `argv`.

    needs:
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

    hint:
        It's self-explanatory, isn't it? Text explaining usage of the option.
        **Warning:** may be deprecated in near future!
    """
    def __init__(self, short='', long='', argument=None, requires=[], needs=[], required=False, not_with=[], conflicts=[], hint=''):
        if not (short or long): raise TypeError('neither short nor long variant was specified')
        if short: short = '-' + short
        if long: long = '--' + long
        self.meta = {   'short': short,
                        'long': long,
                        'argument': argument,
                        'required': required,
                        'requires': requires,
                        'needs': needs,
                        'not_with': not_with,
                        'conflicts': conflicts,
                        'hint': hint,
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
        if self.meta['short']: string = self.meta['short']
        if self.meta['long']: string = self.meta['long']
        return string

    def match(self, s):
        """Returns True if given string matches one of option names.
        """
        return s == self['short'] or s == self['long']

    def type(self):
        """Returns type of argument for this option.
        None indicates no argument.
        """
        t = self['argument']
        return t
