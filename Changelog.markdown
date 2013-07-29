#### Changelog file for CLAP

----

#### Version 0.6.3 (2013-07-19):

* __fix__:  fixed bug in `Parser._checkneeds()` which caused `needs` param to behave like `requires`
* __fix__:  fixed bug in `Parser._checkneeds()` which caused it to raise an exception if parameter `needs` was empty list,

* __upd__:  updated regular expressions used for option string recognition,

* __new__:  `clap/base.py` module,
* __new__:  first tests added for versions `0.6.x`,

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
