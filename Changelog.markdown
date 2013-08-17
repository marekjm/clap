#### Changelog file for CLAP

----

#### Version 0.7.6 (2013-08-):

* __upd__:  order in which validating methods are called (conflicts are checked just after
            unrecognized options to prevent typing a lot and getting an error about conflicting
            options),

* __new__:  `BuilderError` in `clap.errors`, raised when builder loads invalid JSON


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
