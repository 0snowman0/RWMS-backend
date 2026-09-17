**راهنمای فنی پیاده‌سازی دسته‌بندی پویا (Category)**

پروژه RWMS - معماری Clean Architecture + Mediator + Unit of Work + PostgreSQL JSONB

**هدف سند  
**ثبت دقیق روشی که برای طراحی، ذخیره‌سازی، خواندن، ویرایش و حذف Categoryهای دارای فیلدهای پویا استفاده شد؛ به‌گونه‌ای که توسعه آینده سیستم بدون وابستگی به JSON خام و بدون تغییرات گسترده در مدل دیتابیس انجام شود.

نسخه مستند: ۱.۰

وضعیت: CRUD اصلی Category پیاده‌سازی و تست شده است.

**۱. مسئله‌ای که حل کردیم**

در سیستم انبار و کالا، هر دسته محصول مشخصات متفاوتی دارد. برای مثال دوربین مداربسته می‌تواند «رزولوشن»، «نوع دوربین» و «دید در شب» داشته باشد، در حالی که یک سوئیچ شبکه ممکن است «تعداد پورت»، «PoE» و «توان مصرفی» داشته باشد. بنابراین استفاده از ستون‌های ثابت برای تمام مشخصات کالا در بلندمدت مناسب نبود.

• تعریف Category باید کاملاً پویا باشد.

• هر Category بتواند هر تعداد فیلد اختصاصی داشته باشد.

• نوع، الزامی بودن، مقدار پیش‌فرض، گزینه‌ها و قوانین هر فیلد قابل تعریف باشد.

• توسعه‌دهنده در Business/Application Layer با مدل‌های Type-safe کار کند، نه با dict و JSON خام.

• ساختار دیتابیس برای اضافه شدن قابلیت‌های آینده نیازمند Migration دائمی نباشد.

**۲. تصمیم معماری: مدل Hybrid با PostgreSQL JSONB**

برای رسیدن به انعطاف بالا، ساختار پایه Category به‌صورت Relational نگه داشته شد و تعریف فیلدهای پویا در یک ستون JSONB ذخیره شد. این روش بین سادگی دیتابیس و Type Safety در کد تعادل ایجاد می‌کند.

| **لایه**    | **ساختار**               | **وظیفه**                                   |
| ----------- | ------------------------ | ------------------------------------------- |
| PostgreSQL  | fields_schema : JSONB    | ذخیره انعطاف‌پذیر تعریف فیلدها              |
| Domain      | DynamicFieldDefinition   | مدل Type-safe برای تعریف هر فیلد            |
| Entity      | Category.fields property | تبدیل JSONB به مدل و برعکس                  |
| Application | DTO / Command / Handler  | اجرای Use Caseها                            |
| API         | FastAPI + Mediator       | ورودی/خروجی HTTP و ارسال Request به Handler |

**اصل کلیدی  
**JSON فقط فرمت ذخیره‌سازی است؛ قرارداد Business نیست. در کد، فیلدهای پویا به‌صورت list\[DynamicFieldDefinition\] استفاده می‌شوند.

**۳. مدل Category و مخفی کردن JSON خام**

در Entity، ستون واقعی دیتابیس با نام fields_schema تعریف شد، اما به‌صورت خصوصی در متغیر \_fields_schema نگه‌داری می‌شود. Property عمومی fields وظیفه تبدیل دوطرفه را انجام می‌دهد.

```
class Category(Base):
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    _fields_schema: Mapped[list[dict[str, Any]]] = mapped_column(
        "fields_schema",
        JSONB,
        nullable=False,
        default=list,
    )

    @property
    def fields(self) -> list[DynamicFieldDefinition]:
        if not self._fields_schema:
            return []

        return [
            DynamicFieldDefinition.model_validate(item)
            for item in self._fields_schema
        ]

    @fields.setter
    def fields(self, value: list[DynamicFieldDefinition]) -> None:
        self._fields_schema = [
            field.model_dump(mode="json")
            for field in value
        ]
```

مزیت این طراحی این است که هیچ Handler یا Service لازم نیست از جزئیات JSONB آگاه باشد. همچنین Setter کل آرایه JSON را دوباره Assign می‌کند که Change Tracking در SQLAlchemy را قابل‌اعتمادتر می‌سازد.

**۴. تعریف نوع فیلدهای پویا**

نوع فیلدها با Enum مشخص می‌شود تا از Stringهای پراکنده و خطاهای تایپی جلوگیری شود.

```
class DynamicFieldType(StrEnum):
    STRING = "string"
    INTEGER = "integer"
    DECIMAL = "decimal"
    BOOLEAN = "boolean"
    DATE = "date"
    DATETIME = "datetime"
    SELECT = "select"
    MULTI_SELECT = "multi_select"
```

برای SELECT و MULTI_SELECT نیز هر گزینه به‌صورت ساخت‌یافته با value و label ذخیره می‌شود؛ نه به‌شکل رشته‌هایی مانند A|B|C.

```
class DynamicFieldOption(BaseModel):
    model_config = ConfigDict(frozen=True)

    value: str
    label: str
```

**۵. مدل DynamicFieldDefinition**

این مدل مرکز اصلی تعریف مشخصات پویاست. فیلدهای آن در چند گروه قرار گرفتند: اطلاعات پایه، رفتار، نمایش، قوانین عددی، قوانین رشته‌ای، گزینه‌های انتخابی و تنظیمات توسعه آینده.

| **فیلدها**                               | **کاربرد**                                          |
| ---------------------------------------- | --------------------------------------------------- |
| name / title / field_type                | نام داخلی، عنوان نمایشی و نوع داده                  |
| required / unique                        | الزام ورود و یکتا بودن منطقی                        |
| default_value / auto_generate / readonly | مقدار پیش‌فرض، تولید خودکار و فقط‌خواندنی           |
| is_active / sort_order / show_in_list    | فعال بودن، ترتیب نمایش و نمایش در لیست              |
| unit / placeholder / description         | اطلاعات UI و راهنمای فیلد                           |
| min_value / max_value / decimal_places   | قوانین فیلدهای عددی                                 |
| min_length / max_length / regex          | قوانین فیلدهای متنی                                 |
| options                                  | گزینه‌های SELECT و MULTI_SELECT                     |
| settings                                 | فضای آزاد برای تنظیمات آینده بدون تغییر ساختار اصلی |

**۶. DTOهای Category**

برای جلوگیری از وابستگی API به Entity، DTOهای جداگانه برای Create، Update و Response تعریف شدند.

**۶.۱. CreateCategoryDto**

```
class CreateCategoryDto(BaseModel):
    name: str
    description: str | None = None
    fields: list[DynamicFieldDefinition] = Field(default_factory=list)
```

**۶.۲. UpdateCategoryDto**

```
class UpdateCategoryDto(BaseModel):
    name: str
    description: str | None = None
    fields: list[DynamicFieldDefinition] = Field(default_factory=list)
```

Update عمداً به‌صورت PUT و Replace کامل طراحی شد. بنابراین Client وضعیت کامل جدید Category را ارسال می‌کند؛ اگر فیلدی از لیست جدید حذف شده باشد، از fields_schema نیز حذف می‌شود و اگر فیلد جدیدی اضافه شده باشد، وارد JSONB می‌شود.

**۶.۳. CategoryDto**

```
class CategoryDto(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str | None = None
    fields: list[DynamicFieldDefinition] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime
```

**نکته Mapper  
**برای خواندن Entity و ساخت CategoryDto از AutoMapper اختصاصی پروژه استفاده می‌شود. قابلیت‌هایی مانند ignore_none و ignore_unset در Mapper موجودند، اما در Read معمولاً فعال نمی‌شوند چون می‌خواهیم وضعیت کامل Entity منتقل شود.

**۷. Repository و Unit of Work**

CategoryRepository از GenericRepository ارث می‌برد و عملیات عمومی get/add/update/delete را در اختیار Handler قرار می‌دهد. متد اختصاصی get_by_name نیز برای نیازهای تجاری آینده اضافه شد.

```
class ICategoryRepository(
    IGenericRepository[Category],
    Protocol,
):
    async def get_by_name(self, name: str) -> Category | None:
        ...
```

```
class CategoryRepository(GenericRepository[Category], ICategoryRepository):
    def __init__(self, session) -> None:
        super().__init__(session=session, entity_type=Category)

    async def get_by_name(self, name: str) -> Category | None:
        return await self.get(Category.name == name)
```

Repository از طریق property categories در IUnitOfWork و SqlAlchemyUnitOfWork در اختیار Handlerها قرار می‌گیرد. Commit داخل Handler انجام نمی‌شود؛ TransactionBehavior بعد از اجرای موفق Handler، save_changes را فراخوانی می‌کند.

**۸. جریان CRUD با Mediator**

تمام Use Caseها از مسیر Mediator عبور می‌کنند. Controller فقط Request مناسب را می‌سازد و با mediator.send ارسال می‌کند. Business Logic در Handler قرار دارد.

```
API Controller
    ↓
IRequest (Command / Query)
    ↓
Mediator Pipeline
    ↓
Logging / Performance / Validation / Transaction
    ↓
Handler
    ↓
UnitOfWork + Repository
    ↓
PostgreSQL
```

**۸.۱. Create**

• CreateCategoryDto از API دریافت می‌شود.

• CreateCategoryCommand ساخته می‌شود.

• Handler یک Category می‌سازد و category.fields را Assign می‌کند.

• Repository.add اجرا می‌شود و TransactionBehavior در انتها Commit می‌کند.

```
category = Category(
    name=request.data.name,
    description=request.data.description,
)

category.fields = request.data.fields
await self._uow.categories.add(category)
```

**۸.۲. Read بر اساس id**

در Query، Category از Repository با Predicate خوانده می‌شود و سپس توسط Mapper اختصاصی پروژه به CategoryDto تبدیل می‌شود.

```
category = await self._uow.categories.get(
    Category.id == request.category_id
)

category_dto = self._mapper.map(
    category,
    CategoryDto,
)
```

**۸.۳. Update به روش Replace کامل**

برای این Entity، Replace کامل انتخاب شد چون fields یک Schema پویاست و حالت Partial می‌تواند ابهام ایجاد کند: نبودن یک فیلد در Request ممکن است به معنی «تغییر نده» یا «حذف کن» باشد. PUT کامل این ابهام را از بین می‌برد.

```
category = await self._uow.categories.get(
    Category.id == request.category_id
)

category.name = request.data.name
category.description = request.data.description
category.fields = request.data.fields
```

**چرا update() صریح لازم نشد؟  
**Entity از همان SQLAlchemy Session خوانده شده و Tracked است. تغییر propertyها توسط SQLAlchemy تشخیص داده می‌شود و Commit نهایی توسط TransactionBehavior انجام می‌شود.

**۸.۴. Delete**

در حذف، ابتدا وجود Category بررسی می‌شود. سپس Entity به Repository.delete داده می‌شود. Commit باز هم توسط Pipeline انجام می‌شود.

```
category = await self._uow.categories.get(
    Category.id == request.category_id
)

if category is None:
    return BaseResponse[bool].not_found(
        message="Category not found."
    )

await self._uow.categories.delete(category)
```

**۹. APIهای نهایی Category**

| **Method** | **Endpoint**   | **کاربرد**             |
| ---------- | -------------- | ---------------------- |
| POST       | /create        | ایجاد Category         |
| GET        | /{category_id} | دریافت Category        |
| PUT        | /{category_id} | جایگزینی کامل Category |
| DELETE     | /{category_id} | حذف Category           |

**۱۰. نمونه JSON ذخیره‌شده در fields_schema**

```
[
  {
    "name": "resolution",
    "title": "رزولوشن",
    "field_type": "decimal",
    "required": true,
    "unit": "MP",
    "min_value": "1",
    "max_value": "32",
    "decimal_places": 1,
    "options": [],
    "settings": {}
  },
  {
    "name": "camera_type",
    "title": "نوع دوربین",
    "field_type": "select",
    "required": true,
    "options": [
      {"value": "ip", "label": "IP"},
      {"value": "analog", "label": "آنالوگ"}
    ],
    "settings": {}
  }
]
```

**۱۱. نکات مهم برای توسعه آینده**

• در Product می‌توان attributes را نیز به‌صورت JSONB ذخیره کرد و مقادیر آن را بر اساس Category.fields اعتبارسنجی کرد.

• قانون unique برای فیلدهای پویا بهتر است در Application Logic و در صورت نیاز با Index/Constraint تخصصی PostgreSQL تکمیل شود.

• برای PATCH واقعی می‌توان از قابلیت‌های ignore_none و ignore_unset در AutoMapper استفاده کرد؛ اما PUT فعلی عمداً Replace کامل است.

• حذف یا تغییر نوع یک Dynamic Field در Category می‌تواند روی Productهای موجود اثر بگذارد؛ قبل از توسعه Product باید سیاست Migration داده‌های قدیمی تعریف شود.

• settings فضای توسعه کنترل‌شده برای قابلیت‌های آینده است؛ بهتر است فقط تنظیمات واقعاً وابسته به نوع فیلد در آن قرار گیرند.

• API و Handlerها نباید مستقیماً \_fields_schema را تغییر دهند؛ همیشه از property عمومی fields استفاده شود.

**۱۲. جمع‌بندی**

ماژول Category اکنون یک ساختار پویا، Type-safe و توسعه‌پذیر دارد. PostgreSQL انعطاف JSONB را فراهم می‌کند، Domain مدل‌های مشخص و قابل اعتبارسنجی در اختیار برنامه‌نویس می‌گذارد و Application Layer از طریق Mediator، Repository و Unit of Work از جزئیات ذخیره‌سازی جدا باقی می‌ماند.

**وضعیت نهایی  
**Create ✅ Read ✅ Update ✅ Delete ✅  
ساختار پویا با JSONB ✅ مدل Type-safe ✅ Mediator/UoW ✅ آماده برای اتصال به Product Attributes ✅