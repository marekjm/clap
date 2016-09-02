# Changelog file for CLAP

This file describes changes in CLAP codebase, usage, public and private API and documentation.
It's mostly useful for developers who use the CLAP library.

#### Rules

* __fix__:  bug fixes,
* __upd__:  updated feature,
* __new__:  new features,
* __dep__:  deprecated features (scheduled for removal in next *n* versions),
* __rem__:  removed features,


----

## Version 0.11.0 (2016-09-02)

This long awaited release improves both documentation and code.
Documentation was expanded with updated examples and README-style articles explaining how to use CLAP.

On the code front, there are several imporvements.

### Shortened command names

From day-one CLAP supported short and long option names.
People who use a piece of software frequently usually memorise short versions of commonly used options, but
for a very long time CLAP did not provide a way to shorten the *command* names.
This mean that even long command names must have been written in full:

```
~]$ program some-nested command-name that-is-too --verbose --and long-to-type --foo --with spam
```

Now, the above invocation can be shortened to just:

```
~]$ program s c t --verbose --and l --foo --with spam
```

CLAP detects that a mode has nested modes, and automatically expands the shortened command name.
Expansion fails if the command name is ambiguous, i.e. when more two or more subcommands exist (e.g. `foo` and `far`) and
both share a common prefix that, and only this prefix was given to CLAP.


### Fixed rendering detailed option help

Detailed option help (`program help command subcommand --option`) now renders all help available for requested option.


### Better automatically generated help for option arguments

CLAP provides a way to describe individual option arguments, and provide more detailed help messages.
Use `argument-name:argument-type` syntax when definition option arguments:

```
{
    "short": "p",
    "long": "phone-no",
    "arguments": ["use +NN.AAABBBCCC format:str"]
}
```



----


## Version 0.10.0-rc.3 (2014-07-)

This release candidate adds two more parameters to the already available palette of
customization options for CLAP options.

Note that however promising the `defaults` option may sound it can currently be only used to provide values
for options added by CLAP (when running through `implies` hooks).
Support for omitting arguments was not coded to keep the complexity of the parser on an acceptable level.
Said complexity has to be decreased nevertheless, because the `implies` hook that became available to developers caused
the complexity level of parser to raise considerably.

Even though, optional arguments should be requested as operands - it is safer and easier to manage them this way.

This release candidate is not big in terms of List of Changes, but is *huge* in terms of functionality added.

- **new**:  `implies` parameter in `clap.option.Option`,
- **new**:  `defaults` parameter in `clap.option.Option`,
- **new**:  `conflicts()` method in `clap.option.Option`,

- **fix**:  checker can now correctly detect more cases when not enough arguments are provided to an option (i.e. instead of rising
            the invalid-type exception it will raise the missing-argument exception when the item that caused it in the first place is
            an option accepted by parser),


----

## Version 0.10.0-rc.2 (2014-07-09)

- **fix**:  fixed bug introduced in 0.9.6 which cause help runner to crash if help was requested by option,

- **upd**:  examples are no longer included in the full rendering of help screen, they need to be separately viewed,


----

## Version 0.10.0-rc.1 (2014-07-08)

All deprecated features were removed from code.

- **upd**:  `addMode()` method of `RedMode` renamed to `addCommand()`,
- **upd**:  `hasmode()` method of `RedMode` renamed to `hasCommand()`,
- **upd**:  `getmode()` method of `RedMode` renamed to `getCommand()`,
- **upd**:  `modes()` method of `RedMode` renamed to `commands()`,
- **upd**:  `mode` parameter in `clap.builder.export()` function renamed to `command`,
- **upd**:  `RedMode` class renamed to `RedCommand`,
- **upd**:  `UnrecognizedModeError` renamed to `UnrecognizedCommandError`,

- **rem**:  removed support for features deprecated in 0.9.x line,
- **rem**:  `readfile()` and `readjson()` functions were removed from `clap.builder` module,

----

## Version 0.9.6 (2014-07-04)

It seems like the 0.9.x line is about to stay for a bit longer than I expected.
However, it does not mean there are no improvements in the code.

One new feature is the `"examples"` key in `"doc"` field of the top-level command.
Apart from usage, which describes more abstract syntax, the examples are used to
provide real-life invocations of the program.  
This field may change in future (currently it is built the same way as usage) to incorporate
brief explanation what does the line do:

```
"examples": [
    {
        "line": "foo --bar baz -xy",
        "desc": "this line does something"
    }
]
```

Would yield something akin to:

```
Examples:

    program foo --bar baz -xy
        this line does something
```

This release brings another new feature: Help Runner.
It is an object which takes parsed UI and analyses it to tell whether user wanted to see help
screen or not; in either case it will act accordingly, and report the outcome to the program
developer (in code).  
As such, it shifts the burden of managing help screens yet further away from the developers so
that the library can do even more of the heavy lifting.

Currently, the help runner does not offer many customization hooks (only option-triggers can be adjusted), yet it comes with sane defaults:

- `-h` and `--help` options trigger help screen display,
- `help` as first (second, technically) command triggers help display.

The help runner can be more easily integrated into programs using `Builder` object using its `insertHelpCommand()` method which,
as the name says, inserts a model of `help` command into model of UI as a child of main command.
The call looks this way: `mode = clap.builder.Builder(model).insertHelpCommand().build().get()`

Apart from these new features, there is a deprecation also: *verb commands* (akin to Git's `commit`, `pull` or `stash`) are no longer `modes` in JSON
representations of UIs, but are `commands`.
There is a warning about this in code so CLAP will yell about UIs that are not upgraded.


- **new**:  `examples` key in `doc` field of JSON UI representations, **examples should only be set in doc for the TOP LEVEL command **,
- **new**:  `HelpRunner` object in `clap.helper` module,
- **new**:  `top()` method in `ParsedUI`,
- **new**:  `usage()` and `examples()` methods in `Helper`,
- **new**:  `insertHelpCommand()` method added to `Builder`, which makes integration with Help Runner easier and
            provides unified help interface for users of CLAP library,

- **upd**:  `Helper` was refactored a little bit,
- **upd**:  parser undergone major refactoring, actual parsing logic has been broken down into several smaller, easier to understand methods;
            maybe a separate class should be created as `Parser` seems to have too much responsibility,

- **dep**:  `modes` field in JSON UI representations, changed to `commands`,
- **dep**:  `gen` method in `Helper`, use `full` instead,

- **rem**:  `get()` method from `Parser`,
- **rem**:  `getoperands()` method from `Parser`,
- **rem**:  `clap_typehandler.py` method of setting typehandlers for CLAP,


----

## Version 0.9.5 (2014-06-21)

CLAP is now building better help screens, greatest improvement can be seen in how descriptions of commands (sub modes) are rendered, i.e.
the name of the submode is followed by a two-space break and a description of it so users can quickly check what command they want to use.

This release also fixes a bug which caused an error about unrecognized option to be incorrectly raised.

- **new**:  command descriptions in abbreviated help screens,
- **new**:  slightly refactored help screen generator and help screens' look is slightly different,
- **new**:  new way of building doc in JSON, added `"doc"` field (with `"help"` and `"usage"` keys),

- **dep**:  `"help": ` key of mode is moved to `"doc"` field,

- **fix**:  unrecognized option error incorrectly raised when aliases are passed,


----

## Version 0.9.4 (2014-06-16)

CLAP is able to build full or abbreviated help screens.
Abbreviated help screens show help only for top-level mode, i.e. its
options - local and global - and commands.
Full help screen displays help for all sub-commands.

Also, in this release CLAP code was moved back from `redclap/` to `clap/`.

Finally, 0.9.4 is most probably last release from 0.9.x line and
the next version of CLAP will mark the beginning of the 0.10.x line.


- **new**:  full help screens,
- **new**:  abbreviated help screens,

- **fix**:  checker now correctly handles one more case of unrecognized option,


----

## Version 0.9.3 (2014-06-10)

CLAP can build UIs from JSON descriptions and
export UIs built directly in Python to JSON (exporting is work-in-progress and needs more testing, though).

Another feature implemented in this release is help screen generation, but currently to only one level of depth.
This will be fixed in later releases.


- **new**:  building interfaces from JSON,
- **new**:  exporting interfaces written in Python to JSON,
- **new**:  generating help screens,
- **new**:  more fluent interface for formatter,

- **fix**:  bug in parser, which returned items for nested mode even if mode accepted no child modes,

- **rem**:  old CLAP code,
- **rem**:  old CLAP tests,
- **rem**:  old checker code from RedCLAP module,


----

## Version 0.9.2 (2014-06-07)

This is the first version of RedCLAP, i.e. *Redesigned CLAP* and is not backwards compatible with previous release.
However, it brings major improvements to the code.

Notable new features are *operand ranges*, a method for designer to set a range of operands accepted by CLAP and
let CLAP validate them, and *plural options* - which tell CLAP to not overwrite the previously found value of an options but
rather build a list of all values passed (in case of options that take no arguments - to count how many times they occurred).
This provides for greater control over user input.

Another feature is just a huge bugfix. Nested modes are finally working properly.
The can be nested *ad infinitum*, all can have operands with set ranges, all can have global and local options.

Successful improvement was done on the front of UI building.
Global options can now be added freely - after or before modes are added and are *propagated* to nested modes after the
(who would have guessed) `.propagate()` method is called on the top level mode.


- **new**:  [`DESIGN.markdown`](./DESIGN.markdown) file has been added,
- **new**:  development moved to `redclap/` directory while `clap/` contains old, untouched code from 0.9.1 release,
- **new**:  operand ranges,
- **new**:  new behavior of `.get()` method of parsed UI,
- **new**:  plural options,

- **fix**:  nested modes,
- **fix**:  global options propagation,

- **rem**:  old JSON UIs must be ported to new JSON spec,
- **rem**:  CLAP v0.9.2 changed Python APIs for building UIs,


----

#### Version 0.9.1 (2013-11-09):

Deprecated module `clap.modes` was removed.
If you haven't changed your code when update 0.9.0 arrived you must do it now.
Now, `clap.parser.Parser` supports both single and
nested parsers.

* __rem__:  `clap.modes` module was removed,


----

#### Version 0.9.0 (2013-11-):

From this version `clap.modes.Parser` is deprecated - single and nested parsers were unified and
now you can use `clap.parser.Parser` with modes (the API was copied from `clap.modes.Parser`).


* __new__:  `clap.parser.Parser().finalize()` method which will define the parser and parse it via a single call,
* __new__:  `clap.shared` module containing functions and variables shared between various CLAP modules,
* __new__:  `clap.base.Base`, `clap.parser.Parser` and `clap.modes.Parser` got new `getoperands()` method,
* __new__:  `clap.base.Base` and `clap.parser.Parser` have `__eq__()` method overloaded (comparing with `==` will be now possible),

* __upd__:  better help message generation,
* __upd__:  moved option regular expression patterns from `clap.base` to `clap.shared`,
* __upd__:  moved `lookslikeopt()` function from `clap.base` to `clap.shared`,
* __upd__:  information about default parser is now private,

* __rem__:  `lines` parameter from `Helper().help()` method - now it returns only list of strings,


----

#### Version 0.8.4 (2013-09-02):

* __fix__:  type handlers are applied also to nested parsers,


----

#### Version 0.8.3 (2013-08-31):

* __fix__:  fixed bug which prevented building JSON interfaces with local mode-options,


----

#### Version 0.8.2 (2013-08-31):

* __new__:  support for non-global options given to modes (helps writing modes which act more like parsers),


----

#### Version 0.8.1 (2013-08-31):

This version **is not backwards compatible**! You'll need to fix your JSON and/or Python built interfaces
for the new stuff - `needs` was renamed to `wants`, `NeededOptionNotFoundError` was renamed to `WantedOption...`.

* __upd__:  order in which validating methods are called (conflicts are checked just after
            unrecognized options to prevent typing a lot and getting an error about conflicting
            options),
* __upd__:  `needs` arguments renamed to `wants` in all places,
* __upd__:  `clap.checker.Checker._checkneeds` renamed to `clap.checker.Checker._checkwants`,
* __upd__:  `clap.errors.NeededOptionNotFoundError` renamed to `clap.errors.WantedOptionNotFoundError`,

* __new__:  `BuilderError` in `clap.errors`, raised when builder loads invalid JSON
* __new__:  `UIDesignError` in `clap.errors`, raised when one option requires another option
            which is undefined,
* __new__:  `parser` and `modes` arguments in `Builder.build()` for forcing build of given type,
            keep in mind that they are provided as a debug feature for JSON interfaces (type-detection
            should work without them),
* __new__:  `clap.helper.Helper` which can build help information from parsers,
* __new__:  `help` argument for options,


----

#### Version 0.7.5 (2013-08-14):

This version fixes type-detection issues with JSON-based interfaces (well, they are still alpha/beta).
Pure Python API is free from these bugs.


----

#### Version 0.7.4 (2013-08-07):

This version brings support for creating nested modes in JSON interfaces.
Apart from this, some refactoring had been done in `clap/builder.py`.
`clap.builder.ModesParser()` is no longer there - only object that is needed
to build an interface is `clap.builder.Builder()`.
Builder functions, and element-type recognition functions, are exposed so you can
use them directly with no need to initialize builder object.
However, I don't see a need for this - if you would want to translate dicts and
lists to interfaces and bother with all the stuff around them it's easier to just
code the whole interface by hand. This functionality will never be removed.

* __new__:  `isparser()`, `isoption()` and `ismodesparser()` functions in `clap.builder`,
* __new__:  `buildparser()` and `buildmodesparser()` functions in `clap.builder`,

* __upd__:  `clap.builder.Builder()` is no longer limited to simple parsers - it can
            now build also single- and nested-modes parsers.

* __rem__:  `clap.builder.ModesParser()` is removed and it's functionality is now in
            `clap.builder.Builder()`

----

#### Version 0.7.3 (2013-08-06):

This version debugs stuff (I hope) and let's you create simple-parser interfaces using
`clap.builder.Builder()` object (without need for `clap.builder.Parser()`.

* __new__:  `clap.builder.Builder().build()` let's you build simple-parser interfaces,
* __new__:  `clap.builder.Builder()._applyhandlersto()` method returns parser with applied
            type handlers,

* __rem__:  `clap.builder.Parser()` object is removed,


----

#### Version 0.7.2 (2013-08-05):

This version brings support for creating interfaces using JSON.

* __new__:  `clap.builder` module containing `Parser()` and `ModesParser()` objects used for building interfaces,


----

#### Version 0.7.1 (2013-08-04):

This version is capable of having *nested modes*, e.g. syntax like `foo bar baz --some --fancy options --after --this`.
Such behavior needed some changes in code to be done and this resulted in `check()` method of `modes.Parser()`
automatically calling define before any actual checking is done. 

**Notice**: it's possible that in version 0.7.2 `modes.Parser()` will be renamed to prevent it being mistaken for `parser.Parser()` and
to improve accuracy of error messages.


* __fix__:  fixed bug in `clap.modes.Parser().addOption()` (I forgot to port it to the new version of options)

* __new__:  `_append()` method on `clap.modes.Parser()`
* __new__:  you can now nest modes,
* __new__:  `_getarguments()` method in `clap.base.Base()`

* __upd__:  there is no need to call `define()` before `check()` on `modes.Parser()` - the latter automatically calls the former,
* __upd__:  `type()` now returns empty list if option takes no arguments,


----

#### Version 0.7.0 (2013-08-03):

**Warning**: this release is not backwards compatible, you'll need to port your software to it. 
However, only small adjustments will be needed and only the *in* part of the API changes and *out*
remains the same (not quite, it is more powerful now).


* __fix__:  fixed bug in `base.Base._getinput()` which caused it to return whole argv when it should return empty list

* __new__:  it is possible to specify multiple arguments for an option (defined as a list, returned as a tuple of arguments),

* __upd__:  `argument` parameter renamed to `arguments` in all methods and functions,


----

#### Version 0.6.3 (2013-08-02):

* __fix__:  fixed bug in `Parser._checkneeds()` which caused `needs` param to behave like `requires`
* __fix__:  fixed bug in `Parser._checkneeds()` which caused it to raise an exception if parameter `needs` was empty list,

* __upd__:  updated regular expressions used for option string recognition,

* __new__:  `clap/base.py` module,
* __new__:  `clap/checker.py` module,
* __new__:  first test suite added,

* __rem__:  `hint` parameter is removed from all CLAP components,


----

#### Version 0.6.2 (2013-07-12):

* __upd__:  `modes.Modes()` renamed to `modes.Parser()`
* __new__:  `_getinput()` method in `parser.Parser()` added another security layer to checks


----

#### Version 0.2.3 (2013-06-29):

* __new__:  `required` optional argument in `clap.Parser.add()`, if passed and option is not found in input when `check()`ing error is raised,
* __new__:  `gethint()` method in `clap.Parser`,


----

#### Version 0.2.2 (2013-06-29):

* __upd__:  if option requires no argument `None` is returned instead of raising `TypeError`


* __fix__:  


* __new__:  
