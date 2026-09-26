from enum import Enum


class WaybillStatus(str, Enum):
    REGISTERED = "registered"
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    RECEIVING = "receiving"
    RECEIVED = "received"
    PARTIALLY_RECEIVED = "partially_received"
    CANCELLED = "cancelled"
