class NestError(Exception):
    """Base class for all pipeline exceptions"""


class PipelineExistsError(NestError):
    """Thrown if the given pipeline is already installed"""


class PipelineNotFoundError(NestError):
    """Thrown if the given pipeline cannot be found"""


class InvalidPipelineRepositoryError(NestError):
    """Thrown if the given repository appears to have an invalid format."""


class SnkConfigError(Exception):
    """Base class for all SNK config exceptions"""

class InvalidSnkConfigError(SnkConfigError, ValueError):
    """Thrown if the given SNK config appears to have an invalid format."""

class MissingSnkConfigError(SnkConfigError, FileNotFoundError):
    """Thrown if the given SNK config file cannot be found."""