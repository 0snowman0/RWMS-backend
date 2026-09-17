**راهنمای استفاده از Rate Limiting در پروژه RWMS**

راهنمای سریع برای برنامه‌نویسان

هدف این سند، توضیح نحوه استفاده از Rate Limiting است. جزئیات داخلی پیاده‌سازی عمداً حذف شده‌اند تا استفاده از سیستم سریع و روشن باشد.

**۱. محل تعریف و تغییر Policyها**

تمام تنظیمات Rate Limit باید در فایل زیر تعریف یا ویرایش شوند:

```
Configs\RateLimiting\rate_limit.py
```

Policy پیش‌فرض سیستم و Policyهای اختصاصی مانند login، register و refresh_token در همین فایل نگهداری می‌شوند. برای اضافه‌کردن Policy جدید، همان‌جا یک نام جدید تعریف کنید و نوع الگوریتم و محدودیت موردنظر را مشخص کنید.

**۲. الگوریتم‌های پشتیبانی‌شده**

سیستم در حال حاضر از سه روش Rate Limiting پشتیبانی می‌کند:

| **روش**        | **مناسب برای**                                           | **مزیت اصلی**                             | **محدودیت / نکته**                                               |
| -------------- | -------------------------------------------------------- | ----------------------------------------- | ---------------------------------------------------------------- |
| Fixed Window   | ورود، ثبت‌نام و APIهای ساده                              | ساده، سریع و قابل فهم                     | در مرز دو بازه ممکن است تعداد درخواست‌های نزدیک به هم بیشتر شود. |
| Sliding Window | APIهایی که کنترل یکنواخت‌تر لازم دارند                   | کنترل دقیق‌تر و نرم‌تر در طول زمان        | نسبت به Fixed Window محاسبه و نگهداری بیشتری نیاز دارد.          |
| Token Bucket   | APIهای عمومی یا سرویس‌هایی که Burst کنترل‌شده لازم دارند | اجازه Burst کوتاه در کنار کنترل نرخ متوسط | تنظیم ظرفیت و سرعت پرشدن Tokenها نیاز به دقت بیشتری دارد.        |

**۳. Public Rate Limit (Policy پیش‌فرض)**

اگر روی یک Endpoint هیچ Attribute/Decorator اختصاصی Rate Limit قرار ندهید، سیستم به‌صورت خودکار Policy پیش‌فرض (Public/Default) را اعمال می‌کند.

```
@router.get("/products")
async def get_products():
    ...
```

در مثال بالا هیچ Rate Limit اختصاصی نوشته نشده است؛ بنابراین Endpoint از DEFAULT_RATE_LIMIT_POLICY استفاده می‌کند.

**۴. Private Rate Limit (Policy اختصاصی Endpoint)**

اگر یک Endpoint محدودیت اختصاصی نیاز دارد، نام Policy را با Decorator مربوط به Rate Limit مشخص کنید. در این حالت Policy اختصاصی جای Policy پیش‌فرض را می‌گیرد.

```
@router.post("/login")
@rate_limit("login")
async def login():
    ...
```

در این مثال، Endpoint مربوط به login از Policy با نام login استفاده می‌کند و تنظیم Public/Default روی آن اعمال نمی‌شود.

**نکته: منظور از Public و Private در این سند، Policy عمومی و Policy اختصاصی Rate Limit است و ارتباطی با سطح دسترسی، Authentication یا Authorization ندارد.**

**۵. استفاده اجباری از AppRouter**

برای اینکه Rate Limiting به‌صورت خودکار روی Endpointها فعال باشد، Routerها باید با AppRouter ساخته شوند. از APIRouter مستقیم استفاده نکنید.

```
router = AppRouter(
    tags=["Products"]
)
```

در ساختار فعلی پروژه، prefix توسط سیستم به‌صورت خودکار مدیریت می‌شود. برنامه‌نویس فقط در صورت نیاز Tag مناسب را وارد می‌کند. تنظیمات ثابت Rate Limiting نیز توسط AppRouter اعمال می‌شوند و نباید در هر Router تکرار شوند.

**۶. چک‌لیست برنامه‌نویس**

• برای تعریف یا تغییر Rate Limit فقط به Configs\\RateLimiting\\rate_limit.py مراجعه کنید.

• برای Routerها از AppRouter استفاده کنید؛ از APIRouter مستقیم استفاده نکنید.

• اگر Endpoint Decorator اختصاصی Rate Limit ندارد، Policy پیش‌فرض به‌صورت خودکار اعمال می‌شود.

• اگر Endpoint دارای @rate_limit("policy_name") باشد، همان Policy اختصاصی اعمال می‌شود.

• برای اضافه‌کردن محدودیت جدید، ابتدا Policy جدید را در فایل تنظیمات تعریف کنید و سپس نام آن را روی Endpoint موردنظر استفاده کنید.

• برای انتخاب الگوریتم، از FixedWindowOptions، SlidingWindowOptions یا TokenBucketOptions استفاده کنید.