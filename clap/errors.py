class UnrecognizedOptionError(Exception):
    """Raised when unrecognized option is found in input list.
    """
    pass


class RequiredOptionNotFoundError(Exception):
    """Raised when required option is not found in input list.
    """
    pass
