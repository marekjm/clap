# Design of RedCLAP

RedCLAP means Redesigned CLAP and is direct descendant of the CLAP library.
Its development started after numerous flaws, bugs and shortcomings in the original CLAP have been
exposed and the design proved to be too complex to be fixed reasonably.

From now on, both CLAP and RedCLAP refer the new version, unless otherwise specified (e.g. by saying old-CLAP).

----

## Structure of input

Input is made of modes, options and operands. Modes can be nested.

Example:

```
program --verbose modea --foo modeb --bar modec --baz 2 4 8
```

Here, program `program` has one top-level mode and two nested modes.
Each mode has one argument-less option passed, and the last one has three operands.


### Modes

Modes are strings beginning with a letter and followed by a combination of letters, numbers, hyphens and underscores.
Modes can be nested, and can have options and operands attached.

All specified operands for modes are required to be passed, unless a nested mode appears, then they become optional.

If both operands and nested modes are accepted by a mode, last non-option string is checked for its being a name of a
nested mode.
In case the match returns true, the string is assumed to be child-mode and rest of the args is passed to it for parsing.
This can be switched off by passing `--` terminator before list of operans.

```
program modea --spam foo bar modeb --with eggs
```

In this example, `--spam` is option for `modea`, `foo bar` are its operands, and `modeb` is its child-mode which has its
own option `--with` and operand `eggs`.

Modes have:

- local options,
- global options,
- child modes,
- operands,


### Options

Standard options are local to their mode.
Global options found in parent modes are passed to their child-modes.
If a child-mode defines a global option of parent mode as *local* its propagation is stopped.

Options have:

- short name (single character preceded by single hyphen),
- long name (two or more character preceded by two hyphens),
- help message,
- list of other options the current one *requires* to be passed with it (all must be present),
- list of other options the current one *wants* to be passed with it (at least one must be present),
- list of other options the current one *conflicts with* (no one of them must be present),
- list of types of parameters for this option (may be empty), it should be a list of two-tuples: `(type, descriptive_name_for_help)`,
- boolean flag telling whether this option is required to be passed or not,
- list of options the current one is not required to be passed (only one of them may be present),
- boolean flag specifying whether this option is singular or plural (plural option means that each ocurence has semantic meaning),


### Operands

Operands are whatever non-option-looking-strings are found after options and child-modes.
List of operands begins with:

- first non-option-looking string, or
- first non-child-mode string, or
- `--` terminator,

If a mode has a defined list of types for its operands they are required.
If a mode has an empty list of operands it accepts whatever operands are given to it (and may freely discard them).
If a mode has boolean false in the place of list of operands it accepts no operands.


----

## Interface building

Information about how CLAP UIs are designed to be built.

### Operands

UIs can take various numbers and types of operands.
This is specified with `__operands__` directive in mode's JSON represnetation in UI description file.


#### Operand types

> NOTICE: this may be removed from design

On the command line, all operands are strings.
CLAP lets programmers define types into which these operands should be converted, same as for options.

Converters for most basic data types - `str`, `int` and `float` - are always present.

Converter function for `bool` type should be programmer-specified if needed.
This is because `'False'` string will result in `True` boolean value if simply passed to `bool()` function;
as such it requires a bit more sematic analysis, e.g. whether both `False` and `false` should be accepted,
should `no` also mean false etc.

Programmers can define their own, custom converter functions and use them to convert operands to any data-type they wish.
Such functions MUST:

- require exactly one parameter,
- accept string as this parameter,
- raise `ValueError` if the string has invalid form and the function is unable to convert it,

These functions are attached to builder objects, and are referred to in the UI descriptions by the name
under which the functions were attached, a custom string, not by the function name.


#### Operand schemes

The `__operands__` directive may include zero or one *scheme* of operands.
If no scheme is set, CLAP will accept any number and any type of operands.
Otherwise, the set of operands given will be matched against the scheme present.


##### Scheme layout

```
{
    ...
    "__operands__": [
        {
            "no": [<int>, <int>...],
            "types": [<str>, <str>...]
        }
    ]
}
```

The `"no"` rule specifies number of operands accepted by the mode.
The `"types"` rule specifies expected types of operands.

Both rules can be omitted, with certain restrictions.

If *no* rule is omitted and *types* is not, number of operands must be divisible by the length of types list.
List of operands will be divided into groups, and each group will have its members converted according to the
specified types.

If *no* rule is not omitted and *types* is, CLAP will accept any type of operands, and will only try to match against
number rules.

If *no* rule is omitted and *types* group is omitted, CLAP will accept any number and type of operands.
Shorthand for this behaviour is specifying no scheme at all.


##### `types` rule: defining expected types of operands

Types of operands are defined by *types* rule.
It is a list of converter-function names (i.e. list of strings).


##### `no` rule: specifying accepted numbers of operands**

Accepted numbers of operands are defined by *no* rule.
It is a list of integers.  
CLAP will interpret this list's contents and, according to them, form matching rules.

**`[]`**

If list is empty, CLAP will accept any arguments.

**`[<int>]`**

If list contains one integer and it is not negative, CLAP will accept *at most* `<int>` operands.
Useful trick is to set *no* rule to `[0]` which will cause CLAP to accept no operands.

**`[-<int>]**

If list contains one integer and it is negative, CLAP will accept *at least* `<int>` operands.

**`[<int>, <int>]`**

If list contains two integers and both are not negative, CLAP will accept any number of operands between these two integers (inclusive).
This means that `[0, 2]` sequence will cause CLAP to accept 0, 1 or 2 operands.

**`[-<int>, -<int>]` and other sequences**

Sequences containing:

- two integers that are not both positive,
- three or more integers,

are invalid.


----

### Types

Options can take arguments.
These arguments must have a defined type as the number of arguments taken is length of the list of argument types.

#### Built-in types

Just as the original CLAP, RedCLAP supportsd these types by default:

- `str`: string arguments,
- `int`: decimal integers,
- `float`: decimal floating point numbers,


#### Custom types

RedCLAP - just as original CLAP - supports custom types to be used for operands and options.
Type converters MUST BE functions taking single string as their parameter and:

- returning desired type upon successful conversion,
- raising `ValueError` upon unsuccessful conversion,


##### Adding custom type handlers

Type handlers have to be added to every parser indivdually, via API of the parser object.

Other solution if to put special `clap_typehandlers.py` file in one of the `$PYTHONPATH` directories.
This file MUST contain `TYPEHANDLERS` dictionary from which handlers will be pulled to parsers.

Example `clap_typehandlers.py` file:

```
def hexadecimal(n):
    return int(n, 16)

def octal(n):
    return int(n, 8)

TYPEHANDLERS = {
                'hex': hexadecimal,
                'oct': octal,
               }
```

If such file is placed in such a diretory that RedCLAP will be able to import it, it will do and
all type handlers set there will be available to all RedCLAP programs.

----

## JSON representations of UIs

RedCLAP UIs can be saved as JSON encoded files and
built dynamically.
This provides for easier interface building as a developer can create the UI structire in a declarative way and
let the code do the heavy lifting.

Only thing that is required and must be done in code is to set handlers for custom types.
However, if `clap_typehandlers` is used it may not be necessary.


### Modes

Example bare-bones (taking no options and having no sub-modes) UI written as JSON:

```
{
    "modes": [],
    "options": {
        "local": [],
        "global": []
    },
    "help": ""
}
```

Explanations:

- `"mode"`: is a list of child modes (modes can be nested to any level of depth),
- `"options"`: is a dictionary with two possible keys `local` and `global` (every other key is discarded),
    - `"local"`: is a list of local options (that *will not* be propagated to child modes),
    - `"global"`: is a list of global options (that *will* be propagated to child modes),
- `"help"`: is a string containing help message for this mode,


### Options

Options are described in form of JSON dictionaries.

All available keys are listed here:

- `short` (*string*): short name of the option,
- `long` (*string*): long name of the option,
- `arguments` (*list of strings*): list of types of arguments the option takes, every argument is required,
- `requires` (*list of strings*): list of options this option requires to be passed alongside it (input is valid only if all of them are found),
- `wants` (*list of strings*): list of options this option wants to be passed alongside it (input is valid even if only one of them is found),
- `conflicts` (*list of strings*): list of options this option has conflict with (input is invalid even if only one of them is found),
- `required` (*Boolean*): specifies wheter the option is required or not,
- `not_with` (*list of strings*): list of options that (if passed) render this option not required,
- `plural` (*Boolean*): if true, each use of the option is counted or acumulated (check code of parser for exact behaviour),
- `help` (*string*): help message for this option,

**Note regarding plural options:** plural options are tricky beasts and RedCLAP does some magic to support them in a reasonable way.
It is advisable to check the code of `.get()` method in the final object given after the input is parsed to get understanding of the exact behaviour of them.

The only required keys are `short` or `long`, and if one of them is present the other one is optional.
If a key not present on this list will be found in the dictionary it will cause an exception to be raised or be discarded,
check the code of builder for exact behaviour.

Examples of options described in JSON:

*Most basic; specifing only short name*

```
{"short": "f"}
```

*Slightly more advanced; specifing  short and long names, list of arguments and a help string*

```
{
    "short": "o",
    "long": "output",
    "arguments": ["str"],
    "help": "specifies output path"
}
```
