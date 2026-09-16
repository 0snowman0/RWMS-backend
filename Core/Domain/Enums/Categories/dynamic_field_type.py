from enum import StrEnum


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