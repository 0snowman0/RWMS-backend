**راهنمای کسب‌وکار و استفاده از ماژول کالا**

**RWMS - سیستم مدیریت انبار با دسته‌بندی‌ها و مشخصات داینامیک**

نسخه توسعه‌دهنده و مرجع تحلیل بیزینسی

| **چند دسته‌بندی** | **فیلد داینامیک** | **JSONB** | **CRUD کامل** |
| ----------------- | ----------------- | --------- | ------------- |

تاریخ مستند: شهریور ۱۴۰۵ / سپتامبر ۲۰۲۶

**فهرست مطالب**

۱. هدف و داستان کسب‌وکار ماژول کالا

۲. معماری مفهومی و تصمیم‌های اصلی

۳. مدل Category و تعریف فیلدهای داینامیک

۴. مدل Product و نحوه ذخیره مقادیر

۵. قراردادهای DTO و جریان داده

۶. فرایند ساخت کالا

۷. فرایند خواندن و نمایش کالا

۸. فرایند ویرایش و حذف

۹. سناریوی واقعی تست: دوربین مداربسته

۱۰. راهنمای Frontend

۱۱. قوانین یکپارچگی داده و نکات مهم

۱۲. وضعیت فعلی و توسعه‌های بعدی

**دامنه این سند:** این مستند دقیقاً بر اساس پیاده‌سازی فعلی ماژول Category و Product نوشته شده است. قابلیت‌هایی که هنوز پیاده‌سازی نشده‌اند، به‌صراحت در بخش «توسعه‌های بعدی» مشخص شده‌اند.

**۱. هدف و داستان کسب‌وکار ماژول کالا**

هدف این ماژول این است که سیستم انبار مجبور نباشد برای هر نوع کالا یک جدول و مدل جداگانه داشته باشد. کالا فقط چند ویژگی ثابت دارد و مشخصات تخصصی آن از دسته‌بندی‌هایی می‌آید که مدیر یا انباردار برای آن انتخاب می‌کند.

برای مثال یک دوربین می‌تواند هم‌زمان عضو دسته «مشخصات فنی دوربین» و دسته «اطلاعات بازرگانی» باشد. دسته اول فیلدهایی مثل رزولوشن و نوع دوربین را تعریف می‌کند و دسته دوم فیلدهایی مثل کشور سازنده و کد رهگیری واردات را. با انتخاب هر دو دسته، فرم کالا به‌صورت داینامیک از مجموع فیلدهای آنها ساخته می‌شود.

**اصل کسب‌وکاری:** Category می‌گوید «چه اطلاعاتی باید وجود داشته باشد» و Product می‌گوید «مقدار واقعی آن اطلاعات برای این کالا چیست».

**مزیت این رویکرد**

• افزودن نوع جدید کالا بدون تغییر Schema اصلی جدول Product.

• امکان اتصال یک کالا به چند دسته‌بندی هم‌زمان.

• ساخت فرم‌های پویا در Frontend بر اساس تعریف دسته‌بندی‌ها.

• حفظ ساختار رابطه‌ای برای Categoryها و استفاده از JSONB فقط برای داده‌های پویا.

• امکان توسعه تدریجی قوانین اعتبارسنجی بدون بازطراحی دیتابیس.

**۲. معماری مفهومی و تصمیم‌های اصلی**

معماری نهایی یک مدل Hybrid است: روابط واقعی سیستم در PostgreSQL به‌صورت Relational نگه‌داری می‌شوند و مقادیر پویا در JSONB ذخیره می‌شوند.

| **بخش**                | **نوع ذخیره‌سازی**   | **دلیل**                                        |
| ---------------------- | -------------------- | ----------------------------------------------- |
| Product ↔ Category     | جدول واسط Relational | رابطه واقعی چندبه‌چند، مناسب Join و Foreign Key |
| Category.fields_schema | JSONB                | ساختار تعریف فیلدها پویا و قابل توسعه است       |
| Product.attributes     | JSONB                | مقادیر هر کالا پویا و متغیر است                 |

**نمای ساده معماری**

```
Category
  └── fields_schema JSONB
        └── DynamicFieldDefinition
              ├── field_id
              ├── name / title
              ├── field_type
              ├── required / default_value
              └── validation & UI metadata

Product
  ├── name
  ├── categories  (Many-to-Many)
  └── attributes JSONB
        └── [ { category_id, field_id, value }, ... ]
```

**۳. مدل Category و تعریف فیلدهای داینامیک**

هر Category در ستون fields_schema مجموعه‌ای از DynamicFieldDefinitionها را نگه می‌دارد. هر فیلد یک field_id پایدار دارد. این شناسه مهم‌ترین کلید اتصال بین تعریف فیلد و مقدار آن در Product است.

| **فیلد مهم**  | **کارکرد**                                                    |
| ------------- | ------------------------------------------------------------- |
| field_id      | UUID پایدار هر فیلد؛ حتی با تغییر name یا title نباید عوض شود |
| name          | نام داخلی برای توسعه و خوانایی                                |
| title         | عنوان نمایشی برای کاربر                                       |
| field_type    | نوع داده مانند string, decimal, boolean, select               |
| required      | اجباری بودن مقدار                                             |
| default_value | مقداری که در صورت عدم ارسال کاربر قابل اعمال است              |
| is_active     | فعال یا غیرفعال بودن فیلد بدون حذف تعریف                      |
| sort_order    | ترتیب نمایش در فرم و خروجی                                    |
| options       | گزینه‌های select و multi_select                               |
| settings      | فضای توسعه‌پذیر برای تنظیمات آینده                            |

**قانون حیاتی field_id:** پس از استفاده یک field_id در Productها، این شناسه باید پایدار بماند. تغییر نام یا عنوان فیلد مجاز است، اما تولید UUID جدید برای همان فیلد باعث قطع ارتباط با مقادیر قدیمی می‌شود.

**۴. مدل Product و نحوه ذخیره مقادیر**

Product در نسخه فعلی فقط یک فیلد ثابت اصلی به نام name دارد. ارتباط آن با Categoryها از طریق جدول product_categories برقرار می‌شود و مقادیر مشخصات داینامیک در ستون attributes از نوع JSONB نگه‌داری می‌شوند.

**Value Object مقدار فیلد کالا**

```
class ProductAttributeValue(BaseModel):
    category_id: int
    field_id: UUID
    value: Any | None = None
```

در نتیجه هر مقدار ذخیره‌شده به‌تنهایی مشخص می‌کند متعلق به کدام دسته‌بندی و کدام فیلد است. این تصمیم علاوه بر خوانایی دیتابیس، برای گروه‌بندی در Frontend نیز بسیار مفید است.

```
[
  {
    "category_id": 2,
    "field_id": "11111111-1111-4111-8111-111111111111",
    "value": 8
  },
  {
    "category_id": 3,
    "field_id": "33333333-3333-4333-8333-333333333333",
    "value": "China"
  }
]
```

**۵. قراردادهای DTO و جریان داده**

CreateProductDto و UpdateProductDto از یک ساختار واحد برای مقادیر پویا استفاده می‌کنند:

```
name: str
category_ids: list[int]
attributes: list[ProductAttributeValue]
```

در سمت خروجی، ProductDto شامل لیست Categoryها و لیست fields است. هر آیتم در fields از ProductDynamicFieldDto استفاده می‌کند که تمام تعریف DynamicFieldDefinition را به‌اضافه category_id، category_name و value در اختیار Frontend قرار می‌دهد.

```
ProductDynamicFieldDto = DynamicFieldDefinition +
  category_id
  category_name
  value
```

**۶. فرایند ساخت کالا**

CreateProductCommandHandler فرایند ساخت را در چند مرحله انجام می‌دهد:

1\. حذف category_idهای تکراری از ورودی.

2\. خواندن Categoryهای انتخاب‌شده از دیتابیس.

3\. بررسی اینکه همه Categoryها واقعاً وجود دارند.

4\. جمع‌آوری تمام فیلدهای فعال هر Category با کلید ترکیبی (category_id, field_id).

5\. بررسی Attributeهای تکراری.

6\. بررسی اینکه category_id هر Attribute در دسته‌های انتخاب‌شده وجود دارد.

7\. بررسی اینکه field_id واقعاً متعلق به همان Category باشد.

8\. اعمال default_value برای فیلدهایی که ارسال نشده‌اند.

9\. جلوگیری از ثبت در صورت نبود مقدار یک فیلد required بدون Default.

10\. ساخت Product، اتصال Categoryها و ذخیره attributes.

**نمونه Payload ساخت کالا**

```
{
  "name": "دوربین مداربسته مدل X200",
  "category_ids": [2, 3],
  "attributes": [
    {
      "category_id": 2,
      "field_id": "11111111-1111-4111-8111-111111111111",
      "value": 8
    },
    {
      "category_id": 2,
      "field_id": "22222222-2222-4222-8222-222222222222",
      "value": "ip"
    },
    {
      "category_id": 3,
      "field_id": "33333333-3333-4333-8333-333333333333",
      "value": "China"
    }
  ]
}
```

**رفتار Default:** اگر رزولوشن یا نوع دوربین در Category مقدار پیش‌فرض داشته باشند و کاربر آنها را نفرستد، Handler مقدار Default را به‌صورت ProductAttributeValue واقعی داخل Product ذخیره می‌کند؛ بنابراین تغییر Default در آینده، کالاهای قبلی را تغییر نمی‌دهد.

**۷. فرایند خواندن و نمایش کالا**

GetProductByIdQueryHandler فقط JSON خام را برنمی‌گرداند. این Handler تعریف فیلدها را از Category و مقدار واقعی را از Product.attributes ترکیب می‌کند و یک خروجی مناسب برای UI می‌سازد.

```
Category Field Definition
        +
Product Attribute Value
        ↓
ProductDynamicFieldDto
        ↓
category_id + category_name + field metadata + value
```

**نمونه خروجی یک فیلد**

```
{
  "field_id": "11111111-1111-4111-8111-111111111111",
  "category_id": 2,
  "category_name": "مشخصات فنی دوربین",
  "name": "resolution",
  "title": "رزولوشن",
  "field_type": "decimal",
  "unit": "MP",
  "required": true,
  "value": 8
}
```

به همین دلیل Frontend می‌تواند بدون حدس‌زدن، فیلدها را بر اساس category_id یا category_name گروه‌بندی و نمایش دهد.

**۸. فرایند ویرایش و حذف**

**Update**

Update در نسخه فعلی به‌صورت Replace کامل طراحی شده است. یعنی name، لیست Categoryها و کل attributes ارسالی، وضعیت جدید Product محسوب می‌شوند. Handler همان قواعد Create را دوباره اجرا می‌کند و سپس مقادیر قبلی را جایگزین می‌کند.

**معنای Replace کامل:** اگر یک Category یا Attribute در درخواست Update وجود نداشته باشد، سیستم آن را «بدون تغییر» در نظر نمی‌گیرد؛ بلکه آن جزء از وضعیت جدید حذف شده است. برای PATCH جزئی می‌توان بعداً Endpoint جدا طراحی کرد.

**Delete**

DeleteProductCommandHandler Product را با id پیدا می‌کند و در صورت وجود از Repository حذف می‌کند. رابطه‌های جدول واسط product_categories به کمک ondelete="CASCADE" پاک می‌شوند. Commit همچنان در TransactionBehavior انجام می‌شود.

**۹. سناریوی واقعی تست: دوربین مداربسته**

در تست فعلی دو Category ساخته شده‌اند و یک Product هم‌زمان به هر دو متصل می‌شود.

| **Category**             | **field_id** | **فیلد**             | **نمونه مقدار** |
| ------------------------ | ------------ | -------------------- | --------------- |
| مشخصات فنی دوربین (id=2) | 1111…        | resolution           | 8 MP            |
| مشخصات فنی دوربین (id=2) | 2222…        | camera_type          | ip              |
| اطلاعات بازرگانی (id=3)  | 3333…        | country_of_origin    | China           |
| اطلاعات بازرگانی (id=3)  | 4444…        | import_tracking_code | IMP-2026-20001  |

خروجی Read نیز این چهار فیلد را همراه category_id و category_name برمی‌گرداند؛ بنابراین UI می‌تواند آنها را به دو بخش مجزا تقسیم کند: «مشخصات فنی دوربین» و «اطلاعات بازرگانی».

**۱۰. راهنمای Frontend**

Frontend بهتر است در ثبت یا ویرایش کالا این جریان را دنبال کند:

1\. کاربر یک یا چند Category را انتخاب می‌کند.

2\. Frontend تعریف فیلدهای Categoryهای انتخاب‌شده را دریافت می‌کند.

3\. فیلدها بر اساس Category و sort_order گروه‌بندی می‌شوند.

4\. بر اساس field_type، کنترل مناسب ساخته می‌شود: TextBox، Number، Checkbox، Select و غیره.

5\. required، options، placeholder، unit و سایر Metadataها در UI استفاده می‌شوند.

6\. در Submit، برای هر مقدار category_id + field_id + value ارسال می‌شود.

7\. در صفحه نمایش/ویرایش، خروجی ProductDto مستقیماً قابل گروه‌بندی بر اساس category_id یا category_name است.

**نگاشت پیشنهادی field_type به کنترل UI**

| **field_type**    | **کنترل پیشنهادی**     |
| ----------------- | ---------------------- |
| string            | Text Input             |
| integer / decimal | Number Input           |
| boolean           | Checkbox / Switch      |
| date / datetime   | Date / DateTime Picker |
| select            | Dropdown / Select      |
| multi_select      | Multi Select           |

**۱۱. قوانین یکپارچگی داده و نکات مهم**

• field_id باید پایدار و غیرقابل استفاده مجدد برای یک مفهوم متفاوت باشد.

• هر ProductAttributeValue باید هم category_id و هم field_id صحیح داشته باشد.

• Backend اجازه نمی‌دهد field_id یک Category با category_id دسته دیگری ارسال شود.

• Attribute تکراری با همان زوج (category_id, field_id) در Create/Update رد می‌شود.

• فقط فیلدهای active در ساخت و نمایش فعلی لحاظ می‌شوند.

• Product قدیمی که با فرمت dict قبلی ذخیره شده باشد باید در محیط توسعه حذف یا migrate شود؛ Getter جدید انتظار لیست Objectها را دارد.

• Category ↔ Product رابطه واقعی است و در JSONB نگه‌داری نمی‌شود.

**اعتبارسنجی‌هایی که اکنون انجام می‌شوند**

| **قانون**                  | **وضعیت فعلی**              |
| -------------------------- | --------------------------- |
| وجود Category              | پیاده‌سازی شده              |
| تطابق field_id با Category | پیاده‌سازی شده              |
| Duplicate Attribute        | پیاده‌سازی شده              |
| required                   | پیاده‌سازی شده              |
| default_value              | پیاده‌سازی شده              |
| is_active                  | پیاده‌سازی شده              |
| field_type واقعی مقدار     | هنوز کامل نشده              |
| min_value / max_value      | هنوز کامل نشده              |
| min_length / max_length    | هنوز کامل نشده              |
| regex                      | هنوز کامل نشده              |
| options برای select        | هنوز کامل نشده              |
| unique                     | هنوز کامل نشده              |
| readonly / auto_generate   | قوانین کامل هنوز اضافه نشده |

**۱۲. وضعیت فعلی و توسعه‌های بعدی**

ماژول Product از نظر ساختار اصلی CRUD و مدل داینامیک تکمیل شده است. Entity، Repository، Unit of Work، DTOها، Command/Queryها، Handlerها و APIهای اصلی وجود دارند و سناریوی چند Category و مقدارهای پویا با موفقیت تست شده است.

**پیشنهادهای منطقی برای فاز بعد**

• استخراج منطق تکراری اعتبارسنجی Create و Update به یک ProductDynamicFieldValidator مستقل.

• اعتبارسنجی کامل نوع داده، min/max، regex، options، unique، readonly و auto_generate.

• تعریف قواعد تغییر Category بعد از وجود Productهای وابسته و نحوه برخورد با Attributeهای یتیم.

• افزودن واحد شمارش کالا به‌عنوان مفهوم ثابت یا Entity مستقل در صورت نیاز موجودی و گردش انبار.

• افزودن Query لیست کالاها، فیلتر و جست‌وجو با استفاده از show_in_list و فیلدهای قابل جست‌وجو.

• طراحی PATCH در صورت نیاز به ویرایش جزئی به‌جای Replace کامل PUT.

• بهبود Responseهای Create/Update برای برگرداندن DTO به‌جای Entity خام.

**چک‌لیست توسعه‌دهنده**

• قبل از ساخت Product، Category و field_idهای مورد نیاز باید وجود داشته باشند.

• در Payload هر Attribute، category_id و field_id را با هم ارسال کن.

• برای Update همیشه کل وضعیت جدید را بفرست مگر اینکه PATCH جداگانه اضافه شود.

• در Read از ProductDto استفاده کن؛ خروجی آن برای UI آماده و گروه‌بندی‌پذیر است.

• هیچ‌گاه مقدار Product را داخل DynamicFieldDefinition ذخیره نکن؛ Definition و Value دو مفهوم جدا هستند.

**جمع‌بندی:** معماری فعلی اجازه می‌دهد کالاها با حداقل فیلد ثابت، به هر تعداد Category متصل شوند و مشخصات متفاوت خود را بدون تغییر Schema اصلی Product ذخیره کنند. Category قرارداد و تعریف را نگه می‌دارد؛ Product مقدار واقعی را. این جداسازی هسته توسعه‌پذیری ماژول انبار است.