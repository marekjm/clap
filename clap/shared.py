#!/usr/bin/env python3

"""This file contains functions and constants shared between various RedCLAP modules.
"""


import re


longopt_base = '--[a-zA-Z]+[a-zA-Z0-9]+([-_][a-zA-Z0-9]+)*'

regex_opt_short = re.compile('^-[a-zA-Z0-9]$')
regex_opt_long  = re.compile('^' + longopt_base + '$')

regex_longopt_with_equal_sign = re.compile('^' + longopt_base + '=.*$')
regex_connected_shorts = re.compile('^-[a-zA-Z0-9][a-zA-Z0-9]+$')

regex_mode = re.compile('^[A-Za-z]+(-?[A-Za-z]+)*$')


def lookslikeopt(s):
    """Returns True if given string looks like option.
    """
    return (regex_opt_short.match(s) or regex_opt_long.match(s) or regex_longopt_with_equal_sign.match(s) or regex_connected_shorts.match(s) ) is not None

def lookslikemode(s):
    """Returns true if given string looks like mode string.
    """
    return regex_mode.match(s) is not None
