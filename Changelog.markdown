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

## Version 0.9.2 (2014-06-07)

This is the first version of RedCLAP, i.e. *Redesigned CLAP* and is not backwards compatible with previous release.
However, it brings major improvements to the code.

Notable new features are *operand ranges*, a method for designer to set a range of operands accepted by CLAP and
let CLAP validate them, and *plural options* - which tell CLAP to not overwrite the previously found value of an options but
rather build a list of all values passed (in case of options that take no arguments - to count how many times they occured).
This provides for greater control over user input.

Another feature is just a huge bugfix. Nested modes are finally working properly.
The can be nested *ad infinitum*, all can have operands with set ranges, all can have global and local options.

Successful improvement was done on the front of UI building.
Global options can now be added freely - after or before modes are added and are *propagated* to nested modes after the
(who would have guessed) `.propagate()` method is called on the top level mode.


- **new**:  [`DESIGN.markdown`](./DESIGN.markdown) file has been added,
- **new**:  development moved to `redclap/` directory while `clap/` contains old, untouched code from 0.9.1 release,
- **new**:  operand ranges,
- **new**:  new bahaviour of `.get()` method of parsed UI,
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
However, I don't see a need for this - if you would wnat to translate dicts and
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
Such behaviour needed some changes in code to be done and this resulted in `check()` method of `modes.Parser()`
automatically calling define before any actual checking is done. 

**Notice**: it's possible that in version 0.7.2 `modes.Parser()` will be renamed to prevent it being mistaken for `parser.Parser()` and
to imporove accuracy of error messages.


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
