from pydantic import BaseModel, ConfigDict


class DynamicFieldOption(
    BaseModel,
):

    model_config = ConfigDict(
        frozen=True,
    )

    value: str

    label: str