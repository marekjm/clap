#!/usr/bin/env python3

"""Generates usage information and
help data from parsers.
"""


class Helper():
    """Helper object holds logic used to build usage and
    help information.
    """
    def __init__(self, parser):
        self.parser = parser

    def help(self, indent='  ', ignore=[]):
        """Generates help information.

        :param ignore: ignore these options when creating help strings
        :returns: list of strings
        """
        info = []
        final = []
        try:
            for o in self.parser.options:
                if o in ignore:
                    info.append('')
                    continue
                line = ''
                if o['short']:
                    line = indent + o['short']
                if o['long']:
                    if line: line += ', '
                    else: line = indent + '    '
                    line += o['long']
                if o['arguments']:
                    line += '='
                    line += ' '.join(['<{}>'.format(i.__name__) for i in o['arguments']])
                info.append(line)

            longest = 0
            for i in info:
                if len(i) > longest: longest = len(i)

            for i, line in enumerate(info):
                while len(line) < longest + 4: line += ' '
                o = self.parser.options[i]
                if o in ignore: continue
                if o['help']:
                    line = line + '- {0}'.format(o['help'])
                final.append(line)
                if o['required']:
                    final.append('{0}    is required (!)'.format(indent))
                if o['conflicts']:
                    final.append('{0}    conflicts with (-): '.format(indent) + ', '.join(o['conflicts']))
                if o['requires']:
                    final.append('{0}    requires (+): '.format(indent) + ', '.join(o['requires']))
                if o['wants']:
                    final.append('{0}    wants (?): '.format(indent) + ', '.join(o['wants']))
                final.append('')
        except AttributeError:
            final.append('GLOBAL:\n')
            final.extend(Helper(self.parser.modes['']).help(indent=indent+'  '))
            final.append('\nMODES:\n')
            for m in self.parser.modes:
                if m == '': continue
                final.append('{0}{1}:'.format(indent, m))
                final.extend(Helper(self.parser.modes[m]).help(indent=indent+'  ', ignore=self.parser.modes[''].options))
        finally:
            return final
