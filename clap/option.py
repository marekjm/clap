#!/usr/bin/env python3

"""This module contains Option() object.
"""


class Option():
    """Object representing an option.
    """
    def __init__(self, short='', long='', type=None, required=False, not_with=[], conflicts=[], hint=''):
        if not (short or long): raise TypeError('neither short nor long variant was specified')
        if short: short = '-' + short
        if long: long = '--' + long
        self.meta = {   'short': short,
                        'long': long,
                        'type': type,
                        'required': required,
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
        return self['type']
