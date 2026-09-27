import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class AuditLogBatchingSettings:
    batch_size: int = 100
    enable_periodic_flush: bool = True
    flush_interval_in_seconds: float = 5.0

    def __post_init__(self) -> None:
        if self.batch_size <= 0:
            raise ValueError("batch_size must be greater than 0.")
        if self.flush_interval_in_seconds <= 0:
            raise ValueError("flush_interval_in_seconds must be greater than 0.")


@dataclass(slots=True)
class AuditLogSettings:
    enabled: bool = True
    allowed_actions: list[str] = field(
        default_factory=lambda: ["Insert", "Update", "Delete"]
    )
    inclusion_mode: str = "Exclude"  # "Include" or "Exclude"
    tables: list[str] = field(
        default_factory=lambda: [
            "alembic_version",
            "audit_logs",
            "auditlogs",
            "logs",
            "__efmigrationshistory",
        ]
    )
    batching: AuditLogBatchingSettings = field(
        default_factory=AuditLogBatchingSettings
    )
    max_queue_size: int = 20_000

    # Internal cached normalized sets for O(1) lookups
    _always_excluded_tables: set[str] = field(
        default_factory=lambda: {
            "alembic_version",
            "audit_logs",
            "auditlogs",
            "__efmigrationshistory",
        },
        init=False,
    )
    _normalized_tables: set[str] = field(default_factory=set, init=False)
    _normalized_actions: set[str] = field(default_factory=set, init=False)

    def __post_init__(self) -> None:
        self._normalized_tables = {
            t.strip().lower() for t in self.tables if t.strip()
        }
        self._normalized_actions = {
            a.strip().upper() for a in self.allowed_actions if a.strip()
        }

    def is_action_allowed(self, action: str) -> bool:
        if not self.enabled:
            return False
        return action.strip().upper() in self._normalized_actions

    def is_table_audited(self, table_name: str) -> bool:
        if not self.enabled or not table_name:
            return False

        norm_name = table_name.strip().lower()

        # Always exclude system / audit tables to prevent infinite recursion
        if norm_name in self._always_excluded_tables:
            return False

        mode = self.inclusion_mode.strip().lower()
        if mode == "include":
            return norm_name in self._normalized_tables
        else:  # "exclude"
            return norm_name not in self._normalized_tables

    @classmethod
    def load_from_file_or_default(
        cls,
        file_path: str = "appsettings.json",
    ) -> "AuditLogSettings":
        path = Path(file_path)
        if not path.is_file():
            return cls()

        try:
            with open(path, "r", encoding="utf-8") as f:
                data: dict[str, Any] = json.load(f)

            settings_dict = data.get("AuditLogSettings")
            if not isinstance(settings_dict, dict):
                return cls()

            # Parse Batching
            batching_dict = settings_dict.get("Batching", {})
            batching = AuditLogBatchingSettings(
                batch_size=int(batching_dict.get("BatchSize", 100)),
                enable_periodic_flush=bool(
                    batching_dict.get("EnablePeriodicFlush", True)
                ),
                flush_interval_in_seconds=float(
                    batching_dict.get("FlushIntervalInSeconds", 5.0)
                ),
            )

            # Parse Root Settings
            enabled = bool(settings_dict.get("Enabled", True))
            allowed_actions = list(
                settings_dict.get(
                    "AllowedActions", ["Insert", "Update", "Delete"]
                )
            )
            inclusion_mode = str(
                settings_dict.get("InclusionMode", "Exclude")
            )
            tables = list(
                settings_dict.get(
                    "Tables",
                    [
                        "alembic_version",
                        "audit_logs",
                        "auditlogs",
                        "logs",
                        "__efmigrationshistory",
                    ],
                )
            )

            return cls(
                enabled=enabled,
                allowed_actions=allowed_actions,
                inclusion_mode=inclusion_mode,
                tables=tables,
                batching=batching,
            )

        except Exception:
            # Fall back to default settings on any parsing error
            return cls()
