"""This module contains all exceptions raised by CLAP.
"""


class CLAPError(Exception):
    """Base class for all CLAP specific exceptions.
    """
    pass


class UnrecognizedOptionError(CLAPError):
    """Raised when unrecognized option is found in input list.
    """
    pass


class UnrecognizedCommandError(CLAPError):
    """Raised when unrecognized command is found in input list.
    """
    pass


class AmbiguousCommandError(CLAPError):
    """Raised when ambiguous command is found in input list.
    """
    pass


class RequiredOptionNotFoundError(CLAPError):
    """Raised when required option is not found in input list.
    """
    pass


class WantedOptionNotFoundError(CLAPError):
    """Raised when even one of needed options is not found.
    """
    pass


class MissingArgumentError(CLAPError):
    """Raised when option requires an argument but it is not found.
    """
    pass


class InvalidArgumentTypeError(CLAPError):
    """Raised when option's argument cannot be converted to its desired type.
    Example: option `--point` requires two arguments: (int, int) but input is:
        foo --point 42 z
    """
    pass


class MissingOperandError(CLAPError):
    """Raised when required operand is missing.
    """
    pass


class InvalidOperandTypeError(CLAPError):
    """Raised when operand has invalid type.
    """
    pass


class InvalidOperandRangeError(CLAPError):
    """Raised when operand has invalid type.
    """
    pass


class ConflictingOptionsError(CLAPError):
    """Raised when two or more conflicting options are found together.
    """
    pass


class BuilderError(CLAPError):
    """Raised when something wrong went in builder.
    """
    pass


class UIDesignError(CLAPError):
    """Raised by checker when it finds out some error in UI design.
    For example:
    * option requires another option which is unrecognized (I did it once),
    * option uses type handler that is not registered in parser,
    """
    pass


class FixMeError(CLAPError):
    """Exception raised in places that shall be fixed before release.
    Shall not be ever caught because it acts as a FIX-ME-NOW-I-AM-HERE
    marker, and is not intended to be hidden.
    """
    pass
