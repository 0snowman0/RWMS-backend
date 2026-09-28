**راهنمای استفاده و پیکربندی سیستم Audit Log در پروژه RWMS**

**RWMS Developer Guide**

| **هدف**        | راهنمای عملیاتی استفاده، پیکربندی، کوئری‌گیری و نکات معماری سیستم ممیزی دیتابیس (Audit Log) |
| -------------- | ------------------------------------------------------------------------------------------- |
| **مخاطب**      | توسعه‌دهندگان Backend پروژه RWMS                                                            |
| **ذخیره‌سازی** | جدول `audit_logs` در PostgreSQL (با صف درون‌حافظه‌ای ناهمگام و کارگر پس‌زمینه)             |
| **نسخه مستند** | Database Audit Logging Infrastructure - September 2026                                      |

این مستند نحوه عملکرد، تنظیمات، استفاده روزمره، کوئری‌گیری و نکات توسعه سیستم **Audit Logging** در بک‌اند پروژه را توضیح می‌دهد.

---

### ۱. مقدمه و تفاوت با Application Logging

سیستم لاگینگ پروژه به دو بخش کاملاً مجزا تفکیک شده است:

1. **سیستم Application Logger (`Log`)**:
   - برای ثبت رخدادهای عمومی اپلیکیشن، درخواست‌های HTTP، هشدارها و خطاهای سیستمی (`INFO`, `WARNING`, `ERROR`, `EXCEPTION`).
   - از طریق اینترفیس `ILogger` فراخوانی می‌شود.
2. **سیستم Database Audit Logger (`AuditLog`)**:
   - برای **ممیزی تغییرات داده‌های پایگاه‌داده** در سطح جداول (`Insert`, `Update`, `Delete`).
   - مقادیر قبل (`old_values`)، مقادیر بعد (`new_values`)، شناسه رکورد (`primary_key`) و کاربر انجام‌دهنده (`user_id`) را در ستون‌های ساخت‌یافته `JSONB` ذخیره می‌کند.
   - **کاملاً خودکار و مستقل (Decoupled)** است و برای ثبت وقایع آن، برنامه‌نویس نیازی به فراخوانی متد لاگر ندارد.

---

### ۲. نحوه استفاده روزمره در کدنویسی (توسعه‌دهنده چه باید بکند؟)

پاسخ کوتاه: **هیچ کاری! سیستم ۱۰۰٪ خودکار است.**

به لطف معماری Decoupled و غیرمزاحم (Non-Intrusive):
- **هیچ اتریبیوت یا دکوراتوری** روی مدل‌های دامین (مانند `Category`, `Product`, `Waybill`, `User`) قرار داده نمی‌شود.
- مدل‌ها از هیچ کلاس پایه خاصی ارث‌بری نمی‌کنند.
- هر زمان در یک Command Handler یا کنترلر متد `await uow.save_changes()` (یا `await session.commit()`) فراخوانی شود، تغییرات به شکل خودکار استخراج شده و بعد از تأیید قطعی تراکنش کاربر، در پس‌زمینه ثبت می‌گردند.

#### مثال در یک Command Handler معمولی:
```python
@handler_for(UpdateProductCommand)
class UpdateProductCommandHandler(IRequestHandler[UpdateProductCommand, BaseResponse[ProductDto]]):
    def __init__(self, uow: IUnitOfWork):
        self._uow = uow

    async def handle(self, request: UpdateProductCommand) -> BaseResponse[ProductDto]:
        product = await self._uow.products.get(Product.id == request.product_id)
        if not product:
            return BaseResponse[ProductDto].not_found("Product not found.")

        # تغییر فیلدها توسط شما
        product.name = request.data.name
        
        # ذخیره تغییرات
        await self._uow.save_changes()

        # سیستم AuditLog به صورت خودکار:
        # ۱. فیلد name را با مقدار قبل و بعد استخراج می‌کند.
        # ۲. کلید اصلی {'id': product.id} را ثبت می‌کند.
        # ۳. شناسه کاربر جاری را از کانتکست می‌خواند.
        # ۴. بدون معطل کردن کاربر، آن را به صف لاگ ارسال می‌کند.

        return BaseResponse[ProductDto].success(data=...)
```

---

### ۳. رفتار سیستم در انواع عملیات دیتابیس

| نوع عملیات (`action`) | وضعیت `old_values` | وضعیت `new_values` | نحوه حل کلید اصلی (`primary_key`) |
|:---:|:---|:---|:---|
| **درج (`Insert`)** | `null` (خالی) | شامل تمام ستون‌ها و مقادیر اولیه ایجاد شده | شناسه‌های افزایشی خودکار (`Auto-increment ID`) پس از تولید توسط PostgreSQL بلافاصله استخراج و ثبت می‌شوند. |
| **ویرایش (`Update`)** | **صرفاً ستون‌های تغییریافته** با مقادیر قدیمی آن‌ها | **صرفاً ستون‌های تغییریافته** با مقادیر جدید آن‌ها | شناسه رکورد ویرایش‌شده ثبت می‌شود. |
| **حذف (`Delete`)** | اسنپ‌شات کامل تمامی ستون‌ها پیش از حذف | `null` (خالی) | شناسه رکورد حذف‌شده ثبت می‌شود. |

> [!TIP]
> **بهینه‌سازی در ویرایش (`Update`)**: اگر رکوردی در سشن لود شود اما هیچ ستونی از آن تغییر نکند، سیستم هوشمندانه از ثبت لاگ بیهوده صرف‌نظر می‌کند.

---

### ۴. فایل تنظیمات و پیکربندی (`appsettings.json`)

تمام رفتار و کارایی سیستم ممیزی از طریق فایل `appsettings.json` در ریشه پروژه مدیریت می‌شود و نیازی به تغییر کد یا کامپایل مجدد ندارد:

```json
{
  "AuditLogSettings": {
    "Enabled": true,
    "AllowedActions": [
      "Insert",
      "Update",
      "Delete"
    ],
    "InclusionMode": "Exclude",
    "Tables": [
      "alembic_version",
      "audit_logs",
      "logs"
    ],
    "Batching": {
      "BatchSize": 100,
      "EnablePeriodicFlush": true,
      "FlushIntervalInSeconds": 5.0
    }
  }
}
```

#### تشریح کلیدهای تنظیمات:

1. **`Enabled` (روشن/خاموش)**:
   - اگر `false` باشد، سیستم کاملاً خاموش است. در این حالت اینترسپتور در اولین خط بدون اجرای هیچ‌گونه Reflection، سریالایز یا صف‌بندی عبور می‌کند و سربار آن دقیقاً **صفر** است.
2. **`AllowedActions` (فیلتر عملیات مجاز)**:
   - مشخص می‌کند کدام عملیات لاگ شوند.
   - مثال: اگر در محیط تست فقط نیاز به ممیزی ویرایش‌ها دارید:
     ```json
     "AllowedActions": [ "Update" ]
     ```
     در این حالت عملیات‌های `Insert` و `Delete` اصلاً پردازش و لاگ نمی‌شوند.
3. **`InclusionMode` و `Tables` (فیلتر جداول)**:
   - **حالت `Exclude` (پیش‌فرض)**: همه جداول ممیزی می‌شوند **به جز** جداولی که در لیست `Tables` آمده‌اند.
   - **حالت `Include`**: **صرفاً** جداولی که نامشان در `Tables` ذکر شده است ممیزی می‌شوند.
   - **جلوگیری از لوپ بی‌نهایت**: جداول `audit_logs`, `auditlogs`, `alembic_version` همیشه به‌صورت خودکار مستثنی هستند و هرگز لاگ تغییرات خود را ثبت نمی‌کنند.
4. **`Batching` (تنظیمات تخلیه دسته‌ای)**:
   - **`BatchSize`**: تعداد لاگی که پس از جمع‌آوری در صف، فلاش و درج دسته‌ای (`Bulk Insert`) در دیتابیس را تحریک می‌کند (پیش‌فرض: `100`).
   - **`EnablePeriodicFlush`**: فعال/غیرفعال‌سازی تخلیه زمان‌بندی‌شده دوره‌ای (`true`/`false`).
   - **`FlushIntervalInSeconds`**: بازه زمانی بر حسب ثانیه (مثلاً `5.0`). اگر تعداد لاگ‌ها به سقف `BatchSize` نرسد، پس از گذشت این زمان لاگ‌های موجود در صف به صورت دسته‌ای ذخیره می‌شوند.

---

### ۵. نحوه استخراج شناسه کاربر (`user_id`)

شناسه کاربر به شکل ناهمگام و بدون نیاز به پاس دادن دستی از طریق کانتکست درخواست استخراج می‌شود:
- میدلور `LoggingContextMiddleware` در هر درخواست کانتکست `LoggingContext` را ست می‌کند.
- پس از احراز هویت، شناسه کاربر در این کانتکست قرار می‌گیرد.
- اینترسپتور در لحظه تأیید تراکنش (`after_commit`)، مقدار `user_id` را از `LoggingContextAccessor.get().user_id` می‌خواند.
- در صورتی که درخواست فاقد کاربر باشد (مثلاً وب‌هوک، جاب پس‌زمینه یا کاربر مهمان)، مقدار `user_id` برابر با `null` ذخیره خواهد شد.

---

### ۶. سناریوی خاص: نادیده‌گرفتن لاگ در کدهای ویژه (`skip_audit`)

اگر در حال اجرای یک اسکریپت Seed، مایگریشن داده، یا یک عملیات حجیم سیستمی هستید و نمی‌خواهید لاگ ممیزی برای آن ثبت شود، کافی است پرچم `skip_audit` را روی سشن فعال کنید:

```python
async with AsyncSessionLocal() as session:
    # فعال‌سازی نادیده‌گرفتن ممیزی برای این سشن
    session.info["skip_audit"] = True

    # هر تغییری در این سشن بدون ثبت در audit_logs ذخیره می‌شود
    session.add(HeavyBatchEntity(...))
    await session.commit()
```

---

### ۷. ساختار جدول `audit_logs` و نحوه کوئری‌گرفتن از تاریخچه

جدول `audit_logs` در دیتابیس شامل ستون‌های زیر است:

```sql
CREATE TABLE audit_logs (
    id BIGSERIAL PRIMARY KEY,
    table_name VARCHAR(255) NOT NULL,
    action VARCHAR(50) NOT NULL,
    old_values JSONB NULL,
    new_values JSONB NULL,
    primary_key JSONB NOT NULL,
    user_id INTEGER NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL
);
```

#### نمونه کوئری ۱: مشاهده تاریخچه تغییرات یک موجودیت خاص با کلید اصلی
برای بازیابی کل تاریخچه تغییرات یک دسته‌بندی با `id = 15`:

```sql
SELECT 
    id, 
    action, 
    old_values, 
    new_values, 
    user_id, 
    created_at
FROM audit_logs
WHERE table_name = 'categorys' 
  AND primary_key @> '{"id": 15}'
ORDER BY created_at DESC;
```

یا در پایتون با SQLAlchemy:
```python
stmt = (
    select(AuditLog)
    .where(
        AuditLog.table_name == "categorys",
        AuditLog.primary_key == {"id": category_id},
    )
    .order_by(AuditLog.created_at.desc())
)
result = await session.execute(stmt)
history = result.scalars().all()
```

#### نمونه کوئری ۲: مشاهده تغییرات انجام‌شده توسط یک کاربر خاص
```sql
SELECT *
FROM audit_logs
WHERE user_id = 42
ORDER BY created_at DESC
LIMIT 50;
```

#### نمونه کوئری ۳: جست‌وجو در تغییرات یک ستون خاص با اپراتورهای JSONB
مشاهده تمام مواردی که ستون `status` ویرایش شده است:
```sql
SELECT 
    id,
    table_name,
    primary_key,
    old_values->>'status' AS previous_status,
    new_values->>'status' AS current_status,
    created_at
FROM audit_logs
WHERE action = 'Update'
  AND new_values ? 'status';
```

---

### ۸. کارایی و خروج امن (High Performance & Graceful Shutdown)

1. **عدم تأثیر بر زمان پاسخ‌دهی (Zero I/O in Request Thread)**:
   - در جریان درخواست کاربر، هیچ رکورد لاگی در دیتابیس `INSERT` نمی‌شود.
   - داده‌ها پس از Commit موفقیت‌آمیز در یک صف درون‌حافظه‌ای (`asyncio.Queue`) قرار داده می‌شوند (`put_nowait`).
   - کل زمان اضافه شده به چرخه درخواست کمتر از ۱ میلی‌ثانیه است.
2. **تخلیه امن هنگام خاموش شدن سرور (Graceful Shutdown)**:
   - در فایل `application_lifespan.py` متد `await app.state.audit_log_worker.stop()` فراخوانی می‌شود.
   - در زمان توقف یا ری‌استارت اپلیکیشن، کارگر پس‌زمینه ابتدا تمامی لاگ‌های موجود در صف را تا آخرین دانه در دیتابیس ذخیره کرده و سپس تسک را خاتمه می‌دهد؛ بنابراین هیچ رکوردی از دست نخواهد رفت.

---

### ۹. وب‌سرویس دریافت لاگ‌ها با صفحه‌بندی (Audit Logs Paged API)

برای مشاهده و بازیابی لاگ‌های ممیزی، اندپوینت استاندارد زیر همراه با مکانیزم یکپارچه صفحه‌بندی، سورتینگ و قابلیت دریافت تمامی داده‌ها پیاده‌سازی شده است:

- **روش و آدرس:** `GET /api/v1AuditLogs/V1`
- **پارامترهای ورودی (Query Parameters):**
  - `page_number`: شماره صفحه (پیش‌فرض: `1`، یا `-1` برای دریافت همه)
  - `page_size`: تعداد آیتم‌ها در هر صفحه (پیش‌فرض: `10`، بین `1` تا `100`، یا `-1` برای دریافت همه)
  - `sort_by`: ستون مورد نظر برای مرتب‌سازی (اختیاری، مثلاً `id` یا `created_at` - در صورت عدم ارسال بر اساس کلید اصلی مرتب می‌شود)
  - `is_ascending`: جهت مرتب‌سازی (`true` صعودی، `false` نزولی، پیش‌فرض: `true`)

#### نمونه ۱: درخواست صفحه‌بندی استاندارد
```http
GET /api/v1AuditLogs/V1?page_number=1&page_size=10&sort_by=id&is_ascending=false
```

#### نمونه ۲: درخواست دریافت تمامی لاگ‌ها
```http
GET /api/v1AuditLogs/V1?page_number=-1&page_size=-1
```

#### نمونه خروجی:
```json
{
  "is_success": true,
  "message": "Audit logs retrieved successfully.",
  "errors": [],
  "data": {
    "items": [
      {
        "id": 12,
        "table_name": "products",
        "action": "Update",
        "old_values": { "name": "Old Product" },
        "new_values": { "name": "New Product" },
        "primary_key": { "id": 5 },
        "user_id": 1,
        "created_at": "2026-09-28T23:15:00Z",
        "updated_at": "2026-09-28T23:15:00Z"
      }
    ],
    "total_count": 1,
    "page_number": 1,
    "page_size": 10,
    "total_pages": 1,
    "has_previous_page": false,
    "has_next_page": false
  },
  "status": "success"
}
```

