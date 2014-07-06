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


def readfile(path):
    """Reads file and returns its contents as string.
    """
    ifstream = open(path)
    content = ifstream.read()
    ifstream.close()
    return content

def readjson(path):
    """Reads JSON file and returns decoded object.
    """
    return json.loads(readfile(path))


def export(mode):
    """Exports UI built in Python to a dict that can be JSON encoded.
    """
    model = {}
    if mode._options['local'] or mode._options['global']: model['options'] = {}
    for scope in ['local', 'global']:
        if mode._options[scope]:
            model['options'][scope] = []
            for opt in mode._options[scope]: model['options'][scope].append(opt._export())
    if mode.getOperandsRange() != (None, None):
        model['operands'] = {}
        model['operands']['no'] = list(mode.getOperandsRange())
    if mode.modes():
        model['commands'] = {}
        for name, submode in mode._modes.items():
            model['commands'][name] = export(submode)
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
        self._mode = None

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
        ui = mode.RedMode()
        if 'doc' in self._model: ui.setdoc(**self._model['doc'])
        if 'options' in self._model:
            if 'local' in self._model['options']:
                for opt in self._model['options']['local']: ui.addLocalOption(option.Option(**opt))
            if 'global' in self._model['options']:
                for opt in self._model['options']['global']: ui.addGlobalOption(option.Option(**opt))
        if 'operands' in self._model:
            if 'no' in self._model['operands']: ui.setOperandsRange(no=self._model['operands']['no'])
        commands = (self._model['commands'] if 'commands' in self._model else {})
        for name, nmodel in commands.items(): ui.addMode(name=name, mode=Builder().set(nmodel).build().get())
        ui.propagate()
        self._mode = ui
        return self

    def get(self):
        """Returns built mode.
        """
        return self._mode
