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

    def addTypeHandler(self, name, callback):
        """Adds callback function to specific type identifier.
        """
        self.types[name] = callback

    def get(self):
        """Returns built interface.
        """
        return self.interface


class Parser(Builder):
    def build(self):
        """Applies type handlers to options and
        converts loaded JSON to actual interface.
        """
        self.interface = clap.parser.Parser(argv=self.argv)
        self._applyhandlers()
        for option in self.data: self.interface.add(**option)
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
            p = clap.parser.Parser()
            for option in self.data[mode]: p.add(**option)
            self.interface.addMode(mode, p)
        if '__global__' in self.data:
            for option in self.data['__global__']: self.interface.addOption(**option)
        return self.interface
