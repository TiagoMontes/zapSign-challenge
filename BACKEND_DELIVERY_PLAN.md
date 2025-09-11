# Backend Delivery Plan (Baby Steps) - Clean Architecture

Este documento organiza o trabalho em módulos incrementais seguindo Clean Architecture e princípios SOLID, do mais simples ao mais complexo. Cada módulo define objetivo, entregáveis, critérios de aceite e comandos úteis.

## Architecture Overview
- **Clean (simplificada)**: 4 camadas
  - Domain (Entities)
  - Use Cases (Application)
  - Infra (Repositories com Django ORM + mappers em `core/orm`)
  - API (Serializers/ViewSets/Routers em `api/`)
- **Fluxo de dependência**: Entities não dependem de nada; Use Cases dependem de Entities e recebem repositórios concretos por injeção; Repositories usam Django ORM; API pode instanciar Use Cases diretamente ou via providers opcionais (`core/app/providers`).
- **SOLID Principles**: Single responsibility, coesão por módulo, segregação por responsabilidade
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

## M2 — Modelagem e CRUDs básicos (Companies, Documents, Signers) — Clean (simplificada)
- **Objetivo**: Implementar entidades, use cases e repositórios concretos usando Django ORM (sem ports/adapters).
- **Entregáveis**:
  ```
  core/
  ├── domain/
  │   └── entities/                 # Company, Document, Signer (puras)
  ├── use_cases/                    # CreateCompanyUseCase, CreateDocumentUseCase, AssignSignersUseCase
  ├── orm/
  │   ├── models.py                 # Django ORM models
  │   └── mappers.py                # Model ↔ Entity (isola ORM do domínio)
  ├── repositories/
  │   ├── company_repo.py           # CompanyRepository
  │   ├── document_repo.py          # DocumentRepository (assign_signers)
  │   └── signer_repo.py            # SignerRepository
  └── app/
      └── providers/                # Factories opcionais para injetar repositórios em use cases
          ├── company.py
          └── document.py

  api/
  ├── serializers/                  # CompanySerializer, DocumentSerializer, SignerSerializer
  ├── views/                        # CompanyViewSet, DocumentViewSet, SignerViewSet
  └── routers.py                    # DRF router em /api
  
  tests/
  ├── fakes/                        # Repositórios in-memory para TDD dos use cases
  ├── test_entities/
  ├── test_use_cases/
  └── test_frameworks/              # Testes de API (integração)
  ```
  - **TDD**: Testes para entities e use cases antes da implementação
  - **Fakes**: Repositórios in-memory em `tests/fakes/` para testar use cases sem DB
  - **Entities**: `Company`, `Document`, `Signer` com regras de negócio
  - **Use Cases**: `CreateCompanyUseCase`, `CreateDocumentUseCase`, `AssignSignersUseCase` (dependem de Entities e recebem repositórios concretos)
  - **Repositories**: Implementações Django ORM + mapeamento para entidades
  - **API**: DRF (serializers/views/routers) pode usar providers ou instanciar use cases diretamente
  - Endpoints RESTful (`/api/companies/`, `/api/documents/`, `/api/signers/`).
- **Critérios de aceite**:
  - **TDD Red-Green-Refactor**: Todos os use cases implementados com TDD usando fakes
  - **Isolamento do ORM**: Conversões Model↔Entity via `core/orm/mappers.py`
  - **Injeção**: Use cases recebem repositórios concretos por construtor (providers opcionais)
  - **Business Logic**: Entities contêm regras (ex: `document.can_be_signed()`)
  - "Dado que o usuário acessa o painel, então deve ser possível criar, listar, editar e excluir Companies, Documents e Signers via API DRF."
- **Comandos úteis**:
  - `make manage cmd='startapp core'`, `make test`.

## M3 — Integração ZapSign (criação de documento)
- **Objetivo**: Ao criar um `Document`, enviar para a API ZapSign seguindo a arquitetura simplificada.
- **Entregáveis**:
  ```
  core/
  ├── use_cases/
  │   └── create_document_with_zapsign.py  # Orquestração
  └── services/
      └── zapsign/
          ├── client.py     # HTTP client
          └── service.py    # ZapSignService (lida com API externa)

  core/app/providers/            # Factories opcionais para injetar o service no use case
  ```
  - **TDD**: Testes unitários para use case com mock do serviço ZapSign
  - **Service**: `ZapSignService` com métodos `create_document()`, `get_document_status()` (com timeouts e retries)
  - **Entity Logic**: `Document` armazena `token` e `open_id` retornados
  - **Use Case**: `CreateDocumentWithZapSignUseCase` orquestra entity + service
  - Configuração de credenciais via env (`ZAPSIGN_API_KEY`, `ZAPSIGN_BASE_URL`).
- **Critérios de aceite**:
  - **TDD**: Use case testado com mock antes da implementação
  - **Acoplamento controlado**: ZapSign como detalhe de implementação; use case recebe o service por injeção
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
  ├── services/
  │   └── analysis/
  │       ├── ai_service.py         # AIAnalysisService (concreto)
  │       └── heuristic_service.py  # HeuristicAnalysisService (MVP)
  └── orm/
      └── models.py                 # (se precisar) modelos relacionados à análise
  ```
  - **TDD**: Testes para entity business logic e use case
  - **Entity**: `DocumentAnalysis` com `missing_topics`, `summary`, `insights`
  - **Use Case**: `AnalyzeDocumentUseCase` orquestra análise e persistência
  - **Serviços**: MVP heurístico + preparação para LLM
  - Endpoint para solicitar nova análise (`POST /api/documents/{id}/analyze`)
- **Critérios de aceite**:
  - **TDD**: Business logic testada independentemente de IA provider
- **Pluggable Strategy**: múltiplas implementações de serviço de análise
  - **Entity Rules**: `Document.can_be_analyzed()`, `DocumentAnalysis.is_complete()`
  - "Dado que o documento é salvo, então o sistema deve analisar seu conteúdo com IA e apresentar uma visão com tópicos faltantes, resumo e insights úteis."
- **Notas**:
  - MVP: heurísticas/embeddings open-source; evolução LLM posterior.

## M5 — API Pública Autenticada (Integração Externa)
- **Objetivo**: Expor endpoints RESTful autenticados.
- **Entregáveis**:
  ```
  api/
  ├── auth/              # JWT authentication endpoints
  ├── companies/         # Company API endpoints
  ├── documents/         # Document API endpoints
  ├── reports/           # Reporting endpoints
  └── middleware.py      # Custom middleware
  
  core/
  └── use_cases/
      ├── authenticate_user.py
      ├── generate_report.py
      └── create_api_document.py
  
  core/services/         # Serviços concretos (ex.: auth/token) se necessário
  ```
  - **TDD**: Testes de integração para todos os endpoints
  - **Authentication**: JWT com `djangorestframework-simplejwt`
  - **Use Cases**: Específicos para API pública
  - **Versioning**: não versionado inicialmente (`/api/...`)
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
  │   ├── async_create_document.py     # Versões assíncronas dos use cases
  │   └── async_analyze_document.py
  ├── services/
  │   └── queue_service.py             # QueueService (Celery/Redis)
  └── tasks/
      └── celery_app.py                # Celery app e tasks
  ```
  - **Async Use Cases**: Versões assíncronas dos use cases
  - **Celery Tasks**: `send_to_zapsign.delay()`, `run_analysis.delay()`
  - **Retry Logic**: Exponential backoff, dead letter queues
  - **Monitoring**: Task status tracking
- **Critérios de aceite**:
  - **Clean Architecture**: Tasks executam use cases, não lógica própria
  - **Resilience**: Retry automático, handling de falhas
  - **Monitoring**: Status de jobs visível no admin
  - **Performance**: UX não bloqueada por operações externas

## M8 — Testes Automatizados e Qualidade
- **Objetivo**: Cobertura completa com foco nas regras de negócio e integrações principais.
- **Entregáveis**:
  ```
  tests/
  ├── test_entities/           # Unit tests - business logic puro
  ├── test_use_cases/          # Unit tests - orquestração com fakes/mocks
  ├── test_frameworks/         # Integration tests - Django/DB/APIs
  ├── factories/               # Factory Boy test data (opcional)
  └── fixtures/                # Test fixtures (opcional)
  ```
  - **Entity Tests**: Regras de negócio sem dependências externas
  - **Use Case Tests**: Fakes para repositories/services e asserts de orquestração
  - **Integration Tests**: Rotas DRF com banco de testes
  - **Coverage**: Prioridade em entities e use cases
- **Critérios de aceite**:
  - **TDD Compliance**: Implementação dirigida por testes
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
