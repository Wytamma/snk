class NestError(Exception):
    """Base class for all pipeline exceptions"""


class PipelineExistsError(NestError):
    """Thrown if the given pipeline is already installed"""


class PipelineNotFoundError(NestError):
    """Thrown if the given pipeline cannot be found"""


class InvalidPipelineRepositoryError(NestError):
    """Thrown if the given repository appears to have an invalid format."""
