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


@unittest.skip('due to library being redesigned')
class RedBuilderTests(unittest.TestCase):
    def testTypeRecognitionOption(self):
        data = {'short': 'p',
                'arguments': [int, int]
                }
        self.assertEqual(True, clap.builder.isoption(data))

    def testTypeRecognitionParser(self):
        data = [ {'short': 'p',
                 'arguments': [int, int]
                 }
                 ]
        self.assertEqual(True, clap.builder.isparser(data))

    def testTypeRecognitionNestedParser(self):
        data = {
                'foo': [
                    {
                        'short': 'p',
                        'arguments': [int, int]
                    }
                    ],
                '__global__': [
                        {
                            'short': 'o',
                            'long': 'output',
                            'arguments': [str]
                        }
                    ]
                }
        self.assertEqual(True, clap.builder.isparser(data))

    def testBuildingSingleParserDefinedAsNestedWithAllOptionsGlobal(self):
        parser = clap.parser.Parser()
        parser.addOption(short='s', long='string', arguments=[str])
        parser.addOption(short='i', long='integer', arguments=[int])
        parser.addOption(short='f', long='float', arguments=[float])
        built = clap.builder.Builder(path='./testfiles/single_parser_defined_as_nested_with_all_opts_global.json').build()
        self.assertEqual(parser.finalize(), built.finalize())

    def testBuildingSingleParserDefinedAsListOfOptions(self):
        parser = clap.parser.Parser()
        parser.addOption(short='s', long='string', arguments=[str])
        parser.addOption(short='i', long='integer', arguments=[int])
        parser.addOption(short='f', long='float', arguments=[float])
        built = clap.builder.Builder(path='./testfiles/single_parser_defined_as_list_of_options.json').build()
        self.assertEqual(parser.finalize().getopts(), built.finalize().getopts())

    def testBuildingMultipleModeParser(self):
        parser = clap.parser.Parser()
        parser.addMode('foo', clap.parser.Parser().addOption(short='f', long='foo'))
        parser.addMode('bar', clap.parser.Parser().addOption(short='b', long='bar'))
        parser.addOption(short='B', long='baz')
        built = clap.builder.Builder(path='./testfiles/multiple_modes_parser.json').build()
        self.assertEqual(sorted(parser.finalize()._modes.keys()), sorted(built.finalize()._modes.keys()))


if __name__ == '__main__':
    unittest.main()
