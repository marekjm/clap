#!/usr/bin/env python3

"""This suite tests the builder that takes JSON representations of UIs and
translates them to Python-objects representations.
"""

import shutil
import unittest
import warnings

import clap


# enable debugging output which is basically huge number of print() calls
DEBUG = True


class RedBuilderTests(unittest.TestCase):
    def testBuildingFlatCommandEmpty(self):
        mode = clap.mode.RedCommand()
        model = {}
        self.assertEqual(mode, clap.builder.Builder().set(model).build().get())

    def testBuildingFlatCommandWithSingleLocalOption(self):
        mode = clap.mode.RedCommand().addLocalOption(clap.option.Option(short='f', long='foo'))
        model = {'options': {'local': [{'short': 'f', 'long': 'foo'}]}}
        self.assertEqual(mode, clap.builder.Builder().set(model).build().get())

    def testBuildingFlatCommandWithSingleGlobalOption(self):
        mode = clap.mode.RedCommand().addGlobalOption(clap.option.Option(short='f', long='foo'))
        model = {'options': {'global': [{'short': 'f', 'long': 'foo'}]}}
        self.assertEqual(mode, clap.builder.Builder().set(model).build().get())

    def testBuildingFlatCommandWithSingleGlobalAndLocalOption(self):
        mode = clap.mode.RedCommand()
        mode.addLocalOption(clap.option.Option(short='l', long='local'))
        mode.addGlobalOption(clap.option.Option(short='g', long='global'))
        model = {'options': {'local': [{'short': 'l', 'long': 'local'}], 'global': [{'short': 'g', 'long': 'global'}]}}
        self.assertEqual(mode, clap.builder.Builder().set(model).build().get())

    def testBuildingFlatCommandWithSetFixedOperandsRange(self):
        mode = clap.mode.RedCommand().setOperandsRange(no=[2, 2])
        model = {'operands': {'no': [2, 2]}}
        self.assertEqual(mode, clap.builder.Builder().set(model).build().get())

    def testBuildingFlatCommandWithSetFluidOperandsRangeAtMost(self):
        mode = clap.mode.RedCommand().setOperandsRange(no=[0, 4])
        models = [
                {'operands': {'no': [0, 4]}},
                {'operands': {'no': [None, 4]}},
                {'operands': {'no': [-4]}}
                ]
        for model in models:
            self.assertEqual(mode, clap.builder.Builder().set(model).build().get())

    def testBuildingFlatCommandWithSetFluidOperandsRangeAtLeast(self):
        mode = clap.mode.RedCommand().setOperandsRange(no=[4, None])
        models = [
                {'operands': {'no': [4]}},
                {'operands': {'no': [4, None]}}
                ]
        for model in models:
            self.assertEqual(mode, clap.builder.Builder().set(model).build().get())

    def testBuildingNestedCommandEmpty(self):
        mode = clap.mode.RedCommand().addCommand(name='child', command=clap.mode.RedCommand())
        model = {'commands': {'child': {}}}
        self.assertEqual(mode, clap.builder.Builder().set(model).build().get())

    def testBuildingNestedCommandWithSingleGlobalOption(self):
        mode = clap.mode.RedCommand()
        mode.addGlobalOption(clap.option.Option(short='g', long='global'))
        mode.addCommand(name='child', command=clap.mode.RedCommand().addCommand(name='infant', command=clap.mode.RedCommand()))
        mode.propagate()
        model = {'commands': {'child': {'commands': {'infant': {}}}}, 'options': {'global': [{'short': 'g', 'long': 'global'}]}}
        self.assertEqual(mode, clap.builder.Builder().set(model).build().get())


class RedCommandExportingTests(unittest.TestCase):
    def testExportingFlatCommandEmpty(self):
        mode = clap.mode.RedCommand()
        model = {}
        self.assertEqual(model, clap.builder.export(mode))
        self.assertEqual(model, clap.builder.export(clap.builder.Builder().set(model).build().get()))

    def testExportingFlatCommandWithSingleLocalOption(self):
        mode = clap.mode.RedCommand().addLocalOption(clap.option.Option(short='f', long='foo'))
        model = {'options': {'local': [{'short': 'f', 'long': 'foo'}]}}
        self.assertEqual(model, clap.builder.export(mode))
        self.assertEqual(model, clap.builder.export(clap.builder.Builder().set(model).build().get()))

    def testExportingFlatCommandWithSingleGlobalOption(self):
        mode = clap.mode.RedCommand().addGlobalOption(clap.option.Option(short='f', long='foo'))
        model = {'options': {'global': [{'short': 'f', 'long': 'foo'}]}}
        self.assertEqual(model, clap.builder.export(mode))
        self.assertEqual(model, clap.builder.export(clap.builder.Builder().set(model).build().get()))

    def testExportingFlatCommandWithSingleGlobalAndLocalOption(self):
        mode = clap.mode.RedCommand()
        mode.addLocalOption(clap.option.Option(short='l', long='local'))
        mode.addGlobalOption(clap.option.Option(short='g', long='global'))
        model = {'options': {'local': [{'short': 'l', 'long': 'local'}], 'global': [{'short': 'g', 'long': 'global'}]}}
        self.assertEqual(model, clap.builder.export(mode))
        self.assertEqual(model, clap.builder.export(clap.builder.Builder().set(model).build().get()))

    def testExportingFlatCommandWithSetFixedOperandsRange(self):
        mode = clap.mode.RedCommand().setOperandsRange(no=[2, 2])
        model = {'operands': {'no': [2, 2]}}
        self.assertEqual(model, clap.builder.export(mode))
        self.assertEqual(model, clap.builder.export(clap.builder.Builder().set(model).build().get()))

    def testExportingFlatCommandWithSetFluidOperandsRangeAtMost(self):
        mode = clap.mode.RedCommand().setOperandsRange(no=[0, 4])
        model = {'operands': {'no': [0, 4]}}
        self.assertEqual(model, clap.builder.export(mode))
        self.assertEqual(model, clap.builder.export(clap.builder.Builder().set(model).build().get()))

    def testExportingFlatCommandWithSetFluidOperandsRangeAtLeast(self):
        mode = clap.mode.RedCommand().setOperandsRange(no=[4, None])
        model = {'operands': {'no': [4, None]}}
        self.assertEqual(model, clap.builder.export(mode))
        self.assertEqual(model, clap.builder.export(clap.builder.Builder().set(model).build().get()))

    def testExportingNestedCommandEmpty(self):
        mode = clap.mode.RedCommand().addCommand(name='child', command=clap.mode.RedCommand())
        model = {'commands': {'child': {}}}
        self.assertEqual(model, clap.builder.export(mode))
        self.assertEqual(model, clap.builder.export(clap.builder.Builder().set(model).build().get()))

    def testExportingNestedCommandWithSingleGlobalOption(self):
        mode = clap.mode.RedCommand()
        mode.addGlobalOption(clap.option.Option(short='g', long='global'))
        mode.addCommand(name='child', command=clap.mode.RedCommand().addCommand(name='infant', command=clap.mode.RedCommand()))
        mode.propagate()
        model = {'modes': {'child': {'modes': {'infant': {}}}}, 'options': {'global': [{'short': 'g', 'long': 'global'}]}}
        self.assertEqual(mode, clap.builder.Builder().set(clap.builder.export(mode)).build().get())


if __name__ == '__main__':
    unittest.main()
