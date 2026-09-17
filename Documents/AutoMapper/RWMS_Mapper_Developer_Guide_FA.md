**راهنمای عملی Mapper**

راهنمای استفاده، Mappingهای معمولی و Configurationهای سفارشی

این سند برای استفاده روزمره و توسعه آینده نوشته شده است؛ تمرکز آن روی «چطور از سیستم استفاده کنیم» است، نه جزئیات پیاده‌سازی داخلی.

map • map_list • map_to • MappingProfile

# **راهنمای سریع این سند**

اگر چند ماه بعد به پروژه برگشتید، از این بخش شروع کنید. هر موضوع شما را مستقیم به تصمیمی که برای توسعه لازم دارید هدایت می‌کند.

| **1**  | Mapper را از کجا و چطور دریافت کنیم؟      |
| ------ | ----------------------------------------- |
| **2**  | انتخاب بین map، map_list و map_to         |
| **3**  | Mapping بدون Configuration                |
| **4**  | Mapping سفارشی با MappingProfile          |
| **5**  | for_member: source، transform و resolver  |
| **6**  | ignore و کنترل فیلدهای قابل Mapping       |
| **7**  | ثبت Profileها در mapping_configuration.py |
| **8**  | استفاده در Controller و Handler           |
| **9**  | الگوی Create، List و Update/PATCH         |
| **10** | چک‌لیست و خطاهای رایج                     |

# **1\. Mapper چه مسئله‌ای را حل می‌کند؟**

Mapper برای تبدیل DTO، Entity و سایر Objectهای پروژه استفاده می‌شود تا Controller و Handler مجبور نباشند فیلدها را به‌صورت دستی یکی‌یکی کپی کنند.

| **Source Object** | **Mapper** | **Destination Object** |
| ----------------- | ---------- | ---------------------- |

**قاعده اصلی —** اگر نام فیلدها یکسان است، معمولاً Configuration لازم نیست. Configuration را فقط برای Mappingهای خاص نگه دارید.

# **2\. دریافت Mapper از DI**

در Controller یا Handler با IMapper کار کنید. در Controller از MapperDependency استفاده می‌شود؛ در Handler، IMapper از Constructor دریافت می‌شود.

```
# Controller
mapper: MapperDependency

# Handler
def __init__(self, mapper: IMapper):
    self._mapper = mapper
```

به این ترتیب مصرف‌کننده فقط قرارداد IMapper را می‌شناسد و Configuration مرکزی Mapper یک‌بار هنگام راه‌اندازی آماده می‌شود.

# **3\. سه عملیات اصلی Mapper**

| **موضوع**                              | **کاربرد برای برنامه‌نویس**                                     |
| -------------------------------------- | --------------------------------------------------------------- |
| **map(source, destination_type)**      | ساخت یک Object جدید از Source؛ مناسب Create و تبدیل Entity↔DTO. |
| **map_list(source, destination_type)** | تبدیل یک لیست از Objectها به لیست نوع مقصد.                     |
| **map_to(source, destination)**        | اعمال مقادیر Source روی یک Object موجود؛ مناسب Update/PATCH.    |

# **4\. map(...)**

```
dto = mapper.map(user, UserDto)
user = mapper.map(dto, User)
```

پارامترهای کاربردی map:

• source: آبجکت مبدا.

• destination_type: کلاس مقصدی که باید ساخته شود.

• ignore_none=True: فیلدهایی که مقدار None دارند وارد Mapping نشوند.

• ignore_unset=True: فقط فیلدهایی که واقعاً در ورودی مقداردهی شده‌اند Mapping شوند.

# **5\. map_list(...)**

وقتی Repository یا Service یک لیست از Entityها برمی‌گرداند، به جای Loop دستی از map_list استفاده کنید.

```
users = await uow.users.get_all()
dto_list = mapper.map_list(users, UserDto)
```

**مزیت —** نوع Mapping همه آیتم‌ها یکسان می‌ماند و منطق تبدیل لیست در Controller/Handler تکرار نمی‌شود.

# **6\. map_to(...) برای Update/PATCH**

map_to روی Object موجود Mapping می‌کند و Object جدیدی نمی‌سازد. این حالت برای Update روی Entity دریافت‌شده از دیتابیس مناسب است.

```
mapper.map_to(
    request,
    user,
    ignore_unset=True,
)
```

**برای PATCH —** معمولاً ignore_unset=True انتخاب مناسبی است تا فیلدی که اصلاً از Client ارسال نشده، مقدار موجود Entity را بازنویسی نکند.

اگر None نیز نباید مقدار موجود را پاک کند، بر اساس نیاز Use Case از ignore_none=True هم استفاده کنید.

# **7\. Mapping معمولی بدون Configuration**

وقتی Source و Destination فیلدهای هم‌نام دارند، فقط map کافی است.

```
DTO.email      -> User.email
DTO.full_name  -> User.full_name

user = mapper.map(dto, User)
```

**اصل سادگی —** برای Mappingهای عادی Profile نسازید. Profile باید محل استثناها باشد، نه محل تعریف دوباره همه فیلدهای هم‌نام.

# **8\. چه زمانی MappingProfile لازم است؟**

• نام فیلد Source و Destination متفاوت است.

• قبل از قرار گرفتن مقدار در Destination نیاز به Transform دارید.

• مقدار یک فیلد مقصد از چند فیلد Source ساخته می‌شود.

• یک فیلد نباید Mapping شود و باید Ignore شود.

Configurationهای خاص باید در MappingProfile قرار بگیرند؛ نه در Controller و نه در Handler.

# **9\. ساخت Mapping سفارشی**

```
mapper.create_map(
    UserCustomDto,
    User,
).for_member(
    'full_name',
    source='name',
).for_member(
    'is_active',
    source='status',
    transform=lambda value: value.lower() == 'active',
)
```

این Profile مشخص می‌کند که name به full_name برود و status قبل از قرار گرفتن در is_active به bool تبدیل شود.

# **10\. for_member(...)**

| **موضوع**         | **کاربرد برای برنامه‌نویس**                                                            |
| ----------------- | -------------------------------------------------------------------------------------- |
| **source="name"** | وقتی نام فیلد مبدا با مقصد متفاوت است.                                                 |
| **transform=...** | وقتی ابتدا مقدار یک فیلد Source را می‌گیریم و روی همان مقدار تبدیل انجام می‌دهیم.      |
| **resolver=...**  | وقتی برای ساخت مقدار مقصد به کل Source نیاز داریم؛ مثلاً ترکیب first_name و last_name. |

```
# نام متفاوت
.for_member('full_name', source='name')

# Transform روی یک مقدار
.for_member(
    'price',
    source='price',
    transform=lambda value: value * 2,
)

# Resolver با دسترسی به کل Source
.for_member(
    'full_name',
    resolver=lambda src: f'{src.first_name} {src.last_name}',
)
```

# **11\. ignore(...)**

اگر فیلدی در Destination نباید از Source مقدار بگیرد، آن را در Configuration Ignore کنید.

```
mapper.create_map(SourceDto, User).ignore('id')
```

این کار برای فیلدهایی مثل شناسه، مقادیر سیستمی یا هر مقداری که باید توسط دیتابیس/Domain تعیین شود مفید است.

# **12\. MappingProfile**

هر Domain/Feature می‌تواند Profile خودش را داشته باشد تا Mappingهای خاص همان بخش در یک محل مشخص جمع شوند.

```
class UserMappingProfile(MappingProfile):
    def configure(self, mapper: Mapper) -> None:
        mapper.create_map(
            UserCustomDto,
            User,
        ).for_member(
            'full_name',
            source='name',
        ).for_member(
            'is_active',
            source='status',
            transform=lambda value: value.lower() == 'active',
        )
```

**جهت Mapping —** Configuration سفارشی را برای جهت Source → Destination موردنیاز ثبت کنید. اگر جهت برگشت هم رفتار سفارشی دارد، Mapping آن جهت را نیز جداگانه تعریف کنید.

# **13\. ثبت Profile جدید**

ساختن Profile به‌تنهایی کافی نیست. Profile باید در mapping_configuration.py ثبت شود تا هنگام configure_mapper() اجرا شود.

```
profiles: list[MappingProfile] = [
    UserMappingProfile(),
    ProductMappingProfile(),
]
```

• Profile جدید را Import کنید.

• یک instance از آن را به لیست profiles اضافه کنید.

• configure_mapper() Mapper نهایی را می‌سازد و تمام Profileها را یک‌بار Configure می‌کند.

• Mapper آماده از طریق DI در اختیار Controllerها و Handlerها قرار می‌گیرد.

# **14\. نمونه استفاده در Controller**

```
@router.get('/{user_id}')
async def get_user(
    user_id: int,
    uow: UnitOfWorkDependency,
    mapper: MapperDependency,
):
    user = await uow.users.get(User.id == user_id)
    dto = mapper.map(user, UserDto)
    return dto
```

Controller فقط Object مبدا و نوع مقصد را مشخص می‌کند. اگر Mapping خاصی وجود داشته باشد، Profile مربوط به‌صورت خودکار اعمال می‌شود.

# **15\. استفاده داخل Mediator Handler**

در معماری فعلی پروژه، بهتر است Use Caseهای اصلی Mapper را داخل Handler مصرف کنند. Mapper از طریق Constructor به Handler Inject می‌شود.

```
def __init__(self, uow: IUnitOfWork, mapper: IMapper):
    self._uow = uow
    self._mapper = mapper

async def handle(self, request: CreateUserCommand) -> User:
    user = self._mapper.map(request.data, User)
    await self._uow.users.add(user)
    return user
```

**تفکیک مسئولیت —** Mapping خاص در Profile تعریف می‌شود؛ Handler فقط می‌گوید «این Source را به این Destination تبدیل کن».

# **16\. انتخاب سریع متد مناسب**

| **موضوع**                                      | **کاربرد برای برنامه‌نویس** |
| ---------------------------------------------- | --------------------------- |
| **Create یک Object جدید**                      | map()                       |
| **Entity → DTO**                               | map()                       |
| **DTO → Entity**                               | map()                       |
| **لیست Entityها → لیست DTOها**                 | map_list()                  |
| **Update/PATCH روی Entity موجود**              | map_to()                    |
| **فیلدهای هم‌نام**                             | بدون Configuration          |
| **نام متفاوت / Transform / Resolver / Ignore** | MappingProfile              |

# **17\. خطاها و بررسی‌های رایج**

| **موضوع**                                    | **کاربرد برای برنامه‌نویس**                                                                                         |
| -------------------------------------------- | ------------------------------------------------------------------------------------------------------------------- |
| **Mapping سفارشی اعمال نمی‌شود**             | بررسی کنید Profile در mapping_configuration.py ثبت شده باشد و Source/Destination دقیقاً همان Typeهای ثبت‌شده باشند. |
| **فیلد با نام متفاوت مقدار نمی‌گیرد**        | برای Destination مربوطه for_member(..., source=...) تعریف کنید.                                                     |
| **مقدار باید تبدیل شود**                     | از transform استفاده کنید؛ اگر چند فیلد/کل Source لازم است از resolver استفاده کنید.                                |
| **PATCH فیلدهای ارسال‌نشده را تغییر می‌دهد** | در map_to از ignore_unset=True استفاده کنید.                                                                        |
| **None نباید مقدار موجود را پاک کند**        | در Use Case مناسب ignore_none=True را فعال کنید.                                                                    |
| **یک فیلد نباید Mapping شود**                | در Profile آن را ignore کنید.                                                                                       |

# **18\. چک‌لیست افزودن Mapping جدید**

• اول بررسی کن آیا نام فیلدها یکسان است؛ اگر بله احتمالاً هیچ Profileای لازم نیست.

• اگر Mapping خاص است، Profile مناسب Feature را پیدا کن یا Profile جدید بساز.

• create_map(Source, Destination) را برای جهت موردنیاز تعریف کن.

• فقط استثناها را با for_member / ignore مشخص کن.

• Profile را در mapping_configuration.py ثبت کن.

• در Controller یا Handler فقط IMapper/MapperDependency را مصرف کن.

• برای Create از map، برای List از map_list و برای Update موجود از map_to استفاده کن.

**نسخه ذهنی کوتاه —** هم‌نام = خودکار؛ استثنا = Profile؛ ساخت Object = map؛ لیست = map_list؛ ویرایش Object موجود = map_to.