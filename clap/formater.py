#!/usr/bin/env python3


"""This module contains Formatter() object which is used to
properly format input arguments for Parser().

For information what strings CLAP considers *options strings* read the source of
`clap/base.py` which contains regular expressions used for option strings
recognition.
"""


import re


from clap import shared


class Formater():
    """This object is used to format the input list in order for use
    with Parser().
    """
    def __init__(self, argv):
        self.argv = argv
        self.formated = argv

    def __iter__(self):
        return iter(self.formated)

    def __list__(self):
        return self.formated

    def _splitshorts(self):
        """This will split short options. Example:
        -lhR  ->  -l -h -R
        """
        argv = []
        i = 0
        while i < len(self.formated):
            if self.formated[i] == '--':
                current = self.formated[i:]
                i = len(self.formated)
            elif re.match(shared.connected_shorts_regexp, self.formated[i]):
                current = ['-{}'.format(n) for n in list(self.formated[i])[1:]]
            else:
                current = [self.formated[i]]
            argv.extend(current)
            i += 1
        self.formated = argv

    def _splitequal(self):
        """This will split long options passed with arguments connected
        with equal sign.
        --verbose=True  ->  --verbose True
        """
        argv = []
        i = 0
        while i < len(self.formated):
            if self.formated[i] == '--':
                current = self.formated[i:]
                i = len(self.formated)
            elif re.match(shared.longopt_with_equal_sign_regexp, self.formated[i]):
                current = self.formated[i].split('=', 1)
            else:
                current = [self.formated[i]]
            argv.extend(current)
            i += 1
        self.formated = argv

    def format(self):
        """This will format the input list.
        """
        self._splitshorts()
        self._splitequal()

    def reset(self):
        """Resets `formatted` back to `argv`.
        """
        self.formated = [i for i in self.argv]
