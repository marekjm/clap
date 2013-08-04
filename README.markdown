### CLAP - Command Line Arguments Parser

CLAP aims at being powerful and advanced command line interface library for Python 3 language. 
Having built-in support for modes, optional and must-be-passed options, 
options with arguments (whose types can be specified and checked) it enables programmers to 
create powerful command line interfaces for Python 3 programs.


Notice: this CLAP is not in any way connected with this one: https://www.ohloh.net/p/clap

----

#### Features of CLAP:

* built-in support for modes (different options for each and global options for every one),
* support for short options passed together (`ls -lhR`),
* support for long options with equal-sign-connected arguments (`--log=./file.log`),
* support for option aliases (short/long names),
* support for typed arguments (`str`, `int`, `float` and custom types),
* checking types of arguments (eg. `--number` accepts only `int`),
* checking if all options that require it are passed with arguments,
* checking for conflicting options (eg. `--quiet` must not come with option `--verbose`),
* support for required options (eg. `--foo` must be passed),
* support for options *required* by other options (eg. `--key` requires `--value`),
* support for options *needed* by other options (eg. `--which` needs `--this` or `--that` or both),
* optional *deep* checking: check if options' arguments are not other options,

----

##### Some explanations


