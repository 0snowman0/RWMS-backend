import re

from itertools import permutations
from typing import Any, TypeVar

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from Core.Application.Contracts.DataBases.DatabaseRoutines.database_routine_executor import (
    IDatabaseRoutineExecutor,
)

from Core.Application.Contracts.Mapper.mapper import (
    IMapper,
)
from Core.Domain.ViewModels.DatabaseRoutines.routine_result_set import RoutineResultSet




T = TypeVar("T")


class PostgresRoutineExecutor(
    IDatabaseRoutineExecutor,
):

    MAX_MULTI_RESULT_SETS = 3

    AUTO_MATCH_MIN_SCORE = 0.60

    AUTO_MATCH_AMBIGUITY_MARGIN = 0.05

    def __init__(
        self,
        session: AsyncSession,
        mapper: IMapper,
    ):
        self._session = session
        self._mapper = mapper

    # =========================================================
    # Execute Procedure - No Result
    # =========================================================

    async def execute(
        self,
        name: str,
        params: dict[str, Any] | None = None,
    ) -> None:

        params = self._prepare_params(
            params
        )

        statement = text(
            f"CALL {self._build_call(name, params)}"
        )

        await self._session.execute(
            statement,
            params,
        )

    # =========================================================
    # Execute Function - Raw Result
    # =========================================================

    async def execute_raw(
        self,
        name: str,
        params: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:

        params = self._prepare_params(
            params
        )

        statement = text(
            f"SELECT * FROM {self._build_call(name, params)}"
        )

        result = await self._session.execute(
            statement,
            params,
        )

        return [
            dict(row)
            for row in result.mappings().all()
        ]

    # =========================================================
    # Execute Function - Scalar Result
    # =========================================================

    async def execute_scalar(
        self,
        name: str,
        params: dict[str, Any] | None = None,
    ) -> Any:

        params = self._prepare_params(
            params
        )

        statement = text(
            f"SELECT {self._build_call(name, params)}"
        )

        result = await self._session.execute(
            statement,
            params,
        )

        return result.scalar_one_or_none()

    # =========================================================
    # Execute Function - One Result
    # =========================================================

    async def execute_one(
        self,
        name: str,
        destination_type: type[T],
        params: dict[str, Any] | None = None,
    ) -> T | None:

        params = self._prepare_params(
            params
        )

        statement = text(
            f"SELECT * FROM {self._build_call(name, params)}"
        )

        result = await self._session.execute(
            statement,
            params,
        )

        row = result.mappings().first()

        if row is None:
            return None

        return self._mapper.map(
            dict(row),
            destination_type,
        )

    # =========================================================
    # Execute Function - List Result
    # =========================================================

    async def execute_list(
        self,
        name: str,
        destination_type: type[T],
        params: dict[str, Any] | None = None,
    ) -> list[T]:

        params = self._prepare_params(
            params
        )

        statement = text(
            f"SELECT * FROM {self._build_call(name, params)}"
        )

        result = await self._session.execute(
            statement,
            params,
        )

        rows = [
            dict(row)
            for row in result.mappings().all()
        ]

        return self._mapper.map_list(
            rows,
            destination_type,
        )

    # =========================================================
    # Execute Procedure - Multi Result
    # =========================================================

    async def execute_multi(
        self,
        name: str,
        destination_types: tuple[type, ...],
        params: dict[str, Any] | None = None,
        result_count: int | None = None,
    ) -> tuple[list[Any], ...]:

        if not destination_types:
            raise ValueError(
                "At least one destination type is required."
            )

        if len(destination_types) > self.MAX_MULTI_RESULT_SETS:
            raise ValueError(
                "Maximum destination type count is 3."
            )

        if result_count is None:
            result_count = len(destination_types)

        if result_count < 1:
            raise ValueError(
                "Result count must be at least 1."
            )

        if result_count > self.MAX_MULTI_RESULT_SETS:
            raise ValueError(
                "Maximum result set count is 3."
            )

        if result_count > len(destination_types):
            raise ValueError(
                "Result count cannot be greater than "
                "destination type count."
            )

        params = self._prepare_params(
            params
        )

        cursor_parameters = tuple(
            f"cursor{index}"
            for index in range(
                1,
                result_count + 1,
            )
        )

        routine_call = (
            self._build_multi_call(
                name=name,
                params=params,
                cursor_parameters=cursor_parameters,
            )
        )

        call_result = await self._session.execute(
            text(
                f"CALL {routine_call}"
            ),
            params,
        )

        call_row = (
            call_result
            .mappings()
            .first()
        )

        if call_row is None:
            return tuple(
                []
                for _ in destination_types
            )

        result_sets: list[
            RoutineResultSet
        ] = []

        for cursor_parameter in cursor_parameters:

            cursor_name = call_row.get(
                cursor_parameter
            )

            if cursor_name is None:
                continue

            result_set = (
                await self._fetch_cursor(
                    str(cursor_name)
                )
            )

            result_sets.append(
                result_set
            )

        if not result_sets:
            return tuple(
                []
                for _ in destination_types
            )

        matches = (
            self._match_result_sets(
                result_sets=result_sets,
                destination_types=destination_types,
            )
        )

        mapped_results: list[
            list[Any]
        ] = [
            []
            for _ in destination_types
        ]

        for (
            result_set,
            destination_index,
        ) in zip(
            result_sets,
            matches,
        ):

            destination_type = (
                destination_types[
                    destination_index
                ]
            )

            mapped_results[
                destination_index
            ] = self._mapper.map_list(
                result_set.rows,
                destination_type,
            )

        return tuple(
            mapped_results
        )

    # =========================================================
    # Fetch RefCursor
    # =========================================================

    async def _fetch_cursor(
        self,
        cursor_name: str,
    ) -> RoutineResultSet:

        quoted_cursor = (
            self._quote_identifier(
                cursor_name
            )
        )

        result = await self._session.execute(
            text(
                f"FETCH ALL FROM {quoted_cursor}"
            )
        )

        columns = tuple(
            str(column)
            for column in result.keys()
        )

        rows = [
            dict(row)
            for row in result.mappings().all()
        ]

        await self._session.execute(
            text(
                f"CLOSE {quoted_cursor}"
            )
        )

        return RoutineResultSet(
            columns=columns,
            rows=rows,
        )

    # =========================================================
    # Match Result Sets To DTOs
    # =========================================================

    def _match_result_sets(
        self,
        result_sets: list[RoutineResultSet],
        destination_types: tuple[type, ...],
    ) -> tuple[int, ...]:

        possible_matches: list[
            tuple[
                float,
                tuple[int, ...],
            ]
        ] = []

        destination_indexes = range(
            len(destination_types)
        )

        for assignment in permutations(
            destination_indexes,
            len(result_sets),
        ):

            total_score = 0.0
            valid = True

            for (
                result_set,
                destination_index,
            ) in zip(
                result_sets,
                assignment,
            ):

                destination_type = (
                    destination_types[
                        destination_index
                    ]
                )

                score = (
                    self._calculate_similarity(
                        result_set.columns,
                        destination_type,
                    )
                )

                if (
                    score
                    < self.AUTO_MATCH_MIN_SCORE
                ):
                    valid = False
                    break

                total_score += score

            if valid:

                average_score = (
                    total_score
                    / len(result_sets)
                )

                possible_matches.append(
                    (
                        average_score,
                        assignment,
                    )
                )

        if not possible_matches:
            raise ValueError(
                "No suitable DTO mapping was found "
                "for the returned result sets."
            )

        possible_matches.sort(
            key=lambda item: item[0],
            reverse=True,
        )

        best_score, best_assignment = (
            possible_matches[0]
        )

        if len(possible_matches) > 1:

            second_score = (
                possible_matches[1][0]
            )

            if (
                best_score - second_score
                < self.AUTO_MATCH_AMBIGUITY_MARGIN
            ):
                raise ValueError(
                    "Result set mapping is ambiguous. "
                    "DTO structures are too similar."
                )

        return best_assignment

    # =========================================================
    # Calculate DTO Similarity
    # =========================================================

    def _calculate_similarity(
        self,
        columns: tuple[str, ...],
        destination_type: type,
    ) -> float:

        source_fields = {
            field.lower()
            for field in columns
        }

        destination_fields = {
            field.lower()
            for field in self._get_destination_fields(
                destination_type
            )
        }

        if not source_fields:
            return 0.0

        if not destination_fields:
            return 0.0

        matched_fields = (
            source_fields
            & destination_fields
        )

        destination_coverage = (
            len(matched_fields)
            / len(destination_fields)
        )

        source_coverage = (
            len(matched_fields)
            / len(source_fields)
        )

        return (
            destination_coverage * 0.80
            +
            source_coverage * 0.20
        )

    # =========================================================
    # Get DTO / Model Fields
    # =========================================================

    @staticmethod
    def _get_destination_fields(
        destination_type: type,
    ) -> set[str]:

        fields: set[str] = set()

        # Pydantic V2
        model_fields = getattr(
            destination_type,
            "model_fields",
            None,
        )

        if model_fields is not None:
            fields.update(
                model_fields.keys()
            )

        # Normal Classes / Dataclasses
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

        # SQLAlchemy
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

    # =========================================================
    # Build Normal Routine Call
    # =========================================================

    @classmethod
    def _build_call(
        cls,
        name: str,
        params: dict[str, Any],
    ) -> str:

        cls._validate_name(
            name
        )

        arguments = []

        for parameter in params:

            cls._validate_identifier(
                parameter
            )

            arguments.append(
                f"{parameter} => :{parameter}"
            )

        return (
            f"{name}("
            f"{', '.join(arguments)}"
            f")"
        )

    # =========================================================
    # Build Multi Result Procedure Call
    # =========================================================

    @classmethod
    def _build_multi_call(
        cls,
        name: str,
        params: dict[str, Any],
        cursor_parameters: tuple[str, ...],
    ) -> str:

        cls._validate_name(
            name
        )

        arguments = []

        for parameter in params:

            cls._validate_identifier(
                parameter
            )

            arguments.append(
                f"{parameter} => :{parameter}"
            )

        for cursor_parameter in cursor_parameters:

            cls._validate_identifier(
                cursor_parameter
            )

            arguments.append(
                f"{cursor_parameter} => NULL"
            )

        return (
            f"{name}("
            f"{', '.join(arguments)}"
            f")"
        )

    # =========================================================
    # Prepare Parameters
    # =========================================================

    @classmethod
    def _prepare_params(
        cls,
        params: dict[str, Any] | None,
    ) -> dict[str, Any]:

        params = params or {}

        for parameter in params:

            cls._validate_identifier(
                parameter
            )

        return params

    # =========================================================
    # Validate Routine Name
    # =========================================================

    @classmethod
    def _validate_name(
        cls,
        name: str,
    ) -> None:

        if not name:
            raise ValueError(
                "Database routine name cannot be empty."
            )

        parts = name.split(".")

        if not all(
            cls._is_valid_identifier(part)
            for part in parts
        ):
            raise ValueError(
                f"Invalid database routine name: {name}"
            )

    # =========================================================
    # Validate Identifier
    # =========================================================

    @classmethod
    def _validate_identifier(
        cls,
        value: str,
    ) -> None:

        if not cls._is_valid_identifier(
            value
        ):
            raise ValueError(
                f"Invalid database identifier: {value}"
            )

    @staticmethod
    def _is_valid_identifier(
        value: str,
    ) -> bool:

        return bool(
            re.fullmatch(
                r"[A-Za-z_][A-Za-z0-9_]*",
                value,
            )
        )

    # =========================================================
    # Quote Cursor Identifier
    # =========================================================

    @staticmethod
    def _quote_identifier(
        value: str,
    ) -> str:

        escaped_value = value.replace(
            '"',
            '""',
        )

        return f'"{escaped_value}"'