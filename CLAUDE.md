# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Common Development Commands

### Environment Setup
- `make env` - Create .env from .env.example if missing
- `make build` - Build Docker images
- `make up` - Start services (web and PostgreSQL database)
- `make down` - Stop services

### Django Development
- `make migrate` - Run database migrations
- `make createsuperuser` - Create Django superuser
- `make manage cmd="<command>"` - Run any Django manage.py command
- `make test` - Run Django tests from tests/ directory

### Container Access
- `make web/sh` - Open shell in web container
- `make db/psql` - Open PostgreSQL shell connected to app database
- `make logs` - Tail all container logs

### Type Checking
- `pyright` - Run Pyright type checker (configured in pyrightconfig.json)

## Architecture Overview

This project follows a simplified Clean Architecture with 4 layers:

### Layer Structure
```
core/                              # Core business logic
├── domain/
│   └── entities/                 # Pure domain entities (no Django dependencies)
├── use_cases/                    # Application business logic (interactors)
├── orm/
│   ├── models.py                 # Django ORM models
│   └── mappers.py                # Model ↔ Entity mapping (isolates ORM from domain)
├── repositories/                 # Concrete repositories using Django ORM
└── app/
    └── providers/                # Optional DI factories for use cases

api/                              # REST API layer
├── serializers/                  # DRF serializers
├── views/                        # DRF viewsets/controllers
└── routers.py                    # DRF router (mounted under /api)

tests/                            # Test suite
├── test_entities/                # Domain entity tests
├── test_use_cases/               # Use case tests
└── fakes/                        # Test doubles and mocks
```

### Dependency Flow
- **Entities** have no dependencies
- **Use Cases** depend on Entities and receive concrete repositories via dependency injection
- **Repositories** use Django ORM through mappers
- **API** instantiates Use Cases directly or via optional providers in `core/app/providers`

## Key Architectural Principles

- **Clean Architecture**: Clear separation of concerns with dependency inversion
- **SOLID Principles**: Single responsibility, coesão por módulo, segregação por responsabilidade
- **TDD**: Test-driven development for all implementations
- **No direct ORM in domain**: Entity classes are pure Python, ORM models are isolated in `core/orm/`
- **Mappers pattern**: `core/orm/mappers.py` handles bidirectional conversion between Django models and domain entities

## Testing Strategy

Run tests with `make test`. Tests are organized by layer:
- Unit tests for entities (no database)
- Integration tests for use cases (may use fakes)
- Framework tests for Django-specific code
- All test doubles/fakes in `tests/fakes/`

## Development Environment

- **Python**: 3.12
- **Django**: 5.1.x
- **Django REST Framework**: 3.15.x
- **PostgreSQL**: 16 (via Docker)
- **Type Checking**: Pyright (configured for Python 3.12)

## Working with Docker

The project uses Docker Compose with:
- PostgreSQL 16 database with health checks
- Python 3.12 web container with hot-reload via volume mount
- Auto-restart on file changes (development mode)
- Database exposed on port 5432, web on port 8000