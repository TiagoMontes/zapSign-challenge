# Repository Guidelines

## Architecture Principles
- **Clean Architecture**: Clear separation of concerns with dependency inversion
- **SOLID Principles**: Single Responsibility, Open/Closed, Liskov Substitution, Interface Segregation, Dependency Inversion

## Project Structure & Module Organization
- Root: `compose.yaml`, `Dockerfile`, `Makefile`, `requirements.txt`, `.env.example`, `BACKEND_DELIVERY_PLAN.md`.
- **Clean Architecture Structure** (after bootstrap):
  ```
  core/                 # Main application module
  ├── entities/         # Business entities and rules
  │   ├── __init__.py
  │   ├── user.py
  │   ├── document.py
  │   └── company.py
  ├── use_cases/        # Application business logic
  │   ├── __init__.py
  │   ├── create_user.py
  │   ├── sign_document.py
  │   └── analyze_document.py
  ├── interfaces/       # Contracts and abstractions
  │   ├── __init__.py
  │   ├── repositories.py  # Repository interfaces
  │   ├── services.py      # External service interfaces
  │   └── dtos.py          # Data Transfer Objects
  └── frameworks/       # External frameworks and infrastructure
      ├── django/       # Django-specific implementations
      │   ├── models.py     # Django ORM models
      │   ├── serializers.py # DRF serializers
      │   ├── views.py      # DRF viewsets
      │   ├── urls.py       # URL routing
      │   └── admin.py      # Django admin
      ├── repositories.py   # Repository implementations
      └── external/         # Third-party integrations
  ```
- **Additional modules**: Follow same Clean Architecture structure pattern
- **Django Configuration**: `config/` (settings, urls, wsgi/asgi)
- **Tests**: `core/tests/` organized by layer (`test_entities/`, `test_use_cases/`, `test_frameworks/`)
- **Assets**: static/media folders configured later (`STATIC_ROOT=staticfiles`, `media/`)

## Build, Test, and Development Commands
- `make env` — copy `.env.example` to `.env` if missing.
- `make build` — build Docker images.
- `make bootstrap` — run `django-admin startproject config .` (first time).
- `make up` / `make down` — start/stop services.
- `make web/sh` — open a shell in the web container.
- `make manage cmd=migrate` — run Django management commands.
- `make test` — run Django tests via `manage.py test`.

## Coding Style & Naming Conventions
- Python 3.12, PEP 8, 4-space indentation.
- **Entities Layer**:
  - Business entities: `PascalCase` (e.g., `User`, `Document`, `Company`)
  - Entity methods: `snake_case` (e.g., `calculate_risk()`, `is_expired()`)
- **Use Cases Layer**:
  - Use case classes: `PascalCase` + `UseCase` (e.g., `CreateUserUseCase`, `SignDocumentUseCase`)
  - Use case methods: `execute()` as main entry point
- **Interfaces Layer**:
  - Repository interfaces: `I` + `PascalCase` + `Repository` (e.g., `IUserRepository`, `IDocumentRepository`)
  - Service interfaces: `I` + `PascalCase` + `Service` (e.g., `INotificationService`)
  - DTOs: `PascalCase` + `DTO` (e.g., `CreateUserDTO`, `DocumentResponseDTO`)
- **Frameworks Layer**:
  - Django Models: `PascalCase` + `Model` (e.g., `UserModel`, `DocumentModel`)
  - Serializers: `PascalCase` + `Serializer` (e.g., `UserSerializer`)
  - ViewSets: `PascalCase` + `ViewSet` (e.g., `UserViewSet`)
  - Repository implementations: `PascalCase` + `Repository` (e.g., `UserRepository`)
- **General**:
  - Functions/variables: `snake_case`
  - Constants: `UPPER_SNAKE_CASE`
  - Modules: `snake_case` (e.g., `core`, `auth_service`)
- **URLs**: prefer `kebab-case` paths; DRF routes under `/api/`

## Clean Architecture Layers

### **1. Entities (Business Logic)**
- **Pure business rules** independent of frameworks
- **No external dependencies** (no imports from Django, DRF, etc.)
- **Domain models** with behavior and validation
- **Example**: User entity with validation rules, Document with business methods

### **2. Use Cases (Application Logic)**
- **Orchestrate business flows** using entities and interfaces
- **Depend only on entities and interfaces** (dependency inversion)
- **One use case per business operation**
- **Example**: CreateUserUseCase, SignDocumentUseCase, AnalyzeDocumentUseCase

### **3. Interfaces (Contracts)**
- **Abstract interfaces** for external dependencies
- **Repository contracts** for data access
- **Service contracts** for external integrations
- **DTOs** for data transfer between layers

### **4. Frameworks (Infrastructure)**
- **Django/DRF implementations** of interfaces
- **Database access** via ORM
- **External API integrations**
- **Web controllers** (ViewSets)

## SOLID Principles Implementation
- **Single Responsibility**: Each class has one reason to change
  - Entities handle business rules only
  - Use cases handle one business flow only
  - Repositories handle data access only
- **Open/Closed**: Use interfaces for extension without modification
  - Repository interfaces allow different implementations
  - Service interfaces allow different external integrations
- **Liskov Substitution**: Interface implementations are interchangeable
- **Interface Segregation**: Small, focused interfaces
  - Separate interfaces for different concerns
- **Dependency Inversion**: High-level modules depend on abstractions
  - Use cases depend on repository interfaces, not implementations
  - Frameworks implement interfaces defined in inner layers

## Testing Guidelines
- **TDD Workflow**: All implementations must follow Test-Driven Development:
  1. **Red**: Write failing tests first
  2. **Green**: Implement minimal code to make tests pass
  3. **Refactor**: Improve code while keeping tests green
- **Testing Strategy by Layer**:
  - **Entity Tests** (`core/tests/test_entities/`):
    - Pure unit tests for business logic
    - No external dependencies or mocks needed
    - Test business rules and validations
  - **Use Case Tests** (`core/tests/test_use_cases/`):
    - Test business flows with mocked interfaces
    - Verify use case orchestration
    - Use dependency injection with mocks
  - **Framework Tests** (`core/tests/test_frameworks/`):
    - Test Django models, serializers, views
    - Integration tests with database
    - API endpoint tests using DRF test client
  - **Integration Tests** (`core/tests/test_integration/`):
    - End-to-end workflow tests
    - Real implementations with test database
- **Test Isolation**: Use dependency injection and mocking appropriately
- **Test Data**: Factory pattern for test data creation (e.g., `factory_boy`)
- **Coverage**: Focus on entities and use cases (business critical logic)
- Run tests: `make test` (Django test runner) or `pytest`

## Dependency Flow Rules
- **Entities**: No dependencies on outer layers
- **Use Cases**: Can depend on Entities and Interfaces only
- **Interfaces**: Can depend on Entities only (for DTOs and contracts)
- **Frameworks**: Can depend on all inner layers, implements interfaces

## Commit & Pull Request Guidelines
- **Commit Format**: Use aspas simples com quebra literal para commits multi-linha:
  ```bash
  git commit -m 'type(scope): brief description

  - detailed change 1
  - detailed change 2
  - detailed change 3'
  ```
- **Semantic commit types**:
  - `feat(scope): add new feature`
  - `fix(scope): fix bug or issue`
  - `chore(scope): maintenance, deps, config`
  - `docs(scope): documentation updates`
  - `test(scope): add or update tests`
  - `refactor(scope): code restructure without behavior change`
- **Scope examples**: `api`, `core`, `dev`, `deploy`, `auth`, `entities`, `use-cases`, `frameworks`
- **Format example**:
  ```bash
  git commit -m 'feat(entities): add document signer management

  - implement add_signer method in Document entity
  - add business rules for signer assignment
  - include validation for duplicate signers'
  ```
- PRs: clear description, steps to test, linked issues, and screenshots for UI.

## Dependency Management
- **Required packages** for Clean Architecture:
  ```
  # Core
  django>=4.2
  djangorestframework>=3.14
  
  # Dependency injection
  django-injector>=0.2.0
  
  # Data validation and serialization
  dataclasses-json>=0.5.0
  
  # Testing
  factory-boy>=3.2.0
  pytest-django>=4.5.0
  ```

## Security & Configuration Tips
- Never commit `.env` or secrets; use `.env.example` as reference.
- Required envs: `POSTGRES_*`, `DJANGO_SECRET_KEY`, `DJANGO_DEBUG`, `DB_HOST=db`.
- Rotate keys and set `DJANGO_DEBUG=0` for non-dev environments.