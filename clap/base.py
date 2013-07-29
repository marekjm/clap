#!/usr/bin/env python3


"""Functions, routines and regular expressions shared between CLAP modules.
"""


import re


longopt_base = '--[a-zA-Z]+[a-zA-Z0-9]+(-[a-zA-Z0-9]+)*'

shortopt_regexp = re.compile('^-[a-zA-Z0-9]$')
longopt_regexp = re.compile('^' + longopt_base + '$')
longopt_with_equal_sign_regexp = re.compile('^' + longopt_base + '=.*$')
connected_shorts_regexp = re.compile('^-[a-zA-Z0-9][a-zA-Z0-9]+$')


def lookslikeopt(s):
    """Returns True if given string looks like option.
    """
    return bool(re.match(longopt_regexp, s) or
                re.match(longopt_with_equal_sign_regexp, s) or
                re.match(connected_shorts_regexp, s) or
                re.match(shortopt_regexp, s)
                )



