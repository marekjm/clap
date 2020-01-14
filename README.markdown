# RedCLAP - Command Line Arguments Parser (Redesigned)

CLAP aims at being powerful and advanced command line interface library for Python 3 language. 
Having built-in support for modes, optional and obligatory options, 
options with arguments (with type-checking with arbitrary types) it enables programmers to 
create rich command line interfaces for Python 3 programs.


----

## Features of CLAP:

*   support for single-level and nested modes (with per-mode and global options),
*   support for grouped short options (`ls -lhR`),
*   support for long options with or without equal-sign-connected arguments (`--log=./file.log` and `--log ./file.log` are both correct),
*   support for option aliases (short/long names),
*   support for typed arguments (`str`, `int`, `float` built-in and other arbitrary types via callbacks),
*   built-in type checking of option arguments,
*   support for multiple arguments for options (e.g. `--point 0 0`),
*   checking for missing arguments with options which require them,
*   checking for conflicting options (eg. `--quiet` must not come with option `--verbose`),
*   support for options that MUST be passed to the program,
*   support for options *required by* other options (e.g. `--key` requires `--value`),
*   support for options *wanted by* other options (e.g. `--which` wants `--this` or `--that` or both),
*   good set of exceptions with detailed error messages,
*   ability to load interface from JSON descriptions,
*   automatic generation of help screens (for `your-tool help` command) with per-mode, per-option, and per-operand descriptions,
    usage examples, and more
*   support for shortcuts for command names (shortest-unique name is sufficient for CLAP to resolve the command, it is not
    necessary to write full names)

CLAP is not the most easy to use command line arguments parser for Python, but I am quite confident that it is one
of the most powerful (if not *the* most powerful) framework for writing command line interfaces.
With excellent support for modes, options, and operands, automatic input verification, and help screen generation you
get a big return on your investment.

----

## Manual and examples

See the [Issue](https://git.sr.ht/~maelkum/issue) project which is the flagship
software for CLAP and uses all features the library offers.

----

## License

RedCLAP is published under GNU GPL v3 or GNU LGPL v3 (or any later version of one of this licenses).
