

from Core.Domain.Enums.Mediators.mediator import BehaviorType, RequestType

# هشدار اهمیت ترتیب اجرای بهویر ها مهم هست و به ترتیب نوشته شده میباشد
# در صورت اضافه شدن یا کم شدن بیهویر جدید به ترتیب آن دقت کنید
MEDIATOR_BEHAVIOR_POLICIES: dict[
    RequestType,
    tuple[BehaviorType, ...],
] = {

    RequestType.COMMAND: (
        BehaviorType.LOGGING,
        BehaviorType.PERFORMANCE,
        BehaviorType.VALIDATION,
        BehaviorType.TRANSACTION,
    ),

    RequestType.QUERY: (
        BehaviorType.LOGGING,
        BehaviorType.PERFORMANCE,
        BehaviorType.VALIDATION,
    ),
}