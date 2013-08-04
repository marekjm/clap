#!/usr/bin/env python3


"""This is the module responsible for building interfaces from
files.
"""


import json
import os

from clap import parser, modes


class Builder():
    """This object responsible for building interfaces.
    """
    def __init__(self, path, name=''):
        self.path = path
        self.name = name
        self.data = None
        self.interface = None

    def load(self):
        """Loads JSON from given path.
        """
        ifstream = open(self.path)
        data = json.decode(ifstream.read())
        ifstream.close()
        self.data = data


class Parser(Builder):
    def build(self):
        ui = parser.Parser()
        for option in self.data:
            ui.add(**option)
        return ui
