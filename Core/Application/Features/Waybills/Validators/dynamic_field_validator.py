from typing import Any

from Core.Domain.Enums.Categories.dynamic_field_type import (
    DynamicFieldType,
)
from Core.Domain.ViewModels.ValueObjects.Categories.dynamic_field_definition import (
    DynamicFieldDefinition,
)


def validate_dynamic_fields(
    values: dict[str, Any],
    schema: list[DynamicFieldDefinition],
) -> list[str]:
    """
    Validate dynamic field values against the template's field definitions.
    Returns a list of error messages (empty if valid).
    """
    errors: list[str] = []

    for field_def in schema:
        if not field_def.is_active:
            continue

        value = values.get(field_def.name)

        # --- Required check ---
        if field_def.required and (
            field_def.name not in values
            or value is None
        ):
            errors.append(
                f"Required dynamic field '{field_def.title}' is missing."
            )
            continue

        if value is None:
            continue

        # --- Type checks ---
        if field_def.field_type == DynamicFieldType.STRING:
            if not isinstance(value, str):
                errors.append(
                    f"Field '{field_def.title}' must be a string."
                )
            else:
                if (
                    field_def.min_length is not None
                    and len(value) < field_def.min_length
                ):
                    errors.append(
                        f"Field '{field_def.title}' is too short "
                        f"(min {field_def.min_length})."
                    )
                if (
                    field_def.max_length is not None
                    and len(value) > field_def.max_length
                ):
                    errors.append(
                        f"Field '{field_def.title}' is too long "
                        f"(max {field_def.max_length})."
                    )

        elif field_def.field_type in (
            DynamicFieldType.INTEGER,
            DynamicFieldType.DECIMAL,
        ):
            if not isinstance(value, (int, float)):
                errors.append(
                    f"Field '{field_def.title}' must be a number."
                )
            else:
                if (
                    field_def.min_value is not None
                    and value < float(field_def.min_value)
                ):
                    errors.append(
                        f"Field '{field_def.title}' is below "
                        f"minimum ({field_def.min_value})."
                    )
                if (
                    field_def.max_value is not None
                    and value > float(field_def.max_value)
                ):
                    errors.append(
                        f"Field '{field_def.title}' exceeds "
                        f"maximum ({field_def.max_value})."
                    )

        elif field_def.field_type == DynamicFieldType.BOOLEAN:
            if not isinstance(value, bool):
                errors.append(
                    f"Field '{field_def.title}' must be a boolean."
                )

        elif field_def.field_type == DynamicFieldType.SELECT:
            valid_options = [
                opt.value for opt in field_def.options
            ]
            if value not in valid_options:
                errors.append(
                    f"Field '{field_def.title}' has invalid option "
                    f"'{value}'. Valid: {valid_options}"
                )

        elif field_def.field_type == DynamicFieldType.MULTI_SELECT:
            if not isinstance(value, list):
                errors.append(
                    f"Field '{field_def.title}' must be a list."
                )
            else:
                valid_options = [
                    opt.value for opt in field_def.options
                ]
                for v in value:
                    if v not in valid_options:
                        errors.append(
                            f"Field '{field_def.title}' has invalid "
                            f"option '{v}'."
                        )

    return errors
