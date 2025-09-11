# Repository Guidelines

## Architecture Principles
- **Clean Architecture**: Clear separation of concerns with dependency inversion
- **SOLID Principles**: Single Responsibility, Open/Closed, Liskov Substitution, Interface Segregation, Dependency Inversion

## Project Structure & Module Organization
- Root: `compose.yaml`, `Dockerfile`, `Makefile`, `requirements.txt`, `.env.example`, `BACKEND_DELIVERY_PLAN.md`.
- Structure (Clean, simplificada):
  ```
  core/
  ├── domain/
  │   └── entities/                 # Pure domain entities (no Django)
  ├── use_cases/                    # Application business logic (interactors)
  ├── orm/
  │   ├── models.py                 # Django ORM models
  │   └── mappers.py                # Model ↔ Entity mapping
  ├── repositories/                 # Concrete repositories using Django ORM
  └── app/
      └── providers/                # Optional DI factories for use cases

  api/
  ├── serializers/                  # DRF serializers
  ├── views/                        # DRF viewsets/controllers
  └── routers.py                    # DRF router (mounted under /api)
  ```
- Additional modules: Follow the same pattern.
- Django Configuration: `config/` (settings, urls, wsgi/asgi). Migrations in `core/migrations/`.
- Tests: `tests/` organized por camada e fakes (`test_entities/`, `test_use_cases/`, `test_frameworks/`, `fakes/`).
- Assets: static/media folders configured later (`STATIC_ROOT=staticfiles`, `media/`).

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
- **Infra Layer**:
  - Django Models: `PascalCase` + `Model` (em `core/orm/models.py`)
  - Repositories: `PascalCase` + `Repository` (e.g., `UserRepository`)
- **API Layer**:
  - Serializers: `PascalCase` + `Serializer` (e.g., `UserSerializer`)
  - ViewSets: `PascalCase` + `ViewSet` (e.g., `UserViewSet`)
  - Controllers podem usar providers para instanciar use cases ou instanciar diretamente repositórios/use cases.
- **General**:
  - Functions/variables: `snake_case`
  - Constants: `UPPER_SNAKE_CASE`
  - Modules: `snake_case` (e.g., `core`, `auth_service`)
- **URLs**: prefer `kebab-case` paths; DRF routes under `/api/`

## Clean Layers (Simplified)

### **1. Domain (Entities)**
- **Pure business rules** independent of frameworks
- **No external dependencies** (no imports from Django, DRF, etc.)
- **Domain models** with behavior and validation
- **Example**: User entity with validation rules, Document with business methods

### **2. Use Cases (Application)**
- **Orchestrate business flows** using entities and repositories/services
- **Depend only on entities and injected collaborators** (constructor DI)
- **One use case per business operation**
- **Example**: CreateUserUseCase, SignDocumentUseCase, AnalyzeDocumentUseCase

### **3. Infra (ORM + Repositories)**
- **Concrete repositories** using Django ORM
- **External services** (clients) when needed

### **4. API (Web Layer)**
- **DRF controllers** (ViewSets) e serializers
- **Pode usar providers** para instanciar use cases

## SOLID Principles Implementation
- **Single Responsibility**: Each class has one reason to change
  - Entities: business rules only
  - Use cases: orchestration only
  - Repositories: data access only
- **Open/Closed**: Prefer extension via composition; troque implementações por DI quando necessário
- **Liskov Substitution**: Mantenha contratos de métodos consistentes entre implementações
- **Interface Segregation**: Classes focadas e coesas (métodos essenciais)
- **Dependency Inversion**: Use DI por construtor (injetando repositórios/serviços concretos)

## Testing Guidelines
- **TDD Workflow**: All implementations must follow Test-Driven Development:
  1. **Red**: Write failing tests first
  2. **Green**: Implement minimal code to make tests pass
  3. **Refactor**: Improve code while keeping tests green
- **Testing Strategy by Layer**:
  - **Entity Tests** (`tests/test_entities/`):
    - Pure unit tests for business logic
    - No external dependencies or mocks needed
    - Test business rules and validations
  - **Use Case Tests** (`tests/test_use_cases/`):
    - Testam fluxos com fakes em `tests/fakes/`
    - Verificam orquestração e regras sem banco de dados real
- **Test Isolation**: Use dependency injection and mocking appropriately
- **Test Data**: Factory pattern for test data creation (e.g., `factory_boy`)
- **Coverage**: Focus on entities and use cases (business critical logic)
- Run tests: `make test` (Django test runner) or `pytest`

## Dependency Flow Rules
- **Domain (Entities)**: Não dependem de camadas externas
- **Use Cases**: Dependem de Entities e recebem repositórios/serviços por DI
- **Infra (ORM/Repositories)**: Dependem de Django ORM e do domínio (mapeamento)
- **API**: Depende de Use Cases/Providers; não importa ORM diretamente

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
- **Scope examples**: `api`, `core`, `dev`, `deploy`, `auth`, `entities`, `use-cases`, `orm`, `repositories`
- **Format example**:
  ```bash
  git commit -m 'feat(entities): add document signer management

  - implement add_signer method in Document entity
  - add business rules for signer assignment
  - include validation for duplicate signers'
  ```
- PRs: clear description, steps to test, linked issues, and screenshots for UI.

## Dependency Management
- **Required packages**:
  ```
  # Core
  django>=4.2
  djangorestframework>=3.14

  # Testing
  factory-boy>=3.2.0
  pytest-django>=4.5.0
  ```

## Security & Configuration Tips
- Never commit `.env` or secrets; use `.env.example` as reference.
- Required envs: `POSTGRES_*`, `DJANGO_SECRET_KEY`, `DJANGO_DEBUG`, `DB_HOST=db`.
- Rotate keys and set `DJANGO_DEBUG=0` for non-dev environments.
