class NestError(Exception):
    """
    Base class for all workflow exceptions.
    """


class WorkflowExistsError(NestError):
    """
    Thrown if the given workflow is already installed.
    """


class WorkflowNotFoundError(NestError):
    """
    Thrown if the given workflow cannot be found.
    """


class InvalidWorkflowRepositoryError(NestError):
    """
    Thrown if the given repository appears to have an invalid format.
    """

class InvalidWorkflowError(NestError):
    """
    Thrown if the given workflow appears to have an invalid format.
    """
