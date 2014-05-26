"""This module contains all exceptions raised by CLAP.
"""


class UnrecognizedOptionError(Exception):
    """Raised when unrecognized option is found in input list.
    """
    pass


class UnrecognizedModeError(Exception):
    """Raised when unrecognized mode is found in input list.
    """
    pass


class RequiredOptionNotFoundError(Exception):
    """Raised when required option is not found in input list.
    """
    pass


class WantedOptionNotFoundError(Exception):
    """Raised when even one of needed options is not found.
    """
    pass


class MissingArgumentError(Exception):
    """Raised when option requires an argument but it is not found.
    """
    pass


class InvalidArgumentTypeError(Exception):
    """Raised when option's argument cannot be converted to its desired type.
    Example: option `--point` requires two arguments: (int, int) but input is:
        foo --point 42 z
    """
    pass


class MissingOperandError(Exception):
    """Raised when required operand is missing.
    """
    pass


class InvalidOperandTypeError(Exception):
    """Raised when operand has invalid type.
    """
    pass


class InvalidOperandRangeError(Exception):
    """Raised when operand has invalid type.
    """
    pass


class ConflictingOptionsError(Exception):
    """Raised when two or more conflicting options are found together.
    """
    pass


class BuilderError(Exception):
    """Raised when something wrong went in builder.
    """
    pass


class UIDesignError(Exception):
    """Raised by checker when it finds out some error in UI design.
    For example:
    * option requires another option which is unrecognized (I did it once),
    * option uses type handler that is not registered in parser,
    """
    pass
