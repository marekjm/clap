"""Generates usage information and
help data from parsers.
"""

class Helper():
    """Helper object holds logic used to build usage and
    help information.
    """
    def __init__(self, parser):
        self.parser = parser

    def help(self, lines=False):
        """Generates help information.
        """
        info = []
        final = []
        big_indent = ''
        for o in self.parser.options:
            line = ''
            if o['short']: line = o['short']
            if o['long']:
                if line: line += ', '
                else: line = '    '
                line += o['long']
            if o['arguments']:
                line += '='
                line += ' '.join(['<{}>'.format(i.__name__) for i in o['arguments']])
            info.append(line)
        longest = 0
        for i in info:
            if len(i) > longest: longest = len(i)
        while len(big_indent) < longest + 6: big_indent += ' '

        for i, line in enumerate(info):
            while len(line) < longest + 4: line += ' '
            o = self.parser.options[i]
            if o['help']:
                line = line + '- {0}'.format(o['help'])
            final.append(line)
            if o['required']:
                final.append('{0}is required (!)'.format(big_indent))
            if o['conflicts']:
                final.append('{0}conflicts with (-): '.format(big_indent) + ', '.join(o['conflicts']))
            if o['requires']:
                final.append('{0}requires (+): '.format(big_indent) + ', '.join(o['requires']))
            if o['wants']:
                final.append('{0}wants (?): '.format(big_indent) + ', '.join(o['wants']))
            final.append('')

        if not lines: final = '\n\n'.join(final)
        return final
