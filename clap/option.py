#!/usr/bin/env python3

"""This module contains Option() object.
"""


class Option():
    """Object representing an option.
    """
    meta = {'short': '',
            'long': '',
            'type': None,
            'required': False,
            'conflicts': [],
            'hint': '',
            }

    def __init__(self, short='', long='', type=None, required=False, conflicts=[], hint=''):
        if not (short or long): raise TypeError('neither short nor long variant was specified')
        if short: short = '-' + short
        if long: long = '--' + long
        meta = {'short': short,
                'long': long,
                'type': type,
                'required': required,
                'conflicts': conflicts,
                'hint': hint,
                }
        self.meta = meta

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
        if self.meta['short']: string = short
        if self.meta['long']: string = long
        return string

    def __repr__(self):
        return str(self)

    def match(self, s):
        """Returns True if given string matches one of option names.
        """
        return s == self['short'] or s == self['long']

    def type(self):
        """Returns type of argument for this option.
        None indicates no argument.
        """
        return self['type']
