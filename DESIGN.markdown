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
- list of types of arguments for this option (may be empty), it should be a list of two-tuples: `(type, descriptive_name_for_help)`,
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

Operand converters MUST BE functions taking single string as their parameter and:

- returning desired type upon successful conversion,
- raising `ValueError` upon unsuccessful conversion,


----

## Interface building

Information about how CLAP UIs are designed to be built.

### Operands

UIs can take various numbers and types of operands.
This is specified with `__operands__` directive in mode's JSON represnetation in UI description file.


#### Operand types

> NOTICE: this may be removed from the design

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

If list contains one integer and it is positive, CLAP will accept *at most* `<int>` operands.
Useful trick is to set *no* rule to `[0]` which will cause CLAP to accept no operands.

**`[-<int>]**

If list contains one integer and it is negative, CLAP will accept *at least* `<int>` operands.

**`[<int>, <int>]`**

If list contains two integers and both are positive, CLAP will accept any number of operands between these two integers (inclusive).
This means that `[0, 2]` sequence will cause CLAP to accept 0, 1 or 2 operands.

**`[-<int>, -<int>]`**

If list contains two integers and both are negative, the sequence is invalid.

**`[<int>, <int>, <int>...]`**

Lists containing three or more integers are invalid.
