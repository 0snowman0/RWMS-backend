**راهنمای استفاده از  
Global Exception Handler**  
<br/>FastAPI • BaseResponse • ILogger • HTTP 500

**هدف این مستند**

این راهنما برای استفاده عملی از Exception Handler سراسری پروژه نوشته شده است؛ یعنی خطاهایی که در کد محلی کنترل نشده‌اند، به‌صورت یک پاسخ استاندارد BaseResponse به Client برگردند و هم‌زمان با ILogger ثبت شوند.

**محدوده — محدوده نسخه فعلی  
**این مستند وارد Validation، Business Exceptionهای اختصاصی، NotFound/Conflict سفارشی یا Ruleهای آینده نمی‌شود. تمرکز فقط روی Unhandled Exception عمومی است.

**خلاصه رفتار**

| **اگر خطا را خودت کنترل کنی** | **اگر خطا کنترل نشود**      |
| ----------------------------- | --------------------------- |
| try / except محلی             | Global Exception Handler    |
| پاسخ دلخواه خودت              | ثبت Log + ساخت BaseResponse |
| Global Handler دخالت نمی‌کند  | HTTP 500 تمیز و استاندارد   |

**۱. جریان کلی Exception Handling**

درخواست وارد برنامه می‌شود و تا زمانی که Exception داخل همان نقطه با try/except مصرف نشده باشد، خطا به Handler سراسری می‌رسد.

| **مرحله**                      | **رفتار**                        |
| ------------------------------ | -------------------------------- |
| Controller / Handler / Service | کد اصلی اجرا می‌شود              |
| Exception کنترل‌شده            | خودت در except تصمیم می‌گیری     |
| Exception کنترل‌نشده           | به GlobalExceptionHandler می‌رسد |
| GlobalExceptionHandler         | Log + BaseResponse + HTTP Status |

**۲. رفتار try / except محلی**

اگر Exception را بگیری و دیگر raise نکنی، Handler سراسری آن Exception را نمی‌بیند.

**کنترل کامل خطا در همان نقطه**

```
try:
    ...
except Exception as ex:
    # کنترل محلی
    return my_response
```

اگر بعد از کنترل یا ثبت موردی دوباره raise کنی، Exception به Global Handler می‌رسد.

**ارسال مجدد خطا به Handler سراسری**

```
try:
    ...
except Exception as ex:
    ...
    raise
```

**نکته — قاعده استفاده  
**Global Exception Handler جای try/exceptهای هدفمند را نمی‌گیرد. هرجا واقعاً می‌خواهی رفتار خاصی داشته باشی، همان‌جا کنترل کن؛ بقیه خطاهای پیش‌بینی‌نشده به Handler سراسری سپرده می‌شوند.

**۳. نمونه پاسخ Client**

```
{
  "is_success": false,
  "message": "An unexpected error occurred.",
  "errors": [
    "Internal server error."
  ],
  "data": null,
  "status": "internal_server_error"
}
```

**۴. تنظیمات Exception Handler**

تنظیمات در فایل زیر قرار دارند و رفتار عمومی Handler را کنترل می‌کنند:

```
Configs/ExceptionHandlers/exception_handler_settings.py
```

<div class="joplin-table-wrapper"><table><tbody><tr><th><p><strong>تنظیم</strong></p></th><th><p><strong>پیش‌فرض</strong></p></th><th><p><strong>نوع</strong></p></th><th><p><strong>کاربرد</strong></p></th></tr><tr><td><pre><code><strong>enabled</strong></code></pre></td><td><pre><code>True</code></pre></td><td><pre><code>bool</code></pre></td><td><p>فعال یا غیرفعال کردن Handler سراسری.</p></td></tr><tr><td><pre><code><strong>log_exceptions</strong></code></pre></td><td><pre><code>True</code></pre></td><td><pre><code>bool</code></pre></td><td><p>مشخص می‌کند Exceptionهای کنترل‌نشده توسط ILogger ثبت شوند یا نه.</p></td></tr><tr><td><pre><code><strong>include_exception_message_in_response</strong></code></pre></td><td><pre><code>False</code></pre></td><td><pre><code>bool</code></pre></td><td><p>اگر True باشد متن واقعی Exception در پاسخ Client قرار می‌گیرد.</p></td></tr><tr><td><pre><code><strong>default_message</strong></code></pre></td><td><pre><code>An unexpected...</code></pre></td><td><pre><code>str</code></pre></td><td><p>پیام عمومی و امن برای Client.</p></td></tr><tr><td><pre><code><strong>default_error_message</strong></code></pre></td><td><pre><code>Internal server error.</code></pre></td><td><pre><code>str</code></pre></td><td><p>متن پیش‌فرض داخل آرایه errors.</p></td></tr><tr><td><pre><code><strong>default_status_code</strong></code></pre></td><td><pre><code>500</code></pre></td><td><pre><code>int</code></pre></td><td><p>HTTP Status پیش‌فرض برای خطاهای کنترل‌نشده.</p></td></tr></tbody></table></div>

**۵. تنظیم پیشنهادی Production**

```
ExceptionHandlerSettings(
    enabled=True,
    log_exceptions=True,
    include_exception_message_in_response=False,
    default_status_code=500,
)
```

**امنیت — چرا متن واقعی Exception را نمایش ندهیم؟  
**Exception واقعی ممکن است شامل نام جدول، مسیر فایل، Query، Constraint، جزئیات دیتابیس یا اطلاعات داخلی برنامه باشد. در Production بهتر است این اطلاعات فقط در Log ذخیره شوند.

**۶. تنظیم پیشنهادی Development**

```
ExceptionHandlerSettings(
    enabled=True,
    log_exceptions=True,
    include_exception_message_in_response=True,
)
```

این حالت برای Debug مفید است چون متن واقعی Exception را در errors می‌بینی.

**۷. ارتباط با BaseResponse**

برای اینکه خطاهای سراسری هم دقیقاً با فرمت پاسخ‌های بقیه پروژه هماهنگ باشند، یک وضعیت و متد مخصوص خطای داخلی داریم.

**ResponseStatus**

```
class ResponseStatus(str, Enum):
    ...
    INTERNAL_SERVER_ERROR = "internal_server_error"
```

**BaseResponse.internal_server_error**

```
@classmethod
def internal_server_error(
    cls,
    message: str | None = None,
    errors: list[str] | None = None,
) -> "BaseResponse[T]":

    return cls(
        is_success=False,
        message=message,
        errors=errors or [],
        data=None,
        status=ResponseStatus.INTERNAL_SERVER_ERROR,
    )
```

**۸. کار GlobalExceptionHandler**

Handler سراسری چهار مسئولیت اصلی دارد:

• ثبت Status Code در LoggingContext برای همان Request.

• ثبت Exception کامل با ILogger در صورت فعال بودن log_exceptions.

• انتخاب متن امن یا متن واقعی Exception بر اساس Settings.

• ساخت BaseResponse و برگرداندن JSONResponse با HTTP Status مناسب.

**بخش اصلی پاسخ**

```
result = BaseResponse.internal_server_error(
    message=settings.default_message,
    errors=errors,
)

return JSONResponse(
    status_code=settings.default_status_code,
    content=jsonable_encoder(
        result.model_dump(mode="python")
    ),
)
```

**پایداری — Fail-safe Logging  
**اگر خود Logging هنگام ثبت Exception خطا بدهد، Exception Handler نباید دوباره خراب شود. به همین دلیل خطای Logger داخل Handler مصرف می‌شود و پاسخ 500 همچنان به Client برمی‌گردد.

**۹. Logging خطاها**

برای Exception کنترل‌نشده، Handler از ILogger پروژه استفاده می‌کند. در نتیجه همان زیرساخت Logging قبلی فعال است: Queue، Batch Writer، PostgreSQL و File Fallback.

```
logger.exception(
    message="Unhandled application exception.",
    exception=exception,
    properties={
        "exception_type": type(exception).__name__,
        "http_method": request.method,
        "path": request.url.path,
    },
)
```

در Log علاوه بر message و properties، اطلاعات Context نیز به‌صورت خودکار می‌آیند:

• request_id و correlation_id

• IP، HTTP Method و Path

• Exception Type، Exception Message و Stack Trace

• user_id بعد از اتصال Authentication به LoggingContext

**مزیت — Transaction مستقل  
**اگر Transaction اصلی Business Rollback شود، Log Exception همچنان با Session مستقل Logging قابل ذخیره است. اگر PostgreSQL Logging هم در دسترس نباشد، File Fallback وارد عمل می‌شود.

**۱۰. ثبت Handler در FastAPI**

**configure_exception_handlers(app)**

```
def configure_exception_handlers(
    app: FastAPI,
) -> None:

    settings = ExceptionHandlerSettings()

    handler = GlobalExceptionHandler(
        settings=settings,
    )

    if not settings.enabled:
        return

    app.add_exception_handler(
        Exception,
        handler.handle,
    )
```

در main.py فقط Configure مرکزی صدا زده می‌شود تا main شلوغ نشود:

```
configure_logging(app)
configure_rate_limiting(app)
configure_mediator(app)
configure_middlewares(app)
configure_exception_handlers(app)
setup_api(app)
```

**۱۱. نکته مهم درباره LoggingBehavior**

اگر LoggingBehavior هم Exception را Log کند و GlobalExceptionHandler نیز همان Exception را Log کند، یک خطا ممکن است دوبار در جدول logs ثبت شود.

| **LoggingBehavior** | **GlobalExceptionHandler** |
| ------------------- | -------------------------- |
| Request / Response  | Unhandled Exception        |
| لاگ جریان Mediator  | لاگ نهایی خطای کنترل‌نشده  |

**پیشنهاد — پیشنهاد معماری  
**بعد از اطمینان از Global Exception Handler، بهتر است مسئولیت لاگ Exception نهایی فقط در Global Handler باشد و LoggingBehavior روی Request/Response متمرکز بماند.

**۱۲. تست پیشنهادی**

یک سناریوی ساده برای تست، ارسال Email تکراری به CreateUser است؛ Constraint دیتابیس Exception ایجاد می‌کند و TransactionBehavior هنگام Commit خطا می‌گیرد.

| **انتظار**           | **نتیجه**                                |
| -------------------- | ---------------------------------------- |
| Business Transaction | Rollback                                 |
| Client Response      | BaseResponse با HTTP 500                 |
| Logging              | Exception کامل ثبت شود                   |
| Stack Trace          | داخل Log ذخیره شود                       |
| برنامه               | Crash نکند و Request مدیریت‌شده تمام شود |

**۱۳. تفاوت Production و Development**

| **Production**                  | **Development**                        |
| ------------------------------- | -------------------------------------- |
| متن عمومی برای Client           | نمایش متن واقعی Exception در صورت نیاز |
| include_exception_message=False | include_exception_message=True         |
| جزئیات کامل فقط در Log          | جزئیات در Log و Response               |

**۱۴. مسیر فایل‌های اصلی**

<div class="joplin-table-wrapper"><table><tbody><tr><th><p><strong>بخش</strong></p></th><th><p><strong>مسیر</strong></p></th></tr><tr><td><p><strong>Settings</strong></p></td><td><pre><code>Configs/ExceptionHandlers/exception_handler_settings.py</code></pre></td></tr><tr><td><p><strong>Global Handler</strong></p></td><td><pre><code>Api/ExceptionHandlers/global_exception_handler.py</code></pre></td></tr><tr><td><p><strong>Registration</strong></p></td><td><pre><code>Configs/ExceptionHandlers/exception_handler_config.py</code></pre></td></tr><tr><td><p><strong>BaseResponse</strong></p></td><td><pre><code>Core/Application/Commons/base_response.py</code></pre></td></tr><tr><td><p><strong>Logger Contract</strong></p></td><td><pre><code>Core/Application/Contracts/Loggings/logger.py</code></pre></td></tr></tbody></table></div>

**۱۵. Quick Reference**

```
# کنترل محلی
try:
    ...
except Exception as ex:
    return my_response

# ارسال به Global Handler
try:
    ...
except Exception as ex:
    raise

# Production
include_exception_message_in_response = False

# Development
include_exception_message_in_response = True
```

**۱۶. چک‌لیست استفاده**

• ☐ ExceptionHandlerSettings فعال باشد.

• ☐ configure_exception_handlers(app) در startup configuration فراخوانی شده باشد.

• ☐ ILogger قبل از Exception Handler پیکربندی شده باشد.

• ☐ در Production متن واقعی Exception به Client نمایش داده نشود.

• ☐ برای Exceptionهای هدفمند همچنان از try/except محلی استفاده شود.

• ☐ برای جلوگیری از Log تکراری، مسئولیت LoggingBehavior و Global Handler مشخص باشد.

• ☐ یک تست واقعی 500 انجام شود و هم Response و هم جدول logs بررسی شوند.

**جمع‌بندی — خلاصه نهایی  
**Global Exception Handler یک Safety Net برای خطاهای کنترل‌نشده است: برنامه به‌جای خروجی خام یا Crash، یک BaseResponse استاندارد می‌دهد و خطای کامل برای بررسی فنی Log می‌شود.