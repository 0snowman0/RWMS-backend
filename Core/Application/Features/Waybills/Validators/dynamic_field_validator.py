from typing import Any
from uuid import UUID

from Core.Domain.Enums.Categories.dynamic_field_type import (
    DynamicFieldType,
)
from Core.Domain.ViewModels.ValueObjects.Categories.dynamic_field_definition import (
    DynamicFieldDefinition,
)
from Core.Domain.ViewModels.ValueObjects.Waybills.waybill_attribute_value import (
    WaybillAttributeValue,
)


def validate_waybill_attributes(
    attributes: list[WaybillAttributeValue],
    schema: list[DynamicFieldDefinition],
    check_required: bool = True,
) -> tuple[list[str], list[WaybillAttributeValue]]:
    """
    Validate dynamic attribute values against the template's field definitions.
    - Checks for duplicate attributes
    - Checks for unknown field_ids
    - Checks required fields (if check_required=True)
    - Fills default values for missing fields
    - Validates data types, lengths, ranges, and options
    Returns (errors, final_attributes).
    """
    errors: list[str] = []
    final_attributes = list(attributes)

    # Map schema fields by str(field_id)
    field_lookup = {
        str(f.field_id): f
        for f in schema
        if f.is_active
    }

    # 1. Duplicate check
    field_ids = [str(a.field_id) for a in attributes]
    if len(field_ids) != len(set(field_ids)):
        errors.append("Duplicate attribute field_ids are not allowed.")
        return errors, final_attributes

    # 2. Check unknown field_ids
    for attr in attributes:
        fid = str(attr.field_id)
        if fid not in field_lookup:
            errors.append(f"Attribute with field_id '{fid}' does not belong to the template.")

    if errors:
        return errors, final_attributes

    # Lookup passed attributes by str(field_id)
    attr_lookup = {str(a.field_id): a for a in attributes}

    # 3. Handle required & default values
    for fid, field_def in field_lookup.items():
        if fid in attr_lookup:
            continue

        if field_def.default_value is not None:
            default_attr = WaybillAttributeValue(
                field_id=field_def.field_id,
                value=field_def.default_value,
            )
            final_attributes.append(default_attr)
            attr_lookup[fid] = default_attr
        elif check_required and field_def.required:
            errors.append(
                f"Required dynamic field '{field_def.title}' ({field_def.name}) is missing."
            )

    # 4. Type & range validation
    for fid, attr in attr_lookup.items():
        field_def = field_lookup.get(fid)
        if field_def is None:
            continue

        value = attr.value
        if value is None:
            if check_required and field_def.required:
                errors.append(
                    f"Required field '{field_def.title}' cannot have a null value."
                )
            continue

        # Type checks
        if field_def.field_type == DynamicFieldType.STRING:
            if not isinstance(value, str):
                errors.append(f"Field '{field_def.title}' must be a string.")
            else:
                if field_def.min_length is not None and len(value) < field_def.min_length:
                    errors.append(
                        f"Field '{field_def.title}' is too short (min {field_def.min_length})."
                    )
                if field_def.max_length is not None and len(value) > field_def.max_length:
                    errors.append(
                        f"Field '{field_def.title}' is too long (max {field_def.max_length})."
                    )

        elif field_def.field_type in (
            DynamicFieldType.INTEGER,
            DynamicFieldType.DECIMAL,
        ):
            if not isinstance(value, (int, float)):
                errors.append(f"Field '{field_def.title}' must be a number.")
            else:
                if field_def.min_value is not None and value < float(field_def.min_value):
                    errors.append(
                        f"Field '{field_def.title}' is below minimum ({field_def.min_value})."
                    )
                if field_def.max_value is not None and value > float(field_def.max_value):
                    errors.append(
                        f"Field '{field_def.title}' exceeds maximum ({field_def.max_value})."
                    )

        elif field_def.field_type == DynamicFieldType.BOOLEAN:
            if not isinstance(value, bool):
                errors.append(f"Field '{field_def.title}' must be a boolean.")

        elif field_def.field_type == DynamicFieldType.SELECT:
            valid_options = [opt.value for opt in field_def.options]
            if value not in valid_options:
                errors.append(
                    f"Field '{field_def.title}' has invalid option '{value}'. Valid: {valid_options}"
                )

        elif field_def.field_type == DynamicFieldType.MULTI_SELECT:
            if not isinstance(value, list):
                errors.append(f"Field '{field_def.title}' must be a list.")
            else:
                valid_options = [opt.value for opt in field_def.options]
                for v in value:
                    if v not in valid_options:
                        errors.append(
                            f"Field '{field_def.title}' has invalid option '{v}'."
                        )

    return errors, final_attributes
