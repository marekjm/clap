#!/usr/bin/env python3


"""This is the module responsible for building interfaces from
files.
"""


import json
import os

import clap

class Builder():
    """This object responsible for building interfaces.
    """
    def __init__(self, path, argv=[]):
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
        for i, option in enumerate(self.data):
            if 'arguments' in option:
                for n, name in enumerate(option['arguments']): option['arguments'][n] = self.types[name]
                self.data[i] = option

    def _applyhandlersto(self, parser):
        """Replaces type names in given parser-list with their callback functions.
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
        if isparser(self.data): self.interface = buildparser(self._applyhandlersto(self.data), argv=self.argv)

    def get(self):
        """Returns built interface.
        """
        return self.interface


class ModesParser(Builder):
    def _applyhandlers(self):
        """Replaces type names in JSON with their callback functions.
        """
        for p in self.data:
            parser = self.data[p]
            for i, option in enumerate(parser):
                if 'arguments' in option:
                    for n, name in enumerate(option['arguments']): option['arguments'][n] = self.types[name]
                parser[i] = option
            self.data[p] = parser

    def build(self):
        """Applies type handlers to options and
        converts loaded JSON to actual interface.
        """
        self.interface = clap.modes.Parser(argv=self.argv)
        self._applyhandlers()
        for mode in self.data:
            if mode == '__global__': continue
            self.interface.addMode(mode, buildparser(self.data[mode]))
        if '__global__' in self.data:
            for option in self.data['__global__']: self.interface.addOption(**option)


def buildparser(data, argv=[]):
    """Builds parser from dict.
    :param data: data used to build UI
    :type data: dict
    """
    p = clap.parser.Parser(argv=argv)
    for option in data: p.add(**option)
    return p


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
        if not isparser(d) or not ismodesparser(d):
            correct_contents = False
            break
    return type(data) == dict and ('short' not in data and 'long' not in data)
