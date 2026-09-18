from enum import Enum


class QualityStatus(str, Enum):
    GOOD = "good"
    DAMAGED = "damaged"
    EXPIRED = "expired"
