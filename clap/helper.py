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
    i = 0
    while i < len(words):
        word = words[i]
        if len(line + word) <= maxlen-1:
            line += (word + ' ')
            i += 1
        else:
            lines.append(line)
            line = ''
    if line: lines.append(line)
    return lines


def renderOptionHelp(option, help=True):
    """Renders a single help line for passed option.
    """
    message = ''
    message += (option['short'] if option['short'] else '    ')
    if option['short'] and option['long']: message += ', '
    message += (option['long'] if option['long'] else '')
    if option.params():
        message += ('=' if option['long'] else ' ')
        message += ' '.join(['<{0}>'.format(i) for i in option.params()])
    if help: message += (' - {0}'.format(option['help']) if option['help'] else '')
    return message

def _getoptionlines(mode, indent='    ', level=1):
    lines = []
    for scope in ['global', 'local']:
        if mode.options(group=scope): lines.append( ('str', indent*(level) + '{0} options:'.format(scope)) )
        for o in mode.options(group=scope): lines.append( ('option', indent*(level+1) + renderOptionHelp(o, False), o) )
        if mode.options(group=scope): lines.append( ('str', '') )
    return lines


def _cleanback(lines):
    while True:
        type, content = lines[-1]
        if type != 'str': break
        if content.strip() == '': lines.pop(-1)
        else: break
    return lines


class Helper:
    def __init__(self, progname, mode):
        self._mode = mode
        self._indent = {'string': '   ', 'level': 0}
        self._progname = progname
        self._maxlen = 140
        self._opt_desc_start = 0
        self._lines = []

    def addUsage(self, line):
        self._usage.append(line)
        return self

    def setmaxlen(self, n):
        self._maxlen = n
        return self

    def _genexamples(self):
        lines = []
        examples = (self._mode._doc['examples'] if 'examples' in self._mode._doc else [])
        if examples: lines.append( ('str', 'Examples:') )
        for i, example in enumerate(examples):
            if 'line' not in example: continue
            lines.append( ('str', '{0}{1} {2}'.format(self._indent['string'], self._progname, example['line'])) )
            if 'desc' in example and example['desc']:
                lines.append( ('str', '{0}{0}{1}'.format(self._indent['string'], example['desc'])) )
                if i < len(examples)-1: lines.append( ('str', '') )
        if lines: self._lines.extend(lines)
        if self._lines and lines: self._lines.append( ('str', '') )

    def _gendoc(self):
        for key in ['usage']:
            head = '{0}: {1} '.format(key, self._progname)
            indent = len(head) * ' '
            lines = []
            what = (self._mode._doc[key] if key in self._mode._doc else [])
            if what: lines.append( ('str', head + what[0]) )
            for line in what[1:]: lines.append( ('str', indent + line) )
            self._lines.extend(lines)
            if self._lines: self._lines.append( ('str', '') )

    def _genintrolines2(self, mode, name, level=0, longest=0):
        if not longest: longest = len(name)
        SPACING = (2 if longest else 0)  # CONF?
        lines = []
        text = '{0}{1}'.format(name.ljust(longest+SPACING), mode._doc['help'].strip())
        first = makelines(text, self._maxlen)[0]
        lines.append( ('str', ((self._indent['string']*level) + first)) )
        for l in makelines(text[len(first):], (self._maxlen-len(name)-3)):
            indent = self._indent['string']*level
            padding = ' ' * (len(name) + SPACING)
            l = '{0}{1}{2}'.format(indent, padding, l)
            lines.append( ('str', l) )
        lines = _cleanback(lines)
        if text: lines.append( ('str', '') )
        return lines

    def _gencommandslines(self, mode, name, level, deep):
        lines = []
        modes = sorted(mode.modes())
        longest = 0
        for m in modes:
            if len(m) > longest: longest = len(m)
        for m in modes:
            submode = mode.getmode(m)
            if deep:
                lines.extend(self._genmodelines(submode, name=m, level=level+2))
                lines.append( ('str', '') )
            else:
                lines.extend(self._genintrolines2(submode, name=m, level=level+2, longest=longest))
        return lines

    def _genmodelines(self, mode, level=0, name='', deep=True):
        lines = []
        self._lines.extend(self._genintrolines2(mode, name, level=level))
        self._lines.extend(_getoptionlines(mode, indent=self._indent['string'], level=level+1))
        if mode.modes(): self._lines.append( ('str', ((self._indent['string']*(level+1)) + 'commands:')) )
        self._lines.extend(self._gencommandslines(mode, name, level, deep))
        return lines

    def gen(self, deep=True):
        self._gendoc()
        self._genexamples()
        self._lines.extend(self._genmodelines(mode=self._mode, deep=deep))
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


class HelpRunner:
    """Class used to run help screen logic, basing on the contents of parsed UI passed to it.
    """
    def __init__(self, ui, program):
        """Parameters:

        - ui:       parsed UI,
        - program:  program name (as string),
        """
        self._ui = ui
        self._program_name = program
        self._displayed = False
        self._options, self._commands = ['-h', '--help'], ['help']
        self._ignorecmds = ['']

    def _byoptions(self):
        """Display help if options tell you to do so.
        """
        cui, ui = self._ui, self._ui
        while True and str(ui.down()) != 'help':
            present = False
            for i in self._options:
                if i in ui:
                    present = True
                    break
            if present:
                helper = Helper(filename, cui._mode).setmaxlen(n=70)
                print(helper.gen(deep=('--verbose' in cui)).render())
                if '--verbose' not in cui: print('\nRun "{0} --help --verbose" to see full help message'.format(filename))
                self._displayed = True
            if cui.islast(): break
            cui = cui.down()

    def _byhelpcommand(self):
        """Display help message when 'help' command is encountered.
        """
        ui = (self._ui if str(self._ui) else self._ui.down())
        if str(ui) != 'help': return
        items = ui.operands()
        if not items:
            helper = Helper(self._program_name, ui.up()._mode).setmaxlen(n=70)
            print(helper.gen(deep=('--verbose' in ui or '--help' in ui)).render())
            if '--verbose' not in ui and '--help' not in ui: print('\nRun "{0} help --verbose" or "{0} help --help" to see full help message'.format(self._program_name))
            self._displayed = True
        if self._displayed: return
        mode, done = ui.top()._mode, False
        for i, item in enumerate(items):
            if shared.lookslikeopt(item):
                message = (renderOptionHelp(mode.getopt(item)).strip() if mode.accepts(item) else 'unrecognised option: no help available')
                print('(option) {0}'.format(message))
                self._displayed = True
                break
            elif not mode.hasmode(item):
                message = 'unrecognised mode: no help available'
                print('{0}'.format(message))
                self._displayed = True
                break
            elif i < len(items):
                mode = mode.getmode(item)
        if not self._displayed:
            helper = Helper(self._program_name, mode).setmaxlen(n=70)
            print(helper.gen(deep=('--verbose' in ui or '--help' in ui)).render())
            if '--verbose' not in ui and '--help' not in ui: print('\nRun "{0} help --verbose -- [opers...]" or "{0} help --help -- [opers...]" to see full help message'.format(self._program_name))
            self._displayed = True

    def adjust(self, options=None, commands=None, ignorecmds=None):
        """Adjusting help runner to match current program specifics.
        'options' is a list of options (as full names, e.g. '-h' and '--help') that shall trigger help screen display,
        'commands' is a list of commands (their names) that shall trigger help screen display,
        'ignorecmds' is a list of commands that can be trimmed from the to of given UI (in order in which they appear in this list),
        """
        if options is not None: self._options = options
        if commands is not None: self._commands = commands
        if ignorecmds is not None: self._ignorecmds = ignorecmds
        return self

    def run(self):
        """Runs whole logic.
        """
        self._byoptions()
        if not self._displayed: self._byhelpcommand()
        return self

    def displayed(self):
        """Returns true if any help was displayed.
        Usually, this means that no further work shall be done by the program so
        this is convinience method.
        """
        return self._displayed
