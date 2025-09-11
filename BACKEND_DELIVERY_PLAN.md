# Backend Delivery Plan (Baby Steps) - Clean Architecture

Este documento organiza o trabalho em módulos incrementais seguindo Clean Architecture e princípios SOLID, do mais simples ao mais complexo. Cada módulo define objetivo, entregáveis, critérios de aceite e comandos úteis.

## Architecture Overview
- **Clean Architecture**: 4 camadas (Entities, Use Cases, Interfaces, Frameworks)
- **SOLID Principles**: Dependency inversion, single responsibility, interface segregation
- **TDD**: Test-driven development obrigatório em todas as implementações

## M0 — Ambiente de Desenvolvimento (Docker + Postgres)
- **Objetivo**: Subir o ambiente local com Docker Compose, imagem Python 3.12, Postgres 16, e hot-reload via volume.
- **Entregáveis**:
  - `compose.yaml`, `Dockerfile` (dev), `requirements.txt`, `.env.example`, `.dockerignore`, `Makefile` com comandos.
- **Critérios de aceite**:
  - `make env && make up` sobe `web` e `db` com healthcheck do Postgres.
  - É possível abrir shell no container com `make web/sh`.
- **Comandos úteis**:
  - `make env`, `make build`, `make up`, `make down`, `make logs`, `make web/sh`, `make db/psql`.
- **Status**: Concluído.

## M1 — Bootstrap do Projeto Django + DRF + Postgres
- **Objetivo**: Criar o esqueleto Django e configurar DRF e banco.
- **Entregáveis**:
  - Projeto criado com `django-admin startproject config .` e `rest_framework` em `INSTALLED_APPS`.
  - Configuração de banco Postgres usando variáveis de ambiente.
  - Setup inicial de Clean Architecture com estrutura de pastas.
- **Critérios de aceite**:
  - `make bootstrap` cria o projeto; `make migrate` funciona sem erros; acessível em `http://localhost:8000`.
  - Estrutura Clean Architecture criada em `core/`.
- **Comandos úteis**:
  - `make bootstrap`, `make migrate`, `make createsuperuser`.
- **Status**: Concluído.

## M2 — Modelagem e CRUDs básicos (Companies, Documents, Signers) - Clean Architecture
- **Objetivo**: Implementar entidades, use cases e interfaces seguindo Clean Architecture.
- **Entregáveis**:
  ```
  core/
  ├── entities/         # Company, Document, Signer entities
  ├── use_cases/        # CreateCompanyUseCase, CreateDocumentUseCase, etc.
  ├── interfaces/       # ICompanyRepository, IDocumentRepository, DTOs
  └── frameworks/       # Django models, serializers, viewsets
  ```
  - **TDD**: Testes para entities (regras de negócio) antes da implementação
  - **Entities**: `Company`, `Document`, `Signer` com business logic
  - **Use Cases**: `CreateCompanyUseCase`, `CreateDocumentUseCase`, `AssignSignersUseCase`
  - **Repositories**: Interfaces `ICompanyRepository`, `IDocumentRepository`, `ISignerRepository`
  - **DTOs**: `CreateCompanyDTO`, `DocumentResponseDTO`, `SignerDTO`
  - **Frameworks**: Django models, DRF serializers, viewsets
  - Rotas RESTful (`/api/v1/companies/`, `/api/v1/documents/`, `/api/v1/signers/`).
- **Critérios de aceite**:
  - **TDD Red-Green-Refactor**: Todos os use cases implementados com TDD
  - **Dependency Inversion**: Use cases dependem apenas de interfaces
  - **Business Logic**: Entities contêm regras de negócio (ex: `document.can_be_signed()`)
  - "Dado que o usuário acessa o painel da empresa, então deve ser possível criar, listar, editar e excluir Companies, Documents e Signers, com interface fluida (sem reload)."
- **Comandos úteis**:
  - `make manage cmd='startapp core'`, `make test`.

## M3 — Integração ZapSign (criação de documento) - Clean Architecture
- **Objetivo**: Ao criar um `Document`, enviar para a API ZapSign seguindo Clean Architecture.
- **Entregáveis**:
  ```
  core/
  ├── entities/
  │   └── document.py   # Business rules para ZapSign integration
  ├── use_cases/
  │   └── create_document_with_zapsign.py  # Use case orchestration
  ├── interfaces/
  │   └── services.py   # IZapSignService interface
  └── frameworks/
      └── external/
          └── zapsign/
              ├── client.py    # HTTP client implementation
              └── service.py   # ZapSignService (implements IZapSignService)
  ```
  - **TDD**: Testes unitários para use case com mock de IZapSignService
  - **Interface**: `IZapSignService` com métodos `create_document()`, `get_document_status()`
  - **Implementation**: `ZapSignService` com timeouts e retries
  - **Entity Logic**: `Document.integrate_with_zapsign()` business rules
  - **Use Case**: `CreateDocumentWithZapSignUseCase` orquestra entity + service
  - Configuração de credenciais via env (`ZAPSIGN_API_KEY`, `ZAPSIGN_BASE_URL`).
- **Critérios de aceite**:
  - **TDD**: Use case testado com mock antes da implementação
  - **Clean Architecture**: ZapSign como detail, não afeta entities/use cases
  - **SOLID**: Service implementa interface, use case depende de abstração
  - "Dado que o usuário cria um novo documento, então ele deve ser enviado automaticamente para a API da ZapSign, armazenando o token e open_id retornados."
- **Notas**:
  - Primeira versão síncrona; processamento assíncrono em M7.

## M4 — Análise com IA do conteúdo do documento - Clean Architecture
- **Objetivo**: Analisar o conteúdo (texto) do documento seguindo Clean Architecture.
- **Entregáveis**:
  ```
  core/
  ├── entities/
  │   ├── document.py           # Document.analyze() business method
  │   └── document_analysis.py  # DocumentAnalysis entity
  ├── use_cases/
  │   └── analyze_document.py   # AnalyzeDocumentUseCase
  ├── interfaces/
  │   ├── services.py           # IAnalysisService interface
  │   └── repositories.py      # IDocumentAnalysisRepository
  └── frameworks/
      ├── django/
      │   └── models.py         # DocumentAnalysis Django model
      └── external/
          └── analysis/
              ├── ai_service.py  # AIAnalysisService implementation
              └── heuristic_service.py  # HeuristicAnalysisService (MVP)
  ```
  - **TDD**: Testes para entity business logic e use case
  - **Entity**: `DocumentAnalysis` com `missing_topics`, `summary`, `insights`
  - **Use Case**: `AnalyzeDocumentUseCase` orquestra análise e persistência
  - **Interface**: `IAnalysisService.analyze(text) -> AnalysisResult`
  - **Implementations**: MVP heurístico + preparação para LLM
  - Endpoint para solicitar nova análise (`POST /api/v1/documents/{id}/analyze`)
- **Critérios de aceite**:
  - **TDD**: Business logic testada independentemente de IA provider
  - **Strategy Pattern**: Múltiplas implementações de IAnalysisService
  - **Entity Rules**: `Document.can_be_analyzed()`, `DocumentAnalysis.is_complete()`
  - "Dado que o documento é salvo, então o sistema deve analisar seu conteúdo com IA e apresentar uma visão com tópicos faltantes, resumo e insights úteis."
- **Notas**:
  - MVP: heurísticas/embeddings open-source; evolução LLM posterior.

## M5 — API Pública Autenticada (Integração Externa) - Clean Architecture
- **Objetivo**: Expor endpoints RESTful autenticados seguindo Clean Architecture.
- **Entregáveis**:
  ```
  api/
  ├── v1/
  │   ├── auth/          # JWT authentication endpoints
  │   ├── companies/     # Company API endpoints
  │   ├── documents/     # Document API endpoints
  │   └── reports/       # Reporting endpoints
  └── middleware.py      # Custom middleware
  
  core/
  ├── use_cases/
  │   ├── authenticate_user.py
  │   ├── generate_report.py
  │   └── create_api_document.py
  └── interfaces/
      └── auth.py        # IAuthService, ITokenService
  ```
  - **TDD**: Testes de integração para todos os endpoints
  - **Authentication**: JWT com `djangorestframework-simplejwt`
  - **Use Cases**: Específicos para API pública (diferentes do admin)
  - **Versioning**: `/api/v1/...` estrutura
  - **OpenAPI**: Schema automático com `drf-spectacular`
  - **Endpoints**: criar `Document`, disparar análise, relatórios por período/company
- **Critérios de aceite**:
  - **Clean API**: Use cases específicos para cada endpoint público
  - **Security**: JWT authentication, rate limiting
  - **Documentation**: OpenAPI schema completo
  - "Dado que o cliente deseja integrar seus fluxos com ZapSign, então a plataforma deve expor endpoints RESTful autenticados para criação de documentos, nova análise e relatórios."

## M6 — Painel (UX sem reload) – Clean Architecture Frontend
- **Objetivo**: Interface fluida consumindo use cases via API.
- **Entregáveis**:
  ```
  frontend/
  ├── templates/         # Django templates + HTMX
  ├── static/           # CSS, JS, AlpineJS
  ├── components/       # Reusable HTMX components
  └── views.py          # Frontend-specific views
  
  core/
  ├── use_cases/
  │   ├── dashboard/    # Dashboard-specific use cases
  │   └── frontend/     # Frontend-optimized use cases
  ```
  - **Frontend Use Cases**: Otimizados para UI (agregações, formatações)
  - **HTMX Integration**: Componentes assíncronos
  - **AlpineJS**: Interatividade reativa
  - Listagem e formulários assíncronos para Companies, Documents e Signers
- **Critérios de aceite**:
  - **No Reload**: Todas operações CRUD via HTMX/AJAX
  - **Clean Separation**: Frontend consome use cases via controllers
  - **UX**: Interface fluida com loading states e feedback
  - "Interface fluida (sem reload) — operações CRUD e exibição de análises acontecem via requisições assíncronas."

## M7 — Robustez Operacional (Jobs assíncronos + Retentativas) - Clean Architecture
- **Objetivo**: Desacoplar tarefas de longa duração seguindo Clean Architecture.
- **Entregáveis**:
  ```
  core/
  ├── use_cases/
  │   ├── async_create_document.py     # Async version of use cases
  │   └── async_analyze_document.py
  ├── interfaces/
  │   └── queues.py                    # ITaskQueue, IJobScheduler
  └── frameworks/
      ├── celery/
      │   ├── tasks.py                 # Celery task definitions
      │   └── worker.py                # Worker configuration
      └── redis/
          └── queue_service.py         # Redis queue implementation
  ```
  - **Async Use Cases**: Versões assíncronas dos use cases
  - **Queue Interface**: `ITaskQueue` para abstração de filas
  - **Celery Tasks**: `send_to_zapsign.delay()`, `run_analysis.delay()`
  - **Retry Logic**: Exponential backoff, dead letter queues
  - **Monitoring**: Task status tracking
- **Critérios de aceite**:
  - **Clean Architecture**: Tasks executam use cases, não lógica própria
  - **Resilience**: Retry automático, handling de falhas
  - **Monitoring**: Status de jobs visível no admin
  - **Performance**: UX não bloqueada por operações externas

## M8 — Testes Automatizados e Qualidade - Clean Architecture
- **Objetivo**: Cobertura completa seguindo as camadas da Clean Architecture.
- **Entregáveis**:
  ```
  core/tests/
  ├── test_entities/           # Unit tests - business logic puro
  ├── test_use_cases/          # Unit tests - orchestration com mocks
  ├── test_interfaces/         # Contract tests
  └── test_frameworks/         # Integration tests - Django/DB/APIs
  
  tests/
  ├── integration/             # End-to-end tests
  ├── factories/               # Factory Boy test data
  └── fixtures/                # Test fixtures
  ```
  - **Entity Tests**: Regras de negócio sem dependências externas
  - **Use Case Tests**: Mocking de repositories e services
  - **Integration Tests**: Testes completos com BD real
  - **Contract Tests**: Verificação de interfaces
  - **Coverage**: >90% entities e use cases, >80% frameworks
- **Critérios de aceite**:
  - **TDD Compliance**: Todos os módulos implementados com TDD
  - **Layer Testing**: Cada camada testada adequadamente
  - **Fast Tests**: Unit tests executam em <5s
  - **CI Ready**: Pipeline automatizado de testes
  - "Dado que o produto está sendo monitorado, então deve haver testes automatizados garantindo a estabilidade das principais rotas e funcionalidades."

## M9 — Documentação do Projeto - Clean Architecture
- **Objetivo**: Documentar arquitetura, setup e uso.
- **Entregáveis**:
  - **README.md**: Setup, comandos, arquitetura Clean
  - **ARCHITECTURE.md**: Decisões arquiteturais, diagramas
  - **API_DOCS.md**: Endpoints, exemplos curl, authentication
  - **AI_ANALYSIS.md**: Lógica de IA, providers, configuração
  - **DEPLOYMENT.md**: Production setup, environment vars
  - **OpenAPI**: Schema automático com Swagger UI
- **Critérios de aceite**:
  - **Architecture Documentation**: Diagramas das 4 camadas
  - **Developer Experience**: Setup em <10 minutos seguindo README
  - **API Examples**: Curl examples para todos endpoints
  - **Troubleshooting**: Guia de problemas comuns
  - "Dado que o cliente técnico acessa o projeto, então o README deve explicar como subir o sistema, rodar testes, consumir os endpoints e entender a lógica de IA aplicada."

---

## Sequência Recomendada de Entrega
1. **M0 → M1**: ambiente e bootstrap prontos para iteração rápida
2. **M2**: Entities e Use Cases fundamentais (TDD obrigatório)
3. **M3**: ZapSign integration seguindo Clean Architecture
4. **M4**: Análise com IA (MVP heurístico + interface para LLM)
5. **M5**: API pública autenticada + OpenAPI
6. **M6**: Painel fluido (HTMX/AlpineJS) consumindo use cases
7. **M7**: Tarefas assíncronas (elevar robustez operacional)
8. **M8**: Testes automatizados (cobertura completa)
9. **M9**: Documentação completa

## Variáveis de Ambiente (Clean Architecture)
- **Database**: `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `DB_HOST=db`, `DB_PORT=5432`
- **Django**: `DJANGO_DEBUG`, `DJANGO_SECRET_KEY`, `DJANGO_ALLOWED_HOSTS`, `DJANGO_SETTINGS_MODULE`
- **ZapSign (M3)**: `ZAPSIGN_API_KEY`, `ZAPSIGN_BASE_URL`
- **AI Analysis (M4)**: `AI_PROVIDER_API_KEY`, `AI_PROVIDER_BASE_URL`, `AI_PROVIDER_TYPE=heuristic|openai|anthropic`
- **JWT (M5)**: `JWT_SECRET_KEY`, `JWT_ACCESS_TOKEN_LIFETIME`, `JWT_REFRESH_TOKEN_LIFETIME`
- **Async (M7)**: `CELERY_BROKER_URL=redis://redis:6379/0`, `CELERY_RESULT_BACKEND`
- **Monitoring**: `SENTRY_DSN`, `LOG_LEVEL=INFO`

## Comandos Rápidos
- **Primeira vez**: `make env && make build && make bootstrap && make up`
- **Desenvolvimento**: `make up` → code → `make test` → commit
- **Database**: `make manage cmd=makemigrations` → `make manage cmd=migrate`
- **Testes**: `make test` (rápido) | `make test-integration` (completo)
- **Debug**: `make web/sh` (container) | `make logs` (troubleshoot)
- **Deploy**: `make build-prod && make deploy`

## Clean Architecture Benefits
- **Testability**: Business logic isolada e testável
- **Flexibility**: Fácil trocar implementations (ZapSign → outro provider)
- **Maintainability**: Mudanças isoladas por camada
- **Scalability**: Use cases independentes, fácil paralelizar
- **Team Productivity**: Responsabilidades claras, trabalho paralelo