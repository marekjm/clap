### CLAP - Command Line Arguments Parser

CLAP aims at being powerful and advanced command line interface library for Python 3 language. 
Having built-in support for modes, optional and must-be-passed options, 
options with arguments (whose types can be specified and checked) it enables programmers to 
create powerful command line interfaces for Python 3 programs.


----

#### Features of CLAP:

*   support for single-level and nested modes (with per-mode and global options),
*   support for short options passed together (`ls -lhR`),
*   support for long options with equal-sign-connected arguments (`--log=./file.log`),
*   support for option aliases (short/long names),
*   support for typed arguments (`str`, `int`, `float` and custom types),
*   support for multiple arguments (e.g. `--point 0 0`),
*   built-in type checking of arguments (eg. `--number` accepts only `int`),
*   checking for missing arguemnts with options which require them,
*   checking for conflicting options (eg. `--quiet` must not come with option `--verbose`),
*   support for options that MUST be passed to the program,
*   support for options *required by* other options (e.g. `--key` requires `--value`),
*   support for options *needed by* other options (e.g. `--which` needs `--this` or `--that` or both),
*   good set of exception with detailed error messages,
*   ability to build interface in JSON and load it to your program,


----

#### Manual

There is a manual which you may be interested in located in `manual/` directory.


----

#### Reference implemntations

There are reference/example implementations of interface using CLAP which you can check.
Look for the files with `example` in their names in top-level directory.

For more advanced example (with an example of error handling) check
[`diacli`](https://github.com/marekjm/diacli) project.
