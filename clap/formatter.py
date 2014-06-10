#!/usr/bin/env python3


"""This module contains formatter object which is used to
properly format input arguments for parser.

For information what strings RedCLAP considers *options strings* read the source of
`clap/base.py` which contains regular expressions used for option strings
recognition.
"""


import re


from . import shared


class Formatter():
    """This object is used to format the input list in order for use
    with Parser().
    """
    def __init__(self, argv):
        self._argv = argv[:]
        self._formatted = argv[:]

    def __iter__(self):
        return iter(self._formatted)

    def __list__(self):
        return self._formatted

    def _splitshorts(self):
        """This will split short options.
        Example:
            -lhR  ->  -l -h -R
        """
        argv = []
        i = 0
        while i < len(self._formatted):
            if self._formatted[i] == '--':
                current = self._formatted[i:]
                i = len(self._formatted)
            elif shared.regex_connected_shorts.match(self._formatted[i]):
                current = ['-{}'.format(n) for n in list(self._formatted[i])[1:]]
            else:
                current = [self._formatted[i]]
            argv.extend(current)
            i += 1
        self._formatted = argv

    def _splitequal(self):
        """This will split long options passed with arguments connected
        with equal sign.
        --verbose=True  ->  --verbose True
        """
        argv = []
        i = 0
        while i < len(self._formatted):
            if self._formatted[i] == '--':
                current = self._formatted[i:]
                i = len(self._formatted)
            elif shared.regex_longopt_with_equal_sign.match(self._formatted[i]):
                current = self._formatted[i].split('=', 1)
            else:
                current = [self._formatted[i]]
            argv.extend(current)
            i += 1
        self._formatted = argv

    def format(self):
        """This will format the input list.
        """
        self._splitshorts()
        self._splitequal()
        return self

    def reset(self):
        """Resets `formatted` back to `argv`.
        """
        self._formatted = self._argv[:]
