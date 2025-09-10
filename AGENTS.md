# Repository Guidelines

## Project Structure & Module Organization
- Root: `compose.yaml`, `Dockerfile`, `Makefile`, `requirements.txt`, `.env.example`, `BACKEND_DELIVERY_PLAN.md`.
- Django (after bootstrap):
  - `config/` (settings, urls, wsgi/asgi)
  - App modules (e.g., `core/`) with `models.py`, `serializers.py`, `views.py`, `urls.py`.
  - Tests colocated by app: `core/tests/test_*.py`.
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
- Modules and app names: `snake_case` (e.g., `core`, `analysis_service`).
- Classes (Models/Serializers/ViewSets): `PascalCase` (e.g., `CompanyDocument`).
- Functions/variables: `snake_case`; constants: `UPPER_SNAKE_CASE`.
- URLs: prefer `kebab-case` paths; DRF routes under `/api/v1/`.

## Testing Guidelines
- Use Django's test runner (`manage.py test`).
- Place tests under each app: `app/tests/test_*.py` using `TestCase`/`APITestCase`.
- Aim to cover models, serializers, viewsets, and critical flows (ZapSign, analysis).

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
- **Scope examples**: `api`, `core`, `dev`, `deploy`, `auth`, `models`
- **Format example**:
  ```bash
  git commit -m 'chore(dev): allow web to start before Django bootstrap

  - compose: fallback to python -m http.server when manage.py is absent
  - plan: mark M0 as completed and proceed to M1'
  ```
- PRs: clear description, steps to test, linked issues, and screenshots for UI.

## Security & Configuration Tips
- Never commit `.env` or secrets; use `.env.example` as reference.
- Required envs: `POSTGRES_*`, `DJANGO_SECRET_KEY`, `DJANGO_DEBUG`, `DB_HOST=db`.
- Rotate keys and set `DJANGO_DEBUG=0` for non-dev environments.