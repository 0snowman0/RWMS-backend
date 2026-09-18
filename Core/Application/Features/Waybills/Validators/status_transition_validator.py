from Core.Domain.Enums.Waybills.waybill_status import (
    WaybillStatus,
)


# =========================================================
# Valid Status Transitions
# =========================================================
#
# REGISTERED ──► PENDING_APPROVAL ──► APPROVED ──► RECEIVING
#      │                  │                            │
#      │                  │              ┌─────────────┤
#      ▼                  ▼              ▼             ▼
#  CANCELLED          CANCELLED    RECEIVED    PARTIALLY_RECEIVED
#                                                      │
#                                              ┌───────┤
#                                              ▼       ▼
#                                          RECEIVING  RECEIVED

VALID_TRANSITIONS: dict[
    WaybillStatus,
    list[WaybillStatus],
] = {
    WaybillStatus.REGISTERED: [
        WaybillStatus.PENDING_APPROVAL,
        WaybillStatus.CANCELLED,
    ],
    WaybillStatus.PENDING_APPROVAL: [
        WaybillStatus.APPROVED,
        WaybillStatus.CANCELLED,
    ],
    WaybillStatus.APPROVED: [
        WaybillStatus.RECEIVING,
        WaybillStatus.CANCELLED,
    ],
    WaybillStatus.RECEIVING: [
        WaybillStatus.RECEIVED,
        WaybillStatus.PARTIALLY_RECEIVED,
    ],
    WaybillStatus.PARTIALLY_RECEIVED: [
        WaybillStatus.RECEIVING,
        WaybillStatus.RECEIVED,
    ],
    WaybillStatus.RECEIVED: [],
    WaybillStatus.CANCELLED: [],
}


def is_valid_transition(
    current: str,
    target: str,
) -> bool:
    """Check if a status transition is allowed."""
    try:
        current_status = WaybillStatus(current)
        target_status = WaybillStatus(target)
    except ValueError:
        return False

    return target_status in VALID_TRANSITIONS.get(
        current_status, []
    )
