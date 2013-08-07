#!/usr/bin/env python3


"""This is the module responsible for building interfaces from
files.
"""


import json

import clap


#   type recognition functions
def isoption(data):
    """Checks if given data can be treated as a representation of option.
    """
    return type(data) == dict and ('short' in data or 'long' in data)


def isparser(data):
    """Checks if given data can be treated as a representation of parser.
    """
    correct_type = type(data) == list
    correct_contents = True
    for d in data:
        if not isoption(d):
            correct_type = False
            break
    return correct_type and correct_contents


def ismodesparser(data):
    """Checks if given data can be treated as a representation of modes parser.
    """
    correct_contents = True
    for d in data:
        if not isparser(d) or not ismodesparser(d) or isoption(d):
            correct_contents = False
            break
    return type(data) == dict and correct_contents


#   building functions
#   you can use them directly to convert native Python data types
#   to interfaces
def buildparser(data, argv=[]):
    """Builds parser from list.

    :param data: data used to build UI
    :type data: list[dict]
    """
    p = clap.parser.Parser(argv=argv)
    for option in data: p.add(**option)
    return p


def buildmodesparser(data, argv=[]):
    """Builds modes parser from dict.

    :param data: data used to build UI
    :type data: dict
    """
    p = clap.modes.Parser(argv=argv)
    for mode in data:
        if mode == '__global__': continue
        element = data[mode]
        if isparser(element): element = buildparser(element)
        elif ismodesparser(element): element = buildmodesparser(element)
        else: raise Exception('invalid element: {0}'.format(element))
        p.addMode(mode, element)
    if '__global__' in data:
        if type(data['__global__']) != list: raise TypeError('"__global__" must be a list of options')
        for option in data['__global__']: p.addOption(**option)
    return p


#   builder object - use it to build from JSON
class Builder():
    """This object is used to convert JSON representations to CLAP interfaces.
    It can build simple parsers, single-level mode parsers and nested mode parsers.

    Before initialization, make sure that the ui file you are trying to use is
    present because it is loaded immediately.

    **Notice**: Builder will not format the input for you. It must be done explicitly.

        f = clap.formater(Formater(sys.argv[1:])
        f.format()
        builder = clap.builder.Builder(path='/home/user/.stuff/ui.json', argv=list(f))

    The code above is a useful snippet.
    """
    def __init__(self, path, argv=[]):
        """Initialization of a builder.

        :param path: path to JSON representing interface
        :type path: str
        :param argv: formated input list
        :type argv: list
        """
        self.path = path
        self.argv = argv
        self.data = None
        self.interface = None
        self.types = {'str': str, 'int': int, 'float': float}
        self._load()

    def _load(self):
        """Loads JSON from given path.
        """
        ifstream = open(self.path)
        data = json.loads(ifstream.read())
        ifstream.close()
        self.data = data

    def _applyhandlers(self):
        """Replaces type names in JSON with their callback functions.
        """
        for p in self.data: self.data[p] = self._applyhandlersto(self.data[p])

    def _applyhandlersto(self, parser):
        """Replaces type names in given parser-list with their callback functions.

        :param parser: list of options
        :type parsre: list[dict]
        """
        for i, option in enumerate(parser):
            if 'arguments' in option:
                for n, name in enumerate(option['arguments']): option['arguments'][n] = self.types[name]
                parser[i] = option
        return parser

    def addTypeHandler(self, name, callback):
        """Adds callback function to specific type identifier.
        """
        self.types[name] = callback

    def build(self):
        """Builds the interface.
        """
        if isparser(self.data):
            self.interface = buildparser(self._applyhandlersto(self.data), argv=self.argv)
        elif ismodesparser(self.data):
            self._applyhandlers()
            self.interface = buildmodesparser(data=self.data, argv=self.argv)

    def get(self):
        """Returns built interface.
        """
        return self.interface
