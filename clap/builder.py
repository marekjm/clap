"""This module holds logic responsible for turning JSON representations into usable UI descriptions, i.e.
Python objects representing commands and options.
It also contains functionality needed to export UIs to ordinary data structures which, in turn, may be
serializes to JSON.
"""

import json
import warnings

from . import option
from . import mode
from . import shared
from . import errors


def export(command):
    """Exports UI built in Python to a model that can be JSON encoded.
    """
    model = {}
    if command._options['local'] or command._options['global']: model['options'] = {}
    for scope in ['local', 'global']:
        if command._options[scope]:
            model['options'][scope] = []
            for opt in command._options[scope]: model['options'][scope].append(opt._export())
    if command.getOperandsRange() != (None, None):
        model['operands'] = {}
        model['operands']['no'] = list(command.getOperandsRange())
    if command.commands():
        model['commands'] = {}
        for name in command.commands():
            model['commands'][name] = export(command.getCommand(name))
    return model


# model of help command that may be inserted into program's main command
# to ease using the Help Runner
HELP_COMMAND = {
            'doc': {
                'help': 'This command is used to obtain help information about various commands. It accepts any number of operands and can display help about nested commands, but finishes searching as soon as it finds option-looking string.'
            },
            'options': {
                'local': [
                    {
                        'short': 'u',
                        'long': 'usage',
                        'help': 'display usage information (discards operands)'
                    },
                    {
                        'short': 'e',
                        'long': 'examples',
                        'help': 'display example invocations (discards operands)'
                    },
                    {
                        'short': 'c',
                        'long': 'colorize',
                        'help': 'colorize output (do not use with "less" pager unless you want to see escape sequences, or you can use "less -R" too nicely display them)'
                    }
                ]
            },
            'operands': {'no': [0]}
        }


class Builder:
    """Object used to convert JSON representation of UI to
    appropriate CLAP objects.
    """
    def __init__(self, model=None):
        self._model = model
        self._command = None

    def set(self, model):
        """Set model of the UI.
        """
        self._model = model
        return self

    def insertHelpCommand(self):
        """Inser help command into program's main command.
        This provides interface usable by Help Runner.
        """
        if 'commands' not in self._model: self._model['commands'] = {}
        self._model['commands']['help'] = HELP_COMMAND
        return self

    def build(self):
        """Builds UI from loaded model.
        """
        ui = mode.RedCommand()
        if 'doc' in self._model: ui.setdoc(**self._model['doc'])
        if 'options' in self._model:
            if 'local' in self._model['options']:
                for opt in self._model['options']['local']: ui.addLocalOption(option.Option(**opt))
            if 'global' in self._model['options']:
                for opt in self._model['options']['global']: ui.addGlobalOption(option.Option(**opt))
        if 'operands' in self._model:
            if 'no' in self._model['operands']: ui.setOperandsRange(no=self._model['operands']['no'])
            if 'with' in self._model['operands']: ui.setAlternativeOperandsRange(no=self._model['operands']['with'])
        commands = (self._model['commands'] if 'commands' in self._model else {})
        for name, nmodel in commands.items(): ui.addCommand(name=name, command=Builder().set(nmodel).build().get())
        ui.propagate()
        self._command = ui
        return self

    def get(self):
        """Returns built command.
        """
        return self._command
