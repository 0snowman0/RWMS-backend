try:
    from enum import StrEnum
except ImportError:
    from enum import Enum

    class StrEnum(str, Enum):
        pass


class DynamicFieldType(
    StrEnum,
):

    STRING = "string"

    INTEGER = "integer"

    DECIMAL = "decimal"

    BOOLEAN = "boolean"

    DATE = "date"

    DATETIME = "datetime"

    SELECT = "select"

    MULTI_SELECT = "multi_select"