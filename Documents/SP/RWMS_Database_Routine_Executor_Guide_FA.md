**راهنمای استفاده از Database Routine Executor**

راهنمای عملی اجرای Procedure و Function در PostgreSQL برای توسعه‌دهندگان RWMS

**هدف این سند** این راهنما توضیح می‌دهد هر متد چه کاربردی دارد و برنامه‌نویس چگونه از آن استفاده کند. وارد جزئیات پیاده‌سازی داخلی Executor نمی‌شویم.

**۱. تصویر کلی**

Database Routine Executor یک مسیر واحد برای اجرای Routineهای PostgreSQL در اختیار برنامه می‌گذارد. برنامه‌نویس به‌جای نوشتن مستقیم SQLAlchemy در Controller یا Handler، از IDatabaseRoutineExecutor استفاده می‌کند.

```
Controller / Handler
        ↓
IDatabaseRoutineExecutor
        ↓
PostgresRoutineExecutor
        ↓
PostgreSQL
```

**۲. متدهای اصلی**

<div class="joplin-table-wrapper"><table><tbody><tr><th><p><strong>متد</strong></p></th><th><p><strong>خروجی</strong></p></th><th><p><strong>بهترین کاربرد</strong></p></th></tr><tr><td><pre><code>execute()</code></pre></td><td><p>اجرای Procedure بدون Result Set</p></td><td><p>عملیات ثبت/ویرایش/اجرای فرمان دیتابیسی</p></td></tr><tr><td><pre><code>execute_scalar()</code></pre></td><td><p>دریافت یک مقدار</p></td><td><p>Count، Sum، ID، Boolean یا مقدار محاسباتی</p></td></tr><tr><td><pre><code>execute_raw()</code></pre></td><td><p>دریافت خروجی خام</p></td><td><p>وقتی DTO لازم نیست یا می‌خواهیم ساختار واقعی خروجی را ببینیم</p></td></tr><tr><td><pre><code>execute_one()</code></pre></td><td><p>یک ردیف → DTO/Model</p></td><td><p>گرفتن یک رکورد مشخص مانند User بر اساس ID</p></td></tr><tr><td><pre><code>execute_list()</code></pre></td><td><p>چند ردیف → List[DTO/Model]</p></td><td><p>لیست کاربران، محصولات، گزارش‌ها و نتایج چندردیفی</p></td></tr></tbody></table></div>

**۳. گرفتن Executor از DI**

در Controller، Executor از طریق Dependency آماده دریافت می‌شود:

```
routine: DatabaseRoutineExecutorDependency
```

در Handlerهای Mediator نیز می‌توان IDatabaseRoutineExecutor را در Constructor درخواست کرد؛ ServiceResolver همان Dependency ثبت‌شده را در اختیار Handler قرار می‌دهد.

```
def __init__(
    self,
    routine: IDatabaseRoutineExecutor,
):
    self._routine = routine
```

**قاعده پیشنهادی** اگر Use Case از Mediator استفاده می‌کند، اجرای Routine را داخل Handler انجام بده. برای تست‌های ساده یا Endpointهای موقت، استفاده مستقیم در Controller قابل قبول است.

**۴. execute() — اجرای Procedure بدون خروجی**

این متد زمانی استفاده می‌شود که Routine قرار است یک عملیات دیتابیسی انجام دهد و Result Set لازم نداریم؛ مثلاً تغییر وضعیت کاربر، عملیات گروهی، ثبت لاگ دیتابیسی یا به‌روزرسانی چند جدول.

```
await routine.execute(
    "public.sp_test_set_user_active",
    {
        "p_user_id": 10,
        "p_is_active": True,
    },
)
```

پارامترها اختیاری هستند. اگر Procedure ورودی ندارد، آرگومان params را ارسال نکن.

```
await routine.execute(
    "public.sp_rebuild_statistics",
)
```

**Transaction** خود execute() Commit انجام نمی‌دهد. داخل Mediator، TransactionBehavior مسئول Commit است. اگر مستقیم از Controller تست می‌کنی، باید ذخیره نهایی را خودت انجام بدهی.

**۵. execute_scalar() — گرفتن یک مقدار**

برای Functionهایی مناسب است که دقیقاً یک مقدار برمی‌گردانند؛ مانند تعداد رکوردها، مجموع، میانگین، یک ID، Boolean یا یک مقدار محاسباتی.

```
count = await routine.execute_scalar(
    "public.fn_test_user_count",
)
```

مثال با ورودی:

```
count = await routine.execute_scalar(
    "public.fn_count_users_by_status",
    {
        "p_is_active": True,
    },
)
```

**انتخاب درست** اگر فقط یک عدد یا مقدار لازم داری، execute_scalar() از execute_raw() خواناتر و مناسب‌تر است.

**۶. execute_raw() — خروجی خام**

این متد ردیف‌های خروجی را بدون تبدیل به DTO برمی‌گرداند. نتیجه به شکل list\[dict\] است.

```
result = await routine.execute_raw(
    "public.fn_test_users_raw",
)
```

نمونه نتیجه:

```
[
    {
        "id": 1,
        "email": "a@test.com",
        "full_name": "Ali",
        "is_active": True,
    }
]
```

این حالت برای بررسی سریع خروجی Routine، Endpointهای داخلی، گزارش‌های پویا یا زمانی که DTO مشخصی لازم نداریم مناسب است.

**۷. execute_one() — یک ردیف به DTO یا Model**

وقتی انتظار داریم Routine حداکثر یک رکورد منطقی برگرداند از execute_one() استفاده می‌کنیم. خروجی ابتدا از دیتابیس گرفته می‌شود و سپس توسط Mapper موجود سیستم به نوع مقصد تبدیل می‌شود.

```
user = await routine.execute_one(
    "public.fn_test_user_by_id",
    RoutineUserDto,
    {
        "p_user_id": 10,
    },
)
```

اگر رکوردی پیدا نشود، خروجی None است. بنابراین در Controller یا Handler باید این حالت مدیریت شود.

```
if user is None:
    raise HTTPException(
        status_code=404,
        detail="User not found",
    )
```

**۸. execute_list() — چند ردیف به لیست DTO**

برای Result Setهای چندردیفی استفاده می‌شود. تمام ردیف‌ها با Mapper سیستم به نوع مقصد تبدیل می‌شوند و خروجی list\[T\] خواهد بود.

```
users = await routine.execute_list(
    "public.fn_test_users_list",
    RoutineUserDto,
)
```

نمونه با فیلتر ورودی:

```
users = await routine.execute_list(
    "public.fn_test_users_list",
    RoutineUserDto,
    {
        "p_is_active": True,
    },
)
```

**مزیت مهم** اگر نام ستون‌های خروجی با فیلدهای DTO یکسان باشد، Mapping معمولی کافی است. اگر نام‌ها متفاوت باشند، همان MappingProfile و تنظیمات سفارشی Mapper فعلی قابل استفاده است.

**۹. پارامترهای Routine**

پارامترها به شکل dict ارسال می‌شوند. نام کلید باید با نام پارامتر تعریف‌شده در Routine هماهنگ باشد.

```
{
    "p_user_id": 10,
    "p_is_active": True,
}
```

برای Routine بدون ورودی:

```
result = await routine.execute_scalar(
    "public.fn_test_user_count",
)
```

**نام Routine** نام Routine را ترجیحاً همراه Schema بنویس؛ برای مثال public.fn_test_user_count. این کار از ابهام بین Schemaها جلوگیری می‌کند.

**۱۰. DTO مناسب برای خروجی**

برای execute_one() و execute_list() نوع مقصد باید با خروجی Routine سازگار باشد. یک DTO ساده برای تست کاربران می‌تواند چنین شکلی داشته باشد:

```
class RoutineUserDto(BaseModel):
    id: int
    email: str
    full_name: str
    is_active: bool
```

اگر Routine ستون‌های بیشتری برگرداند ولی Mapper مقصد فقط فیلدهای موردنیاز را بشناسد، DTO همچنان می‌تواند فقط اطلاعات موردنیاز Use Case را نمایش دهد.

**۱۱. انتخاب سریع متد**

<div class="joplin-table-wrapper"><table><tbody><tr><th><p><strong>نیاز</strong></p></th><th><p><strong>متد مناسب</strong></p></th></tr><tr><td><p>فقط عملیات انجام شود و خروجی لازم نیست</p></td><td><pre><code>execute()</code></pre></td></tr><tr><td><p>یک مقدار مانند Count یا ID لازم است</p></td><td><pre><code>execute_scalar()</code></pre></td></tr><tr><td><p>خروجی خام و بدون DTO لازم است</p></td><td><pre><code>execute_raw()</code></pre></td></tr><tr><td><p>یک رکورد و تبدیل مستقیم به DTO لازم است</p></td><td><pre><code>execute_one()</code></pre></td></tr><tr><td><p>چند رکورد و تبدیل مستقیم به List[DTO] لازم است</p></td><td><pre><code>execute_list()</code></pre></td></tr></tbody></table></div>

**۱۲. استفاده در Mediator Handler**

در Use Caseهای اصلی، Executor می‌تواند مانند IMapper و IUnitOfWork از Constructor Handler دریافت شود.

```
class ExampleHandler:

    def __init__(
        self,
        routine: IDatabaseRoutineExecutor,
    ):
        self._routine = routine

    async def handle(self, request):
        return await self._routine.execute_list(
            "public.fn_test_users_list",
            RoutineUserDto,
        )
```

اگر Handler یک Command باشد، TransactionBehavior می‌تواند Commit نهایی را مدیریت کند. برای Queryهای صرفاً خواندنی نیازی به SaveChanges نیست.

**۱۳. خطاهای رایج هنگام استفاده**

• استفاده از execute() برای Function خروجی‌دار یا استفاده از execute_raw()/execute_one()/execute_list() برای Procedure معمولی.

• اشتباه نوشتن نام پارامتر در dict نسبت به پارامتر Routine.

• ناهماهنگی ستون‌های خروجی با DTO مقصد در execute_one() یا execute_list().

• فراموش کردن Commit هنگام تست مستقیم یک Procedure تغییردهنده خارج از TransactionBehavior.

• فرض کردن اینکه execute_one() همیشه نتیجه دارد؛ این متد ممکن است None برگرداند.

**۱۴. چک‌لیست افزودن یک Routine جدید**

• مشخص کن Routine فقط عملیات انجام می‌دهد یا خروجی دارد.

• اگر خروجی دارد، مشخص کن Scalar، Raw، یک رکورد یا چند رکورد است.

• در صورت نیاز DTO مناسب خروجی را تعریف کن.

• اگر نام ستون‌ها متفاوت است، MappingProfile را تنظیم کن.

• نام Routine و پارامترها را همراه Schema ثبت کن.

• متد مناسب Executor را در Handler یا Controller صدا بزن.

• برای عملیات تغییردهنده، مرز Transaction و Commit را بررسی کن.

**خارج از محدوده این نسخه** قابلیت Multi Result و تشخیص خودکار چند Result Set عمداً در این راهنما پوشش داده نشده و به‌صورت جداگانه مستند خواهد شد.