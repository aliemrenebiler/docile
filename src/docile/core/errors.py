class DocileError(Exception):
    """A problem the user can fix; the message is safe to show as is."""


class OutputExists(DocileError):
    """The output file already exists and overwriting was not allowed."""

    def __init__(self, path):
        self.path = path
        super().__init__(f"{path} already exists")
