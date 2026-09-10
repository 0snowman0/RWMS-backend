from enum import Enum


class RequestType(str, Enum):
    COMMAND = "command"
    QUERY = "query"


class BehaviorType(str, Enum):
    TRANSACTION = "transaction"
    LOGGING = "logging"
    VALIDATION = "validation"
    PERFORMANCE = "performance"
    AUTHORIZATION = "authorization"
    CACHE = "cache"