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

Some definitions may be confusing at first so here are explanations to some concepts used in 
CLAP.

*required option*

This is option required by the program to run. User MUST pass it. 


*option* ***required*** *by other option*

It's set via `requires` parameter. Every option present on this list must be present in `argv`.

Option that is not required by a program directly but is required when some other option is 
passed. Imagine that you have a program which inserts key/value pairs into some file. Let's 
run it:

    our-program

It did nothing. But when we pass it only a key option...

    our-program --key foo
    fatal: option --key requires option --value to be passed

... it returns an error. User MUST pass both key and value.

    our-program --key foo --value bar


*option* ***needed*** *by other option*

It's set via `needs` parameter. **At least one** option present on this list must be present in `argv`. 
Non-greedy version of `requires`.

Imagine that `--which` option needs `--this` or `--that` option to be present but not neccessarily both. 


*conflicting options*

Options that must not come together. This may be because it would break the program, for convinience, because the logic 
for such combination is not yet implemented or becuase author likes it that way.
First example which comes to my mind (I implement this rule in all my programs) is `--verbose` and `--quiet` options. 
What sense is passing them together? Passing `--quiet` and `--debug` together makes more sense because user may want not 
to be distracted by normal output when debugging.
