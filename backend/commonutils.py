"""Commonly used utility functions."""

# imports
import os

# constants
# exception classes
class ExecutableNotFound(Exception):
    """Raised when the which-function can't find the given executable.
    """
    def __init__(self, path):
        self.path = path

    def __str__(self):
        return "Executable %s not found" % self.path

# interface functions
def is_exe(fpath):
    """Returns True if path is executable."""
    return os.path.isfile(fpath) and os.access(fpath, os.X_OK)


def which(program):
    """Tries to find the path to executable."""
    fpath, fname = os.path.split(program)
    if is_exe(program):
        return program
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return exe_file

    raise ExecutableNotFound(program)




# classes
# internal functions & classes

