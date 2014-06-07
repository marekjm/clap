#!/usr/bin/env python3

"""This suite tests the builder that takes JSON representations of UIs and
translates them to Python-objects representations.
"""

import shutil
import unittest
import warnings

import redclap as clap


# enable debugging output which is basically huge number of print() calls
DEBUG = True


class RedBuilderTests(unittest.TestCase):
    def testBuildingFlatModeEmpty(self):
        mode = clap.mode.RedMode()
        model = {}
        self.assertEqual(mode, clap.builder.Builder().set(model).build().get())

    def testBuildingFlatModeWithSingleLocalOption(self):
        mode = clap.mode.RedMode().addLocalOption(clap.option.Option(short='f', long='foo'))
        model = {'options': {'local': [{'short': 'f', 'long': 'foo'}]}}
        self.assertEqual(mode, clap.builder.Builder().set(model).build().get())

    def testBuildingFlatModeWithSingleGlobalOption(self):
        mode = clap.mode.RedMode().addGlobalOption(clap.option.Option(short='f', long='foo'))
        model = {'options': {'global': [{'short': 'f', 'long': 'foo'}]}}
        self.assertEqual(mode, clap.builder.Builder().set(model).build().get())

    def testBuildingFlatModeWithSingleGlobalAndLocalOption(self):
        mode = clap.mode.RedMode()
        mode.addLocalOption(clap.option.Option(short='l', long='local'))
        mode.addGlobalOption(clap.option.Option(short='g', long='global'))
        model = {'options': {'local': [{'short': 'l', 'long': 'local'}], 'global': [{'short': 'g', 'long': 'global'}]}}
        self.assertEqual(mode, clap.builder.Builder().set(model).build().get())

    def testBuildingFlatModeWithSetFixedOperandsRange(self):
        mode = clap.mode.RedMode().setOperandsRange(no=[2, 2])
        model = {'operands': {'no': [2, 2]}}
        self.assertEqual(mode, clap.builder.Builder().set(model).build().get())

    def testBuildingFlatModeWithSetFluidOperandsRangeAtMost(self):
        mode = clap.mode.RedMode().setOperandsRange(no=[0, 4])
        models = [
                {'operands': {'no': [0, 4]}},
                {'operands': {'no': [None, 4]}},
                {'operands': {'no': [-4]}}
                ]
        for model in models:
            self.assertEqual(mode, clap.builder.Builder().set(model).build().get())

    def testBuildingFlatModeWithSetFluidOperandsRangeAtLeast(self):
        mode = clap.mode.RedMode().setOperandsRange(no=[4, None])
        models = [
                {'operands': {'no': [4]}},
                {'operands': {'no': [4, None]}}
                ]
        for model in models:
            self.assertEqual(mode, clap.builder.Builder().set(model).build().get())

    def testBuildingNestedModeEmpty(self):
        mode = clap.mode.RedMode().addMode(name='child', mode=clap.mode.RedMode())
        model = {'modes': {'child': {}}}
        self.assertEqual(mode, clap.builder.Builder().set(model).build().get())

    def testBuildingNestedModeWithSingleGlobalOption(self):
        mode = clap.mode.RedMode()
        mode.addGlobalOption(clap.option.Option(short='g', long='global'))
        mode.addMode(name='child', mode=clap.mode.RedMode().addMode(name='infant', mode=clap.mode.RedMode()))
        mode.propagate()
        model = {'modes': {'child': {'modes': {'infant': {}}}}, 'options': {'global': [{'short': 'g', 'long': 'global'}]}}
        self.assertEqual(mode, clap.builder.Builder().set(model).build().get())


if __name__ == '__main__':
    unittest.main()
