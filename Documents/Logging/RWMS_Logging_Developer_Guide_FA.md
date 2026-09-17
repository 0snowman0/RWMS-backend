**راهنمای استفاده از سیستم Logging**

**RWMS Developer Guide**

| **هدف**        | استفاده عملی از Logger، تنظیمات، Context، Mediator و Fallback |
| -------------- | ------------------------------------------------------------- |
| **مخاطب**      | برنامه‌نویس Backend پروژه RWMS                                |
| **ذخیره‌سازی** | PostgreSQL با Batch Writer و Session مستقل                    |
| **نسخه مستند** | Logging Infrastructure - September 2026                       |

این سند برای استفاده سریع در پروژه نوشته شده است؛ تمرکز آن روی «چطور استفاده کنم؟» و «کدام تنظیم چه اثری دارد؟» است، نه جزئیات پیاده‌سازی داخلی.

**۱. شروع سریع**

برای استفاده از Logger در Handler، Service یا Behavior فقط ILogger را در سازنده دریافت کنید. ثبت در Mediator به‌صورت خودکار توسط سیستم DI انجام می‌شود.

```
from Core.Application.Contracts.Loggings.logger import ILogger

class SampleHandler:
    def __init__(self, logger: ILogger):
        self._logger = logger
```

**نکته** برای سرویس‌هایی که باید داخل Handler یا Behavior قابل Resolve باشند، ثبت @mediator_service(...) انجام می‌شود؛ نیازی به resolver.add(...) دستی نیست.

**۲. ثبت لاگ‌ها**

**INFO - عملیات عادی**

```
self._logger.info(
    "User created successfully.",
    properties={
        "email": user.email,
        "user_id": user.id,
    },
)
```

**DEBUG - جزئیات توسعه و بررسی**

```
self._logger.debug(
    "User DTO mapped to entity."
)
```

اگر minimum_level روی INFO یا بالاتر باشد، DEBUG اصلاً وارد Queue نمی‌شود.

**WARNING / ERROR / CRITICAL**

```
self._logger.warning("User has no active role.")

self._logger.error(
    "User creation failed.",
    exception=ex,
)

self._logger.critical(
    "Critical application failure.",
    exception=ex,
)
```

**EXCEPTION - همراه با Stack Trace**

```
try:
    ...
except Exception as ex:
    self._logger.exception(
        message="Create user failed.",
        exception=ex,
        properties={"email": request.data.email},
    )
    raise
```

**۳. Properties؛ اطلاعات اضافی ساخت‌یافته**

اطلاعات متغیر و قابل جست‌وجو را در properties قرار دهید. این داده‌ها در PostgreSQL داخل ستون JSONB ذخیره می‌شوند.

```
self._logger.info(
    "Order processed.",
    properties={
        "order_id": order.id,
        "amount": order.total,
        "source": "api",
    },
)
```

**قاعده پیشنهادی** Message کوتاه و ثابت باشد؛ جزئیات متغیر مثل id، email، amount و ... داخل properties قرار بگیرند.

**۴. Logging در Mediator**

LoggingBehavior ورودی، خروجی و Exception کل Pipeline را ثبت می‌کند. بنابراین معمولاً لازم نیست ورود و خروج Handler را دوباره دستی Log کنید.

| **تنظیم / مورد**       | **کاربرد و رفتار**                                                                  |
| ---------------------- | ----------------------------------------------------------------------------------- |
| **Mediator Request**   | قبل از اجرای Pipeline ثبت می‌شود.                                                   |
| **Mediator Response**  | بعد از اجرای موفق Handler و Behaviorهای داخلی ثبت می‌شود.                           |
| **Mediator Exception** | اگر هر بخش Pipeline - از جمله Commit در TransactionBehavior - خطا بدهد، ثبت می‌شود. |

```
@behavior(BehaviorType.LOGGING)
class LoggingBehavior(IPipelineBehavior):
    def __init__(self, logger: ILogger):
        self._logger = logger

    async def handle(self, request, next_handler):
        ...
```

**مزیت مهم** اگر Commit در TransactionBehavior خطا بدهد، Handler ممکن است قبلاً تمام شده باشد؛ LoggingBehavior بیرونی همچنان Exception را ثبت می‌کند.

**۵. Request ID و Correlation ID**

برای هر HTTP Request یک request_id ساخته می‌شود. correlation_id برای مرتبط‌کردن Logهای یک جریان استفاده می‌شود. اگر Header خارجی X-Correlation-ID وجود نداشته باشد، correlation_id برابر request_id در نظر گرفته می‌شود.

| **تنظیم / مورد**     | **کاربرد و رفتار**                                                                |
| -------------------- | --------------------------------------------------------------------------------- |
| **request_id**       | شناسه یکتای همین HTTP Request.                                                    |
| **correlation_id**   | شناسه مشترک برای دنبال‌کردن عملیات مرتبط؛ در سناریوهای بین‌سرویسی قابل ادامه است. |
| **X-Request-ID**     | در Response Header برگردانده می‌شود.                                              |
| **X-Correlation-ID** | در Response Header برگردانده می‌شود و می‌تواند از Request ورودی خوانده شود.       |

نمونه جست‌وجوی تمام Logهای یک درخواست:

```
SELECT *
FROM logs
WHERE correlation_id = '...';
```

**۶. اطلاعات Context که خودکار ثبت می‌شوند**

| **تنظیم / مورد**                | **کاربرد و رفتار**                                                |
| ------------------------------- | ----------------------------------------------------------------- |
| **request_id / correlation_id** | از LoggingContextMiddleware                                       |
| **ip_address**                  | از Request client                                                 |
| **user_id**                     | بعد از اتصال Authentication به Context؛ فعلاً ممکن است NULL باشد. |
| **http_method**                 | مثل GET / POST / PUT                                              |
| **path**                        | مسیر Endpoint                                                     |
| **status_code**                 | فقط وقتی در لحظه ثبت Log، Response Status مشخص شده باشد.          |

**چرا status_code داخل Handler ممکن است NULL باشد؟** چون Handler قبل از ساخته‌شدن HTTP Response اجرا می‌شود. Status نهایی بعداً در Middleware مشخص می‌شود.

**۷. تنظیمات Logging**

فایل تنظیمات: Configs/Loggings/logging_settings.py

```
LoggingSettings(
    enabled=True,
    minimum_level=LogLevel.INFO,
    database_enabled=True,
    console_enabled=False,
    batch_size=50,
    flush_interval_seconds=5.0,
    max_queue_size=10_000,
    include_request_context=True,
    include_user_context=True,
    include_stack_trace=True,
    fallback_to_file=True,
    fallback_file_path="logs/logging-fallback.log",
)
```

| **تنظیم / مورد**            | **کاربرد و رفتار**                                                 |
| --------------------------- | ------------------------------------------------------------------ |
| **enabled**                 | روشن/خاموش‌کردن کل Logging. اگر False باشد Log وارد Queue نمی‌شود. |
| **minimum_level**           | حداقل Level قابل ثبت.                                              |
| **database_enabled**        | فعال/غیرفعال‌کردن مسیر PostgreSQL.                                 |
| **console_enabled**         | نمایش همزمان Logها در Console؛ نقش Backup ندارد.                   |
| **batch_size**              | تعداد Logهایی که با هم ذخیره می‌شوند.                              |
| **flush_interval_seconds**  | حداکثر زمان انتظار برای Flush؛ مقدار None یعنی Timer غیرفعال.      |
| **max_queue_size**          | حداکثر ظرفیت Queue برای کنترل مصرف حافظه.                          |
| **include_request_context** | ثبت خودکار Request ID، IP، Method، Path و Status.                  |
| **include_user_context**    | ثبت User ID در صورت موجود بودن.                                    |
| **include_stack_trace**     | ثبت Stack Trace برای Exceptionها.                                  |
| **fallback_to_file**        | در خطای PostgreSQL، Log در فایل پشتیبان ذخیره شود.                 |
| **fallback_file_path**      | مسیر فایل JSONL پشتیبان.                                           |

**۸. Levelها و minimum_level**

| **تنظیم / مورد**  | **کاربرد و رفتار**            |
| ----------------- | ----------------------------- |
| **DEBUG = 10**    | جزئیات توسعه و عیب‌یابی.      |
| **INFO = 20**     | رویدادهای عادی و مهم.         |
| **WARNING = 30**  | وضعیت غیرعادی اما قابل ادامه. |
| **ERROR = 40**    | خطای عملیاتی.                 |
| **CRITICAL = 50** | خطای بسیار جدی و سطح بالا.    |

مثال: اگر minimum_level = LogLevel.WARNING باشد، DEBUG و INFO اصلاً وارد Queue نمی‌شوند.

**۹. Batch و Flush**

Logging به‌صورت Async و Batch انجام می‌شود تا Request اصلی منتظر ذخیره هر Log نماند.

| **تنظیم / مورد**                  | **کاربرد و رفتار**                                                        |
| --------------------------------- | ------------------------------------------------------------------------- |
| **batch_size = 50**               | به محض جمع‌شدن ۵۰ Log، Batch ذخیره می‌شود.                                |
| **flush_interval_seconds = 5.0**  | اگر Batch کامل نشود، Logهای موجود بعد از ۵ ثانیه Flush می‌شوند.           |
| **flush_interval_seconds = None** | Flush زمانی کاملاً غیرفعال؛ فقط Batch Size یا Shutdown باعث Flush می‌شود. |
| **Shutdown**                      | Logهای باقی‌مانده Queue قبل از توقف Worker Flush می‌شوند.                 |

**مثال عملی** اگر batch_size=50 و flush_interval_seconds=5 باشد و فقط 7 Log برسد، حدود 5 ثانیه بعد همان 7 Log ذخیره می‌شوند.

**۱۰. Fallback به فایل**

اگر PostgreSQL نتواند Batch را ذخیره کند، Worker همان Batch را به FileLogFallbackWriter تحویل می‌دهد. فایل پشتیبان به صورت JSON Lines ذخیره می‌شود؛ هر خط یک Log مستقل است.

```
{"timestamp":"...","level":"ERROR","message":"Database error","request_id":"..."}
```

| **تنظیم / مورد**      | **کاربرد و رفتار**                                |
| --------------------- | ------------------------------------------------- |
| **PostgreSQL موفق**   | Log در جدول logs ذخیره می‌شود.                    |
| **PostgreSQL ناموفق** | Log در logs/logging-fallback.log نوشته می‌شود.    |
| **Queue Full**        | Log می‌تواند مستقیماً به Fallback File منتقل شود. |

**۱۱. استقلال Logging از Transaction اصلی**

Logging از Session مستقل استفاده می‌کند. بنابراین Rollback شدن Transaction اصلی Business باعث Rollback شدن Log نمی‌شود.

```
Business Session
    -> ROLLBACK

Logging Session
    -> COMMIT
```

این رفتار برای ثبت خطاهای واقعی حیاتی است؛ مخصوصاً خطاهایی که هنگام commit() رخ می‌دهند.

**سناریوی واقعی** Handler عملیات را انجام می‌دهد، TransactionBehavior روی commit با UniqueViolationError مواجه می‌شود، Business Rollback می‌شود؛ اما Mediator Exception همچنان با Session مستقل Logger ثبت می‌شود.

**۱۲. Lifecycle Worker**

LogWorker همراه lifespan برنامه Start و Stop می‌شود.

```
@asynccontextmanager
async def application_lifespan(app: FastAPI):
    await app.state.log_worker.start()
    try:
        yield
    finally:
        await app.state.log_worker.stop()
```

در Shutdown، Worker ابتدا Queue باقی‌مانده را پردازش می‌کند و سپس متوقف می‌شود.

**۱۳. چه چیزهایی را Log نکنیم؟**

Logging نباید باعث نشت اطلاعات حساس شود. این موارد را داخل message یا properties ثبت نکنید:

• Password و Password Hash

• Access Token و Refresh Token

• Authorization Header

• Cookie / Session Secret

• Secret Key و Connection String

• اطلاعات حساس شخصی که برای Debug لازم نیست

**برای توسعه بعدی** بهتر است Sensitive Data Redaction به Logger یا LoggingBehavior اضافه شود تا فیلدهای شناخته‌شده به‌صورت خودکار Mask شوند.

**۱۴. الگوی پیشنهادی استفاده در Handler**

```
class CreateUserCommandHandler(...):
    def __init__(
        self,
        uow: IUnitOfWork,
        mapper: IMapper,
        logger: ILogger,
    ):
        self._uow = uow
        self._mapper = mapper
        self._logger = logger

    async def handle(self, request):
        self._logger.info(
            "User creation started.",
            properties={"email": request.data.email},
        )

        user = self._mapper.map(request.data, User)
        await self._uow.users.add(user)

        return BaseResponse.success(data=user)
```

**توصیه** ورود/خروج کلی Pipeline را LoggingBehavior ثبت می‌کند. داخل Handler فقط نقاط مهم Business را Log کنید.

**۱۵. Quick Reference**

| **تنظیم / مورد**          | **کاربرد و رفتار**                            |
| ------------------------- | --------------------------------------------- |
| **لاگ عادی**              | logger.info("...")                            |
| **لاگ توسعه‌ای**          | logger.debug("...")                           |
| **هشدار**                 | logger.warning("...")                         |
| **خطا**                   | logger.error("...", exception=ex)             |
| **Exception کامل**        | logger.exception(message="...", exception=ex) |
| **اطلاعات اضافی**         | properties={...}                              |
| **خاموش‌کردن کل Logging** | enabled=False                                 |
| **غیرفعال‌کردن Timer**    | flush_interval_seconds=None                   |
| **فقط Warning به بالا**   | minimum_level=LogLevel.WARNING                |
| **قطع Console**           | console_enabled=False                         |
| **Fallback فایل**         | fallback_to_file=True                         |

**۱۶. جریان کلی سیستم**

```
ILogger
   ↓
ApplicationLogger
   ↓
LogEntry + Request Context
   ↓
AsyncLogQueue
   ↓
LogWorker
   ↓
Batch Writer
   ↓
PostgreSQL
   └── Failure → Fallback File
```

**نتیجه: مسیر Logging از Transaction اصلی جداست، Request را Block نمی‌کند، Batch و Timer دارد، Context درخواست را خودکار حمل می‌کند و در خطای دیتابیس Log را از دست نمی‌دهد.**

**۱۷. مسیر فایل‌های مهم**

| **تنظیم / مورد**          | **کاربرد و رفتار**                                   |
| ------------------------- | ---------------------------------------------------- |
| **LoggingSettings**       | Configs/Loggings/logging_settings.py                 |
| **ILogger**               | Core/Application/Contracts/Loggings/logger.py        |
| **LogEntry**              | Core/Domain/ViewModels/Loggings/log_entry.py         |
| **LoggingContext**        | Core/Application/Loggings/logging_context.py         |
| **ApplicationLogger**     | Infrastructure/Loggings/application_logger.py        |
| **AsyncLogQueue**         | Infrastructure/Loggings/async_log_queue.py           |
| **LogWorker**             | Infrastructure/Loggings/log_worker.py                |
| **Fallback Writer**       | Infrastructure/Loggings/file_log_fallback_writer.py  |
| **Postgres Batch Writer** | Infrastructure/Loggings/postgres_log_batch_writer.py |

**۱۸. چک‌لیست سریع**

• برای Log در Handler یا Behavior فقط ILogger را Inject کنید.

• برای Exception از logger.exception(...) استفاده کنید تا Stack Trace ثبت شود.

• اطلاعات متغیر را در properties نگه دارید.

• Password، Token، Cookie و Secretها را Log نکنید.

• برای خاموش‌کردن Timer مقدار flush_interval_seconds را None قرار دهید.

• در Production سطح minimum_level و batch_size را متناسب با حجم Log تنظیم کنید.