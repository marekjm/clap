# Design of RedCLAP

RedCLAP means Redesigned CLAP and is direct descendant of the CLAP library.
Its development started after numerous flaws, bugs and shortcomings in the original CLAP have been
exposed and the design proved to be too complex to be fixed reasonably.

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
