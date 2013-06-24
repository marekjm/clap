#!/usr/bin/env python3


import re


"""This module contains Formatter() object which is used to
properly format input arguments for Parser().
"""


shortopt_regexp = re.compile('^-[a-zA-Z]$')
longopt_regexp = re.compile('^--[a-zA-Z]+[a-zA-Z0-9]*(-[a-zA-Z0-9]+)*$')
longopt_with_equal_sign_regexp = re.compile('^--[a-zA-Z]+[a-zA-Z0-9]*(-[a-zA-Z0-9]+)*=.*$')
connected_shorts_regexp = re.compile('^-[a-zA-Z][a-zA-Z]+$')


def lookslikeopt(s):
    """Returns True if given string looks like option.
    """
    return bool(re.match(longopt_regexp, s) or
                re.match(longopt_with_equal_sign_regexp, s) or
                re.match(connected_shorts_regexp, s) or
                re.match(shortopt_regexp, s)
                )


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
            elif re.match(connected_shorts_regexp, self.formated[i]):
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
            elif re.match(longopt_with_equal_sign_regexp, self.formated[i]):
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
