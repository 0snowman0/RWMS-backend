from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Iterable, TypeVar

from Core.Application.Contracts.Mapper.mapper import IMapper


TSource = TypeVar("TSource")
TDestination = TypeVar("TDestination")


# ============================================================
# Mapping Rules
# ============================================================


@dataclass
class MemberRule:
    source_name: str | None = None

    transform: Callable[[Any], Any] | None = None

    resolver: Callable[[Any], Any] | None = None

    ignore: bool = False


@dataclass
class MappingConfig:
    source_type: type

    destination_type: type

    member_rules: dict[str, MemberRule] = field(
        default_factory=dict
    )


# ============================================================
# Mapping Builder
# ============================================================


class MappingBuilder:

    def __init__(
        self,
        config: MappingConfig,
    ):
        self._config = config

    def for_member(
        self,
        destination_member: str,
        *,
        source: str | None = None,
        transform: Callable[[Any], Any] | None = None,
        resolver: Callable[[Any], Any] | None = None,
    ) -> MappingBuilder:

        if source is not None and resolver is not None:
            raise ValueError(
                "'source' and 'resolver' cannot be used together."
            )

        self._config.member_rules[
            destination_member
        ] = MemberRule(
            source_name=source,
            transform=transform,
            resolver=resolver,
        )

        return self

    def ignore(
        self,
        destination_member: str,
    ) -> MappingBuilder:

        self._config.member_rules[
            destination_member
        ] = MemberRule(
            ignore=True
        )

        return self


# ============================================================
# Mapper
# ============================================================


class Mapper(IMapper):

    def __init__(self):
        self._configs: dict[
            tuple[type, type],
            MappingConfig,
        ] = {}

    # ========================================================
    # Configuration
    # ========================================================

    def create_map(
        self,
        source_type: type[TSource],
        destination_type: type[TDestination],
    ) -> MappingBuilder:

        config = MappingConfig(
            source_type=source_type,
            destination_type=destination_type,
        )

        key = (
            source_type,
            destination_type,
        )

        self._configs[key] = config

        return MappingBuilder(
            config=config,
        )

    # ========================================================
    # Map Object -> Object
    # ========================================================

    def map(
        self,
        source: Any,
        destination_type: type[TDestination],
        *,
        ignore_none: bool = False,
        ignore_unset: bool = False,
    ) -> TDestination:

        if source is None:
            raise ValueError(
                "Source cannot be None."
            )

        values = self._build_values(
            source=source,
            destination_type=destination_type,
            ignore_none=ignore_none,
            ignore_unset=ignore_unset,
        )

        return destination_type(
            **values
        )

    # ========================================================
    # Map List -> List
    # ========================================================

    def map_list(
        self,
        source: Iterable[Any],
        destination_type: type[TDestination],
        *,
        ignore_none: bool = False,
        ignore_unset: bool = False,
    ) -> list[TDestination]:

        return [
            self.map(
                item,
                destination_type,
                ignore_none=ignore_none,
                ignore_unset=ignore_unset,
            )
            for item in source
        ]

    # ========================================================
    # Map Object -> Existing Object
    # ========================================================

    def map_to(
        self,
        source: Any,
        destination: TDestination,
        *,
        ignore_none: bool = False,
        ignore_unset: bool = False,
    ) -> TDestination:

        if source is None:
            raise ValueError(
                "Source cannot be None."
            )

        values = self._build_values(
            source=source,
            destination_type=type(destination),
            ignore_none=ignore_none,
            ignore_unset=ignore_unset,
        )

        for field_name, value in values.items():
            setattr(
                destination,
                field_name,
                value,
            )

        return destination

    # ========================================================
    # Build Mapping Values
    # ========================================================

    def _build_values(
        self,
        source: Any,
        destination_type: type,
        ignore_none: bool,
        ignore_unset: bool,
    ) -> dict[str, Any]:

        source_type = type(source)

        config = self._configs.get(
            (
                source_type,
                destination_type,
            )
        )

        destination_fields = (
            self._get_destination_fields(
                destination_type
            )
        )

        values: dict[str, Any] = {}

        for destination_field in destination_fields:

            rule = None

            if config is not None:
                rule = config.member_rules.get(
                    destination_field
                )

            # --------------------------------------------
            # Ignore
            # --------------------------------------------

            if rule is not None and rule.ignore:
                continue

            # --------------------------------------------
            # Resolver
            # --------------------------------------------

            if (
                rule is not None
                and rule.resolver is not None
            ):
                value = rule.resolver(
                    source
                )

            else:

                # ----------------------------------------
                # Determine source field
                # ----------------------------------------

                if (
                    rule is not None
                    and rule.source_name is not None
                ):
                    source_field = (
                        rule.source_name
                    )
                else:
                    source_field = (
                        destination_field
                    )

                # ----------------------------------------
                # Ignore unset
                # ----------------------------------------

                if (
                    ignore_unset
                    and not self._is_field_set(
                        source,
                        source_field,
                    )
                ):
                    continue

                # ----------------------------------------
                # Get source value
                # ----------------------------------------

                exists, value = (
                    self._get_source_value(
                        source,
                        source_field,
                    )
                )

                if not exists:
                    continue

            # --------------------------------------------
            # Ignore None
            # --------------------------------------------

            if (
                ignore_none
                and value is None
            ):
                continue

            # --------------------------------------------
            # Transform
            # --------------------------------------------

            if (
                rule is not None
                and rule.transform is not None
            ):
                value = rule.transform(
                    value
                )

            values[
                destination_field
            ] = value

        return values

    # ========================================================
    # Get Destination Fields
    # ========================================================

    @staticmethod
    def _get_destination_fields(
        destination_type: type,
    ) -> set[str]:

        fields: set[str] = set()

        # --------------------------------------------
        # Pydantic V2
        # --------------------------------------------

        model_fields = getattr(
            destination_type,
            "model_fields",
            None,
        )

        if model_fields is not None:
            fields.update(
                model_fields.keys()
            )

        # --------------------------------------------
        # Normal Python Classes
        # --------------------------------------------

        for cls in reversed(
            destination_type.__mro__
        ):

            annotations = getattr(
                cls,
                "__annotations__",
                {},
            )

            fields.update(
                annotations.keys()
            )

        # --------------------------------------------
        # SQLAlchemy
        # --------------------------------------------

        sqlalchemy_mapper = getattr(
            destination_type,
            "__mapper__",
            None,
        )

        if sqlalchemy_mapper is not None:

            fields.update(
                attribute.key
                for attribute
                in sqlalchemy_mapper.column_attrs
            )

        return fields

    # ========================================================
    # Get Source Value
    # ========================================================

    @staticmethod
    def _get_source_value(
        source: Any,
        field_name: str,
    ) -> tuple[bool, Any]:

        # --------------------------------------------
        # Dict
        # --------------------------------------------

        if isinstance(
            source,
            dict,
        ):

            if field_name not in source:
                return False, None

            return (
                True,
                source[field_name],
            )

        # --------------------------------------------
        # Object
        # --------------------------------------------

        if not hasattr(
            source,
            field_name,
        ):
            return False, None

        return (
            True,
            getattr(
                source,
                field_name,
            ),
        )

    # ========================================================
    # Check Field Set
    # ========================================================

    @staticmethod
    def _is_field_set(
        source: Any,
        field_name: str,
    ) -> bool:

        # --------------------------------------------
        # Pydantic V2
        # --------------------------------------------

        fields_set = getattr(
            source,
            "model_fields_set",
            None,
        )

        if fields_set is not None:
            return (
                field_name
                in fields_set
            )

        # --------------------------------------------
        # Dict
        # --------------------------------------------

        if isinstance(
            source,
            dict,
        ):
            return (
                field_name
                in source
            )

        # --------------------------------------------
        # Normal Object
        # --------------------------------------------

        return hasattr(
            source,
            field_name,
        )