# RWMS-Backend — Agent Rules

## Project Context

This is the **RWMS (Relief Warehouse Management System)** backend — a FastAPI + PostgreSQL application built with **Clean Architecture**. The language is **Python 3** and all documentation is in **Farsi (FA)**.

---

## Architecture Rules

### Layer Structure (NEVER violate dependency direction)

```
Api  →  Configs  →  Core  ←  Infrastructure
```

- **Core** is the center — it has NO dependency on any other layer.
- **Infrastructure** depends on Core (implements its interfaces).
- **Api** depends on Core and Configs.
- **Configs** wires everything together.

### Layer Responsibilities

| Layer | Path | Allowed Dependencies |
|-------|------|---------------------|
| **Api** | `Api/` | Core, Configs (via DI) |
| **Configs** | `Configs/` | Core, Infrastructure (only for DI wiring) |
| **Core** | `Core/` | **NONE** — only stdlib and pydantic |
| **Infrastructure** | `Infrastructure/` | Core only |

### Import Rules

- **Core MUST NOT** import from `Api/`, `Configs/`, or `Infrastructure/`.
- **Infrastructure** implements Core's interfaces (`Core/Application/Contracts/`).
- Controllers should only depend on `MediatorDependency` and DTOs — never import Infrastructure directly.
- Exception: `Core/Domain/Models/user.py` currently imports from `Infrastructure.Persistence.Configs.PGdatabase` for `Base`. This is a known deviation — `Base` lives in `Core/Domain/Models/Base/base_models.py` and models should import from there.

---

## Coding Conventions

### General

- Use **type hints** everywhere (function signatures, return types, class attributes).
- Use `Mapped[]` and `mapped_column()` for SQLAlchemy models (SQLAlchemy 2.0 style).
- Use **Pydantic v2** `BaseModel` for DTOs and ViewModels.
- Use `@dataclass(frozen=True, slots=True)` for Request objects (Commands/Queries).
- All classes and methods should have **explicit return type annotations**.
- Prefer `Annotated[Type, Depends(...)]` pattern for FastAPI dependencies.

### Naming Conventions

- **Models:** PascalCase, singular (e.g., `User`, `Category`)
- **Tables:** auto-generated as lowercase plural (`users`, `categorys`)
- **DTOs:** `{Action}{Entity}Dto` (e.g., `CreateCategoryDto`, `UpdateCategoryDto`)
- **Commands:** `{Action}{Entity}Command` (e.g., `CreateCategoryCommand`)
- **Queries:** `{Action}{Entity}Query` (e.g., `GetCategoryByIdQuery`)
- **Handlers:** `{Command/Query}Handler` (e.g., `CreateCategoryCommandHandler`)
- **Repositories:** `I{Entity}Repository` (interface), `{Entity}Repository` (implementation)
- **Files:** snake_case (e.g., `create_category.py`, `category_repository.py`)

### Directory Naming

- Use **PascalCase** for directories (e.g., `Controllers/`, `Categories/`, `Commands/`)
- Version directories: `V1/`, `V2/`

### Response Pattern

- All handler responses MUST use `BaseResponse[T]` with its factory methods:
  - `BaseResponse.success(data=..., message=...)`
  - `BaseResponse.fail(message=..., errors=[...])`
  - `BaseResponse.not_found(message=...)`
  - `BaseResponse.validation_error(message=..., errors=[...])`
- Controllers convert with `to_api_response(result)`.

---

## Adding New Features — Checklist

When adding a new feature (e.g., a new entity), follow this exact order:

1. **Domain Model** → `Core/Domain/Models/{Feature}/` — inherit from `Base`
2. **Enums** (if needed) → `Core/Domain/Enums/{Feature}/`
3. **ViewModels** (if needed) → `Core/Domain/ViewModels/{Feature}/`
4. **DTOs** → `Core/Application/DTOs/{Feature}/`
5. **Repository Interface** → `Core/Application/Contracts/DataBases/Repositories/{Feature}/`
6. **Request objects** → `Core/Application/Features/{Feature}/Requests/Commands/` and `Queries/`
   - Decorate with `@request_type(RequestType.COMMAND)` or `@request_type(RequestType.QUERY)`
   - Use `@dataclass(frozen=True, slots=True)`
   - Extend `IRequest[BaseResponse[T]]`
7. **Handlers** → `Core/Application/Features/{Feature}/Handlers/Commands/` and `Queries/`
   - Decorate with `@handler_for(RequestClass)`
   - Inject dependencies via constructor (`IUnitOfWork`, `IMapper`, `ILogger`, etc.)
8. **Repository Implementation** → `Infrastructure/Persistence/Repositories/{Feature}/`
   - Extend `GenericRepository[Model]`
9. **Register in UnitOfWork** → Add property in both:
   - `Core/Application/Contracts/DataBases/UnitOfWorks/unit_of_works.py` (interface)
   - `Infrastructure/Persistence/UnitOfWorks/unit_of_works.py` (implementation)
10. **Controller** → `Api/Controllers/{Feature}/V1/`
    - Use `AppRouter(tags=["{Feature}"])`
    - Inject `MediatorDependency`
    - Return `to_api_response(result)`
11. **Create `__init__.py`** in every new directory.
12. **Alembic migration** → `alembic revision --autogenerate -m "description"`

---

## Mediator Pattern Rules

### Request Types

- **Commands** mutate state → get `LOGGING → PERFORMANCE → VALIDATION → TRANSACTION` behaviors
- **Queries** read state → get `LOGGING → PERFORMANCE → VALIDATION` behaviors

### Behavior Pipeline Order

The order in `Configs/Mediators/behavior_policy.py` is critical. **DO NOT** change the order without understanding the implications. Transaction MUST be the innermost behavior for commands.

### Handler Registration

- Handlers are auto-discovered from `Core.Application.Features` package.
- Behaviors are auto-discovered from `Core.Application.Mediators.Behaviors` package.
- No manual registration needed — just use the decorators.

---

## Database Rules

- Use **async** sessions (`AsyncSession`) everywhere except Alembic migrations.
- All models inherit from `Core/Domain/Models/Base/base_models.py:Base`.
- Use JSONB for dynamic/flexible data storage.
- Connection pool: `pool_size=10`, `max_overflow=20`.
- Alembic migration scripts location: `Infrastructure/Persistence/migration/`.

---

## API Versioning

- All routes are auto-prefixed with `/api/v1/` or `/api/v2/` based on their folder structure.
- Place V1 controllers in `Api/Controllers/{Feature}/V1/`.
- Place V2 controllers in `Api/Controllers/{Feature}/V2/`.
- Each controller file MUST export a `router` variable.

---

## Rate Limiting

- Default policy applies to all endpoints automatically.
- Override with `@rate_limit("policy_name")` decorator on endpoint functions.
- Policies are defined in `Configs/RateLimiting/rate_limit.py`.

---

## Logging

- Use `ILogger` (injected via `LoggerDependency`) — never use `print()` or stdlib `logging` directly.
- Per-request context (request_id, correlation_id, IP) is automatic via middleware.
- Logs batch-write to PostgreSQL, with file fallback if DB fails.

---

## DI / Service Registration

- To make a service available to Mediator handlers, decorate its factory with `@mediator_service(InterfaceType)` in `Configs/dependencies.py`.
- All dependency type aliases follow the pattern: `{Name}Dependency = Annotated[IInterface, Depends(factory)]`.

---

## Testing Endpoints

- Test/experimental endpoints go in `Api/Controllers/Test/V1/test.py`.
- SP/routine test endpoints go in `Api/Controllers/SP/V1/sp.py`.

---

## File Management

- Every directory must have an `__init__.py` file.
- Static assets (Swagger UI) live in `static/swagger-ui/`.
- Environment variables are in `.env` (gitignored). Reference template: `Documents/Settings/env.txt`.
