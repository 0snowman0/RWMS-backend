**راهنمای عملی Mediator**

راهنمای استفاده و توسعه برای برنامه‌نویس پروژه — نسخه Generic و Type-Safe

این سند برای استفاده روزمره و توسعه آینده نوشته شده است؛ تمرکز آن روی «چطور از سیستم استفاده کنیم» است، نه جزئیات پیاده‌سازی داخلی.

Command / Query • Handler • Pipeline Behavior • DI & Resolver

# **راهنمای سریع این سند**

اگر چند ماه بعد به پروژه برگشتید، از این بخش شروع کنید. هر موضوع شما را مستقیم به تصمیمی که برای توسعه لازم دارید هدایت می‌کند.

| **1**  | تصویر کلی: وقتی mediator.send() اجرا می‌شود چه اتفاقی می‌افتد؟          |
| ------ | ----------------------------------------------------------------------- |
| **2**  | افزودن Command یا Query جدید همراه با IRequest\[TResponse\] و Type Flow |
| **3**  | افزودن Handler و دریافت Dependency در Constructor                       |
| **4**  | استفاده از Mediator در Controller                                       |
| **5**  | افزودن Behavior جدید و تعیین Policy اجرا                                |
| **6**  | Skip / Require کردن Behavior برای یک Request خاص                        |
| **7**  | Transaction، SaveChanges و مرزهای Commit                                |
| **8**  | Resolver و اضافه کردن Dependency جدید                                   |
| **9**  | پوشه‌بندی چندلایه و Loaderها                                            |
| **10** | خطاهای رایج و چک‌لیست توسعه                                             |

# **1\. تصویر کلی سیستم**

Mediator نقطه واسط بین Controller و منطق Use Case است. Controller فقط Request مناسب را می‌سازد و آن را برای Mediator می‌فرستد؛ هر Request با IRequest\[TResponse\] نوع خروجی خود را نیز مشخص می‌کند. Mediator بر اساس نوع Request، Handler و Behaviorهای لازم را اجرا می‌کند و همان TResponse را به Controller برمی‌گرداند.

| **Controller** | **Request** | **Mediator** | **Behaviors** | **Handler** | **TResponse** |
| -------------- | ----------- | ------------ | ------------- | ----------- | ------------- |

**قاعده اصلی —** Controller نباید مستقیماً Handler را بسازد یا صدا بزند. ورودی باید به شکل Command/Query به mediator.send(...) تحویل داده شود.

| **موضوع**                 | **کاربرد برای برنامه‌نویس**                                                                                        |
| ------------------------- | ------------------------------------------------------------------------------------------------------------------ |
| **IMediator**             | ورودی اصلی سیستم در Controller؛ send(request) را اجرا می‌کند و TResponse همان Request را برمی‌گرداند.              |
| **IRequest\[TResponse\]** | قرارداد Request تایپ‌سیف؛ هر Command/Query از طریق TResponse اعلام می‌کند mediator.send(...) چه نوع خروجی‌ای دارد. |
| **IRequestHandler**       | قرارداد Handler؛ نوع Request و نوع Result/Response را به‌صورت Generic مشخص می‌کند.                                 |
| **IPipelineBehavior**     | قرارداد Behaviorهایی مثل Logging، Validation، Performance و Transaction.                                           |
| **RequestType**           | مشخص می‌کند Request از نوع COMMAND یا QUERY است.                                                                   |
| **BehaviorType**          | شناسه استاندارد Behaviorها؛ برای Policy، Skip و Require استفاده می‌شود.                                            |
| **IServiceResolver**      | Dependencyهای موردنیاز Handler/Behavior را بر اساس Type Annotation در Constructor تأمین می‌کند.                    |

# **2\. ساخت Request جدید: Command یا Query**

هر Use Case یک Request مشخص دارد. Request علاوه بر داده‌های موردنیاز Use Case، نوع خروجی خود را نیز با IRequest\[TResponse\] اعلام می‌کند. برای عملیات تغییردهنده داده معمولاً COMMAND و برای خواندن داده معمولاً QUERY استفاده می‌شود.

• Command: ایجاد، ویرایش، حذف یا عملیاتی که معمولاً نیاز به Transaction دارد.

• Query: خواندن داده؛ به‌صورت پیش‌فرض Transaction ندارد.

• Request داده موردنیاز Use Case را حمل می‌کند و با IRequest\[TResponse\] نوع Response را برای Type Checker مشخص می‌کند؛ منطق اصلی در Handler قرار می‌گیرد.

```
@request_type(RequestType.COMMAND)
@dataclass(frozen=True, slots=True)
class CreateUserCommand(
    IRequest[BaseResponse[UserDto]]
):
    data: UserCustomDto
```

**نکته — دو چیز روی Request مستقل از هم هستند: @request_type(...) Policy اجرایی Command/Query را مشخص می‌کند؛ IRequest\[TResponse\] نوع خروجی را برای Type Checker مشخص می‌کند. هر دو لازم‌اند.**

# **3\. ساخت Handler**

برای هر Request فقط Handler مربوط به همان Use Case را تعریف کنید. ارتباط Request و Handler با @handler_for(...) مشخص می‌شود و Loader آن را به Registry معرفی می‌کند. نوع خروجی Handler باید با TResponse تعریف‌شده روی IRequest همان Request هماهنگ باشد.

```
@handler_for(CreateUserCommand)
class CreateUserCommandHandler(
    IRequestHandler[
        CreateUserCommand,
        BaseResponse[UserDto],
    ]
):
    def __init__(
        self,
        uow: IUnitOfWork,
        mapper: IMapper,
    ):
        self._uow = uow
        self._mapper = mapper

    async def handle(
        self,
        request: CreateUserCommand,
    ) -> BaseResponse[UserDto]:

        user = self._mapper.map(
            request.data,
            User,
        )

        await self._uow.users.add(user)

        user_dto = self._mapper.map(
            user,
            UserDto,
        )

        return BaseResponse[UserDto].success(
            data=user_dto,
            message="User created successfully.",
        )
```

| **موضوع**                                 | **کاربرد برای برنامه‌نویس**                                                                                 |
| ----------------------------------------- | ----------------------------------------------------------------------------------------------------------- |
| **@handler_for(CreateUserCommand)**       | به Loader اعلام می‌کند این کلاس Handler مربوط به CreateUserCommand است.                                     |
| **IRequestHandler\[Request, TResponse\]** | نوع ورودی و خروجی Handler را روشن می‌کند؛ TResponse باید با IRequest\[TResponse\] همان Request هماهنگ باشد. |
| **Constructor**                           | محل اعلام Dependencyهای موردنیاز Handler؛ مثل IUnitOfWork یا IMapper.                                       |
| **handle(...)**                           | منطق Use Case را اجرا می‌کند و همان TResponse تعریف‌شده را برمی‌گرداند.                                     |

**برای Handlerهای Command —** در حالت معمول داخل Handler، save_changes() نزنید؛ TransactionBehavior در انتهای Pipeline Commit را انجام می‌دهد.

# **4\. گرفتن Dependency داخل Handler**

Handler می‌تواند هر Dependency ثبت‌شده در ServiceResolver را از طریق Constructor دریافت کند. نوع Dependency باید با Type Annotation مشخص باشد.

```
def __init__(
    self,
    uow: IUnitOfWork,
    mapper: IMapper,
    token_service: ITokenService,
):
    ...
```

Factory نوع هر پارامتر Constructor را می‌خواند و همان Interface را از ServiceResolver Resolve می‌کند. بنابراین Handler نباید خودش Session، Repository یا Service را بسازد.

**اگر Dependency جدید لازم شد —** ابتدا Interface/Service را در DI پروژه آماده کنید و سپس همان Interface را داخل get_service_resolver(...) ثبت کنید. بعد از آن هر Handler یا Behavior می‌تواند آن را در Constructor درخواست کند.

# **5\. استفاده در Controller**

در Endpoint فقط MediatorDependency را دریافت کنید، Request مناسب را بسازید و send را صدا بزنید. اگر Request به‌صورت IRequest\[TResponse\] تعریف شده باشد، IDE/Pylance نوع result را از روی همان TResponse تشخیص می‌دهد.

```
@router.post('/mediator-test')
async def create_user(
    request: UserCustomDto,
    mediator: MediatorDependency,
):
    command = CreateUserCommand(
        data=request,
    )

    result = await mediator.send(
        command
    )

    # IDE: BaseResponse[UserDto]
    return result
```

**Scope صحیح — Mediator را Global نکنید. MediatorDependency باید در هر Endpointی که به آن نیاز دارد دریافت شود تا همان UnitOfWork/Session مربوط به همان HTTP Request استفاده شود. اگر Hover روی result مقدار Any نشان داد، ابتدا بررسی کنید Request از IRequest\[TResponse\] ارث برده باشد و امضای IMediator.send و Mediator.send تایپ Generic را حفظ کرده باشند.**

# **6\. Behaviorها چه هستند؟**

Behaviorها عملیات مشترکی هستند که قبل و/یا بعد از Handler اجرا می‌شوند. ترتیب پیش‌فرض Pipeline باید مشخص و قابل پیش‌بینی بماند.

| **Logging** | **Performance** | **Validation** | **Transaction** | **Handler** |
| ----------- | --------------- | -------------- | --------------- | ----------- |

| **موضوع**       | **کاربرد برای برنامه‌نویس**                                                        |
| --------------- | ---------------------------------------------------------------------------------- |
| **Logging**     | ثبت اطلاعات Request و Result. فعلاً می‌تواند ساده باشد.                            |
| **Performance** | محل اندازه‌گیری زمان یا بررسی کندی؛ فعلاً می‌تواند Pass-through باشد.              |
| **Validation**  | محل اعتبارسنجی عمومی Request؛ فعلاً می‌تواند Pass-through باشد.                    |
| **Transaction** | برای Use Caseهای تراکنشی؛ Handler را اجرا می‌کند و در پایان save_changes() می‌زند. |

# **7\. اگر Behavior جدید خواستیم اضافه کنیم**

برای اضافه کردن Behavior جدید، برنامه‌نویس فقط باید چهار نقطه را بررسی کند: نوع Behavior، کلاس Behavior، محل Load شدن و Policy اجرا.

• یک مقدار جدید به BehaviorType اضافه کنید، اگر نوع موردنظر هنوز وجود ندارد.

• کلاس Behavior را از IPipelineBehavior مشتق کنید و با @behavior(BehaviorType.X) علامت بزنید.

• فایل را زیر Packageای قرار دهید که BehaviorLoader به‌صورت recursive آن را Scan می‌کند.

• اگر باید به‌صورت پیش‌فرض برای Command یا Query اجرا شود، آن را در MEDIATOR_BEHAVIOR_POLICIES قرار دهید. اگر فقط برای چند Request خاص است، لازم نیست Default Policy را تغییر دهید؛ از @require_behaviors(...) استفاده کنید.

```
@behavior(BehaviorType.PERFORMANCE)
class PerformanceBehavior(IPipelineBehavior):
    async def handle(
        self,
        request,
        next_handler: NextHandler,
    ):
        return await next_handler()
```

# **8\. Policy پیش‌فرض و Skip / Require**

BehaviorPolicyResolver بر اساس RequestType، Behaviorهای پیش‌فرض را انتخاب می‌کند و سپس Skip/Require همان Request را اعمال می‌کند.

| **موضوع**   | **کاربرد برای برنامه‌نویس**                      |
| ----------- | ------------------------------------------------ |
| **COMMAND** | Logging → Performance → Validation → Transaction |
| **QUERY**   | Logging → Performance → Validation               |

```
@skip_behaviors(BehaviorType.TRANSACTION)
@request_type(RequestType.COMMAND)
class SendSmsCommand(
    IRequest[BaseResponse[None]]
):
    ...

@require_behaviors(BehaviorType.TRANSACTION)
@request_type(RequestType.QUERY)
class SpecialQuery(
    IRequest[BaseResponse[SomeDto]]
):
    ...
```

**تعارض Policy —** یک Behavior را هم‌زمان Skip و Require نکنید. این وضعیت خطای Configuration محسوب می‌شود و باید اصلاح شود.

# **9\. Transaction و SaveChanges**

در Commandهای عادی، Handler عملیات Repository را انجام می‌دهد و Commit نهایی توسط TransactionBehavior انجام می‌شود. این روش باعث می‌شود مرز Transaction در Pipeline متمرکز باشد.

| **Handler: add/update/delete** | **return result** | **TransactionBehavior** | **save_changes()** |
| ------------------------------ | ----------------- | ----------------------- | ------------------ |

**استثنای آگاهانه —** اگر یک Use Case واقعاً نیاز دارد بخشی از عملیات زودتر Commit شود، Handler می‌تواند save_changes() را در نقطه مشخص صدا بزند؛ اما از آن لحظه عملیات قبلی دیگر با خطای بعدی Rollback نمی‌شود. این باید یک تصمیم Business Boundary باشد، نه عادت.

برای عملیات جانبی مثل SMS/Email که Transaction دیتابیس مفهومی ندارد، می‌توان TransactionBehavior را برای همان Command با @skip_behaviors(...) حذف کرد.

# **10\. ServiceResolver و اضافه کردن Service جدید**

ServiceResolver پل بین Factoryهای Mediator و DI برنامه است. HandlerFactory و BehaviorFactory فقط نوع Constructor را می‌بینند و Resolver نمونه همان Dependency را برمی‌گرداند.

```
resolver.add(IUnitOfWork, uow)
resolver.add(IMapper, mapper)
resolver.add(ITokenService, token_service)
resolver.add(IDatabaseRoutineExecutor, routine_executor)
```

• Dependency را با Interface آن ثبت کنید، نه با ساختن مستقیم در Handler.

• Type Annotation Constructor باید دقیق باشد؛ Factory از همان Type برای Resolve استفاده می‌کند.

• UnitOfWork باید همان instance مربوط به Request باشد تا Handler و TransactionBehavior روی یک Session کار کنند.

# **11\. پوشه‌بندی چندلایه**

پروژه می‌تواند Featureها و Handlerها را در چندین سطح پوشه دسته‌بندی کند. Loader از ریشه Core.Application.Features به‌صورت recursive Scan می‌کند، بنابراین عمق پوشه محدودیت معماری ایجاد نمی‌کند.

```
Core/Application/Features/
  Products/
    Inventory/
      Warehouses/
        Handlers/
          Commands/
            ...
```

**شرط مهم —** مسیرها باید Python package قابل import باشند. برای ساختار شفاف و قابل‌اعتماد، پوشه‌های Package را با \__init_\_.py نگه دارید.

# **12\. خطاهای رایج**

| **موضوع**                                           | **کاربرد برای برنامه‌نویس**                                                                                                                                     |
| --------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Handler پیدا نمی‌شود**                            | @handler_for را بررسی کنید؛ Handler باید زیر ریشه‌ای باشد که HandlerLoader آن را Load می‌کند.                                                                   |
| **RequestType پیدا نمی‌شود**                        | @request_type(RequestType.COMMAND/QUERY) را روی Request بررسی کنید.                                                                                             |
| **Behavior پیدا نمی‌شود**                           | @behavior(...)، BehaviorType و Package Load شده توسط BehaviorLoader را بررسی کنید.                                                                              |
| **Dependency 'args' ... must have type annotation** | Factory باید \*args و \*\*kwargs را نادیده بگیرد؛ Behavior/Handler بدون Constructor نباید به‌عنوان Dependency تفسیر شود.                                        |
| **Dependency resolve نمی‌شود**                      | Interface موردنظر را در ServiceResolver ثبت کنید و Type Annotation Constructor را با همان Interface تطبیق دهید.                                                 |
| **Commit اتفاق نمی‌افتد**                           | بررسی کنید Request از نوع COMMAND است، TransactionBehavior در Policy وجود دارد و Skip نشده است.                                                                 |
| result در Controller از نوع Any است                 | بررسی کنید Request از IRequest\[TResponse\] ارث برده باشد و هر دو IMediator.send و Mediator.send امضای request: IRequest\[TResponse\] -> TResponse داشته باشند. |

# **13\. چک‌لیست افزودن Use Case جدید**

• Request را زیر Features/.../Requests/Commands یا Queries بساز و از IRequest\[TResponse\] ارث بده.

• @request_type(RequestType.COMMAND/QUERY) را تعیین کن؛ این Decorator Policy اجرا را مشخص می‌کند.

• Handler را زیر Handlers/Commands یا Queries بساز و خروجی آن را با همان TResponse هماهنگ نگه دار.

• @handler_for(RequestClass) را روی Handler قرار بده.

• Dependencyها را فقط در Constructor و با Interface درخواست کن.

• در Command عادی save_changes() را داخل Handler تکرار نکن.

• در Controller فقط MediatorDependency بگیر و mediator.send(...) را صدا بزن؛ IDE باید result را به‌صورت TResponse واقعی تشخیص دهد.

• اگر Behavior خاصی لازم است، @skip_behaviors یا @require_behaviors را روی Request اعمال کن.