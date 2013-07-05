class UnrecognizedOptionError(Exception):
    """Raised when unrecognized option is found in input list.
    """
    pass


class RequiredOptionNotFoundError(Exception):
    """Raised when required option is not found in input list.
    """
    pass


class MissingArgumentError(Exception):
    """Raised when option requires an argument but it is not found.
    """
    pass
