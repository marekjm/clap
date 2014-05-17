"""Module containg mode implementation.
"""


class Mode:
    """Actual mode implementation.
    """
    def __init__(self):
        self._options = []
        self._modes = {}
        self._operands = []

    def operands(self):
        """Returns copy of list of operands.
        """
        return self._operands[:]

    def appendOption(self, o):
        """Append option to this mode.
        """
        return self

    def appendMode(self, m):
        """Append nested mode to this mode.
        """
        return self
