### CLAP - Command Line Arguments Parser

CLAP aims at being powerful and advanced command line interface library for Python 3 language. 
Having built-in support for modes, optional and must-be-passed options, 
options with arguments (whose types can be specified) it enables programmers to easily create powerful command line interfaces.


Notice: this CLAP is not in any way connected with this one: https://www.ohloh.net/p/clap


Features of CLAP:
* built-in support for modes (different options for each and global options for every one),
* support for short options passed together (`ls -lhR`),
* support for long options with equal-sign-connected arguments (`--log=./file.log`),
* support for option aliases (short/long names),
* support for typed arguments (`str`, `int` and `float`),
* checking for conflicting options (eg. `--foo` must not come with option `--bar`),
* checking types of arguments (eg. `--number` accepts only `int`),
* support for required options (eg. `--foo` must be passed),
* support for options required by other options are specified (eg. `--key` requires `--value`),
* checking if all options that require it are passed with arguments,
* optional *deep* checking: check if options' arguments are not other options,