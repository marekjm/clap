"""This module holds logic responsible for turning JSON representations into usable UI descriptions, i.e.
Python objects representing modes and options.
"""

import json

from . import option
from . import mode
from . import shared
from . import errors


def makelines(s, maxlen):
    lines = []
    words = s.split(' ')
    line = ''
    for i in words:
        if len(line + i) <= maxlen-1:
            line += (i + ' ')
        else:
            lines.append(line)
            line = ''
    if line: lines.append(line)
    return lines


def _getoptionlines(mode, indent='    ', level=1):
    lines = []
    for scope in ['global', 'local']:
        if mode.options(group=scope): lines.append( ('str', indent*(level) + '{0} options:'.format(scope)) )
        for o in mode.options(group=scope):
            s = ''
            s += (o['short'] if o['short'] else '    ')
            if o['short'] and o['long']: s += ', '
            s += (o['long'] if o['long'] else '')
            if o.params():
                s += '='
                s += ' '.join(['<{0}>'.format(i) for i in o.params()])
            lines.append( ('option', indent*(level+1) + s, o) )
        if mode.options(group=scope): lines.append( ('str', '') )
    return lines


class Helper:
    def __init__(self, progname, mode):
        self._mode = mode
        self._indent = {'string': '    ', 'level': 0}
        self._usage = []
        self._progname = progname
        self._maxlen = 140
        self._opt_desc_start = 0
        self._lines = []

    def addUsage(self, line):
        self._usage.append(line)
        return self

    def gen(self):
        usage_head = 'usage: {0} '.format(self._progname)
        usage_indent = len(usage_head) * ' '
        usage_lines = []
        if self._usage: usage_lines.append( ('str', usage_head + self._usage[0]) )
        for line in self._usage[1:]: usage_lines.append( ('str', usage_indent + line) )
        self._lines.extend(usage_lines)
        if self._lines: self._lines.append( ('str', '') )

        intro_head = 'MAIN MODE of "{0}":'.format(self._progname)
        intro_lines = []
        intro_lines.append( ('str', intro_head) )
        for i in makelines(self._mode._help, 96): intro_lines.append( ('str', self._indent['string'] + i) )
        self._lines.extend(intro_lines)
        if self._mode._help: self._lines.append( ('str', '') )
        self._lines.extend(_getoptionlines(self._mode))

        if self._mode.modes(): self._lines.append( ('str', 'MODES:') )
        for m in sorted(self._mode.modes()):
            intro_head = self._indent['string'] + m
            intro_lines = []
            intro_lines.append( ('str', intro_head) )
            mode = self._mode.getmode(m)
            for i in makelines(mode._help, 92): intro_lines.append( ('str', self._indent['string']*2 + i) )
            self._lines.extend(intro_lines)
            if mode._help: self._lines.append( ('str', '') )
            self._lines.extend(_getoptionlines(mode, level=2))
        
        return self

    def render(self):
        for i in self._lines:
            if i[0] == 'option':
                if len(i[1]) > self._opt_desc_start: self._opt_desc_start = len(i[1])
        self._opt_desc_start += 2

        lines = []
        for no, i in enumerate(self._lines):
            if i[0] == 'str':
                type, string = i
            elif i[0] == 'option':
                type, string, opt = i
                while len(string) < self._opt_desc_start: string += ' '
                string += ('- {0}'.format(opt['help']) if opt['help'] else '')
            else:
                raise Exception('line {0}: unknown type: {1}: {2}'.format(no, i[0], i))
            lines.append(string)
        while lines:
            if lines[-1] == '': lines.pop(-1)
            else: break
        return '\n'.join(lines)
