
class TokenHandlingError(Exception):
    """
    Exception raised for errors in encoding or decoding JWT tokens.
    """
    def __init__(self, message: str):
        super().__init__(message)

class EnvironmentNotFound(Exception):
    def __init__(self, message: str = 'Environment not found.'):
        super().__init__(message)


class EnvironmentSlugTaken(Exception):
    def __init__(self, message: str = 'Environment slug already taken.'):
        super().__init__(message)

class BranchNotFound(Exception):
    def __init__(self, message: str = 'Branch not found.'):
        super().__init__(message)

class BranchSlugTaken(Exception):
    def __init__(self, message: str = 'Branch slug already taken.'):
        super().__init__(message)

class CommitNotFound(Exception):
    def __init__(self, message: str = 'Commit not found.'):
        super().__init__(message)

class MemberNotFound(Exception):
    def __init__(self, message: str = 'Member not found.'):
        super().__init__(message)

class MemberAlreadyExist(Exception):
    def __init__(self, message: str = 'Member already exist.'):
        super().__init__(message)

class ProjetNotFound(Exception):
    def __init__(self, message: str = 'Project not found.'):
        super().__init__(message)

class ProjectSlugTaken(Exception):
    def __init__(self, message: str = 'Project slug already taken.'):
        super().__init__(message)

class UserNotFound(Exception):
    def __init__(self, message: str = 'User not found.'):
        super().__init__(message)

class EmailAlreadyTaken(Exception):
    def __init__(self, message: str = 'Email already taken.'):
        super().__init__(message)

class UnauthorizedException(Exception):
    def __init__(self, message: str = 'You are not authorized to do this action.'):
        super().__init__(message)

class BadRequest(Exception):
    def __init__(self, message: str):
        super().__init__(message)

class ItemNotFound(Exception):
    def __init__(self, message: str = 'Item not found.'):
        super().__init__(message)

class JSONSchemaError(Exception):
    def __init__(self, message: str):
        super().__init__(message)
