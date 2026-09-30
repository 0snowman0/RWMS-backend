from datetime import date, datetime, timezone
from decimal import Decimal
from enum import Enum
from typing import Any
from uuid import UUID

from sqlalchemy import event, inspect
from sqlalchemy.orm import Session

from Configs.AuditLogs.audit_log_settings import AuditLogSettings
from Core.Application.Loggings.logging_context import LoggingContextAccessor
from Core.Domain.ViewModels.AuditLogs.audit_log_entry import AuditLogEntry
from Infrastructure.AuditLogs.async_audit_log_queue import AsyncAuditLogQueue


def _serialize_value(val: Any) -> Any:
    """
    سریالایزر ایمن برای تبدیل مقادیر ستون‌ها به انواع سازگار با JSON.
    """
    if val is None:
        return None
    if isinstance(val, (int, float, bool, str)):
        return val
    if isinstance(val, (datetime, date)):
        return val.isoformat()
    if isinstance(val, UUID):
        return str(val)
    if isinstance(val, Decimal):
        return float(val)
    if isinstance(val, Enum):
        return val.value
    if isinstance(val, dict):
        return {str(k): _serialize_value(v) for k, v in val.items()}
    if isinstance(val, (list, tuple, set)):
        return [_serialize_value(item) for item in val]
    return str(val)


def _extract_primary_key(obj: Any) -> dict[str, Any]:
    state = inspect(obj)
    pk_dict: dict[str, Any] = {}
    for col in state.mapper.primary_key:
        val = getattr(obj, col.name, None)
        pk_dict[col.name] = _serialize_value(val)
    return pk_dict


class AuditLogInterceptor:
    """
    اینترسپتور ثبت تغییرات پایگاه داده در سطح سشن‌های SQLAlchemy.
    کاملاً Decoupled و بدون تحمیل هیچ وابستگی به مدل‌های دامین.
    """

    def __init__(
        self,
        queue: AsyncAuditLogQueue,
        settings: AuditLogSettings,
    ) -> None:
        self._queue = queue
        self._settings = settings
        self._attached = False

    def attach(self) -> None:
        """
        اتصال رویدادهای چرخه حیات Session در SQLAlchemy.
        """
        if self._attached:
            return

        event.listen(Session, "before_flush", self._before_flush)
        event.listen(Session, "after_flush", self._after_flush)
        event.listen(Session, "after_commit", self._after_commit)
        event.listen(Session, "after_rollback", self._after_rollback)

        self._attached = True

    def _before_flush(self, session: Session, flush_context, instances) -> None:
        # خروج سریع در صورت غیرفعال بودن کلی سیستم یا عملیات داخلی خود ورکر
        if not self._settings.enabled or session.info.get("skip_audit"):
            return

        entries: list[dict[str, Any]] = session.info.setdefault(
            "pending_audit_entries", []
        )

        # =====================================================
        # ۱. رکوردهای جدید (Insert)
        # =====================================================
        if self._settings.is_action_allowed("Insert"):
            for obj in session.new:
                table_name = getattr(obj, "__tablename__", None)
                if not table_name or not self._settings.is_table_audited(table_name):
                    continue

                state = inspect(obj)
                new_vals = {
                    attr.key: _serialize_value(getattr(obj, attr.key, None))
                    for attr in state.mapper.column_attrs
                }

                entries.append({
                    "action": "Insert",
                    "table_name": table_name,
                    "obj": obj,
                    "old_values": None,
                    "new_values": new_vals,
                    "pk": None,  # پس از flush مقداردهی می‌شود
                })

        # =====================================================
        # ۲. رکوردهای ویرایش‌شده (Update)
        # =====================================================
        if self._settings.is_action_allowed("Update"):
            for obj in session.dirty:
                table_name = getattr(obj, "__tablename__", None)
                if not table_name or not self._settings.is_table_audited(table_name):
                    continue

                state = inspect(obj)
                old_vals: dict[str, Any] = {}
                new_vals: dict[str, Any] = {}

                for attr in state.mapper.column_attrs:
                    hist = state.get_history(attr.key, True)
                    if hist.has_changes():
                        old_val = hist.deleted[0] if hist.deleted else None
                        new_val = (
                            hist.added[0]
                            if hist.added
                            else getattr(obj, attr.key, None)
                        )
                        old_vals[attr.key] = _serialize_value(old_val)
                        new_vals[attr.key] = _serialize_value(new_val)

                # فقط در صورتی لاگ می‌شود که فیلدی تغییر کرده باشد
                if old_vals or new_vals:
                    pk = _extract_primary_key(obj)
                    entries.append({
                        "action": "Update",
                        "table_name": table_name,
                        "obj": None,
                        "old_values": old_vals,
                        "new_values": new_vals,
                        "pk": pk,
                    })

        # =====================================================
        # ۳. رکوردهای حذف‌شده (Delete)
        # =====================================================
        if self._settings.is_action_allowed("Delete"):
            for obj in session.deleted:
                table_name = getattr(obj, "__tablename__", None)
                if not table_name or not self._settings.is_table_audited(table_name):
                    continue

                state = inspect(obj)
                old_vals = {
                    attr.key: _serialize_value(getattr(obj, attr.key, None))
                    for attr in state.mapper.column_attrs
                }
                pk = _extract_primary_key(obj)

                entries.append({
                    "action": "Delete",
                    "table_name": table_name,
                    "obj": None,
                    "old_values": old_vals,
                    "new_values": None,
                    "pk": pk,
                })

    def _after_flush(self, session: Session, flush_context) -> None:
        if not self._settings.enabled or session.info.get("skip_audit"):
            return

        entries: list[dict[str, Any]] = session.info.get(
            "pending_audit_entries", []
        )

        for entry in entries:
            # استخراج شناسه برای رکوردهای درج شده پس از ایجاد توسط دیتابیس
            if entry["action"] == "Insert" and entry.get("obj") is not None:
                obj = entry["obj"]
                pk = _extract_primary_key(obj)
                entry["pk"] = pk

                # به‌روزرسانی مقادیر تولیدشده پس از فلاش (مانند id, created_at, updated_at)
                if entry["new_values"] is not None:
                    state = inspect(obj)
                    for attr in state.mapper.column_attrs:
                        if entry["new_values"].get(attr.key) is None:
                            val = getattr(obj, attr.key, None)
                            if val is not None:
                                entry["new_values"][attr.key] = _serialize_value(val)

                # پاک‌سازی ارجاع به آبجکت ORM جهت آزادسازی حافظه
                entry["obj"] = None

    def _after_commit(self, session: Session) -> None:
        entries: list[dict[str, Any]] = session.info.pop(
            "pending_audit_entries", []
        )

        if not entries or not self._settings.enabled:
            return

        # دریافت شناسه کاربر از کانتکست درخواست جاری
        context = LoggingContextAccessor.get()
        user_id = context.user_id if context else None
        now_utc = datetime.now(timezone.utc)

        for e in entries:
            pk = e["pk"] or {}
            entry = AuditLogEntry(
                table_name=e["table_name"],
                action=e["action"],
                primary_key=pk,
                old_values=e["old_values"],
                new_values=e["new_values"],
                user_id=user_id,
                created_at=now_utc,
            )
            self._queue.enqueue(entry)

    def _after_rollback(self, session: Session) -> None:
        # در صورت رول‌بک، هیچ لاگی نباید به صف منتقل شود
        session.info.pop("pending_audit_entries", None)
