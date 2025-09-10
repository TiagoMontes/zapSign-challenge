# Backend Delivery Plan (Baby Steps)

Este documento organiza o trabalho em módulos incrementais, do mais simples ao mais complexo, e incorpora o fluxo solicitado. Cada módulo define objetivo, entregáveis, critérios de aceite e comandos úteis.

## M0 — Ambiente de Desenvolvimento (Docker + Postgres)
- Objetivo: Subir o ambiente local com Docker Compose, imagem Python 3.12, Postgres 16, e hot-reload via volume.
- Entregáveis:
  - `compose.yaml`, `Dockerfile` (dev), `requirements.txt`, `.env.example`, `.dockerignore`, `Makefile` com comandos.
- Critérios de aceite:
  - `make env && make up` sobe `web` e `db` com healthcheck do Postgres.
  - É possível abrir shell no container com `make web/sh`.
- Comandos úteis:
  - `make env`, `make build`, `make up`, `make down`, `make logs`, `make web/sh`, `make db/psql`.
 - Status: Concluído.

## M1 — Bootstrap do Projeto Django + DRF + Postgres
- Objetivo: Criar o esqueleto Django e configurar DRF e banco.
- Entregáveis:
  - Projeto criado com `django-admin startproject config .` e `rest_framework` em `INSTALLED_APPS`.
  - Configuração de banco Postgres usando variáveis de ambiente.
- Critérios de aceite:
  - `make bootstrap` cria o projeto; `make migrate` funciona sem erros; acessível em `http://localhost:8000`.
- Comandos úteis:
  - `make bootstrap`, `make migrate`, `make createsuperuser`.

## M2 — Modelagem e CRUDs básicos (Companies, Documents, Signers)
- Objetivo: Modelos, serializers, viewsets e rotas CRUD no DRF.
- Entregáveis:
  - App `core` (ou `company`) com modelos `Company`, `Document`, `Signer` e relações adequadas.
  - Serializers e `ViewSet`s com permissões e validações básicas.
  - Rotas RESTful (`/api/companies/`, `/api/documents/`, `/api/signers/`).
- Critérios de aceite (Fluxo):
  - "Dado que o usuário acessa o painel da empresa, então deve ser possível criar, listar, editar e excluir Companies, Documents e Signers, com interface fluida (sem reload)." (No backend: endpoints estáveis; no frontend: previsto uso de HTMX/SPA — fora do escopo backend, mas previsto para M6.)
- Comandos úteis:
  - `make manage cmd='startapp core'`, `make test`.

## M3 — Integração ZapSign (criação de documento)
- Objetivo: Ao criar um `Document`, enviar para a API ZapSign e armazenar `token` e `open_id` retornados.
- Entregáveis:
  - Cliente de integração (`zapsign/client.py`) com timeouts e retries.
  - Sinal ou serviço de domínio que, após criação de `Document`, chama ZapSign e persiste `token`/`open_id`.
  - Configuração de credenciais via env (`ZAPSIGN_API_KEY`, `ZAPSIGN_BASE_URL`).
- Critérios de aceite (Fluxo):
  - "Dado que o usuário cria um novo documento, então ele deve ser enviado automaticamente para a API da ZapSign, armazenando o token e open_id retornados." 
- Notas:
  - Recomendado processamento assíncrono (M7 – Celery) para robustez, mas a primeira entrega pode ser síncrona com timeouts e tratamento de erros.

## M4 — Análise com IA do conteúdo do documento
- Objetivo: Analisar o conteúdo (texto) do documento e oferecer visão com tópicos faltantes, resumo e insights.
- Entregáveis:
  - Serviço `analysis/service.py` com interface `analyze(text) -> {missing_topics, summary, insights}`.
  - Persistência do resultado por `Document` (modelo `DocumentAnalysis`).
  - Endpoint para solicitar nova análise e endpoint para obter resultado.
- Critérios de aceite (Fluxo):
  - "Dado que o documento é salvo, então o sistema deve analisar seu conteúdo com IA e apresentar uma visão com tópicos faltantes, resumo e insights úteis." 
- Notas:
  - Primeira versão pode usar heurísticas/embeddings open-source; evolução para provedor LLM pode ocorrer depois (chave e base URL por env).

## M5 — API Pública Autenticada (Integração Externa)
- Objetivo: Expor endpoints RESTful autenticados para criação de documentos, nova análise e relatórios.
- Entregáveis:
  - Autenticação JWT (ex.: `djangorestframework-simplejwt`).
  - Endpoints: criar `Document`, disparar análise, obter relatório por período/company.
  - Versionamento de API (`/api/v1/...`) e schema OpenAPI.
- Critérios de aceite (Fluxo):
  - "Dado que o cliente deseja integrar seus fluxos com ZapSign, então a plataforma deve expor endpoints RESTful autenticados para criação de documentos, nova análise e relatórios."

## M6 — Painel (UX sem reload) – escopo mínimo backend + esqueleto frontend
- Objetivo: Prover uma interface fluida para CRUD e exibição de análises (sem reload), utilizando o backend pronto.
- Entregáveis (mínimos):
  - Views/templates Django + HTMX/AlpineJS ou um micro-frontend SPA (React/Vite) consumindo a API DRF.
  - Listagem e formulários assíncronos para Companies, Documents e Signers; tela de detalhes com análise.
- Critérios de aceite (Fluxo):
  - "...interface fluida (sem reload)" — operações CRUD e exibição de análises acontecem via requisições assíncronas.
- Notas:
  - Se o foco for apenas backend, entregue mocks básicos de UI e concentre os critérios nos endpoints.

## M7 — Robustez Operacional (Jobs assíncronos + Retentativas)
- Objetivo: Desacoplar tarefas de longa duração (ZapSign, análise) com Celery + Redis.
- Entregáveis:
  - Worker Celery e fila Redis no `compose.yaml` (serviço `worker` e `redis`).
  - Tarefas: `send_to_zapsign(document_id)` e `run_analysis(document_id)` com retries exponenciais.
- Benefício:
  - Melhor UX e tolerância a falhas externas.

## M8 — Testes Automatizados e Qualidade
- Objetivo: Cobrir rotas e funcionalidades principais com testes automáticos.
- Entregáveis:
  - `pytest`/`pytest-django`, factories, cobertura de models/serializers/views.
  - Pipelines locais (pre-commit opcional) para lint/format/test.
- Critérios de aceite (Fluxo):
  - "Dado que o produto está sendo monitorado, então deve haver testes automatizados garantindo a estabilidade das principais rotas e funcionalidades."

## M9 — Documentação do Projeto
- Objetivo: Documentar setup, testes, endpoints e visão de IA.
- Entregáveis:
  - README com: como subir o sistema, rodar testes, consumir endpoints (exemplos curl), e visão da lógica de IA.
  - OpenAPI gerado (ex.: `drf-spectacular`) com UI Swagger.
- Critérios de aceite (Fluxo):
  - "Dado que o cliente técnico acessa o projeto, então o README deve explicar como subir o sistema, rodar testes, consumir os endpoints e entender a lógica de IA aplicada."

---

## Sequência Recomendada de Entrega
1) M0 → M1: ambiente e bootstrap prontos para iteração rápida.
2) M2: CRUDs essenciais (desbloqueia UI e integrações).
3) M3: ZapSign síncrono (primeira versão).
4) M4: Análise com IA (MVP de heurística/sumário). 
5) M5: API pública autenticada + OpenAPI.
6) M6: Painel fluido (HTMX/SPA) consumindo endpoints.
7) M7: Tarefas assíncronas (elevar robustez).
8) M8: Testes automatizados.
9) M9: Documentação completa.

## Variáveis de Ambiente (base)
- Banco: `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `DB_HOST=db`, `DB_PORT=5432`.
- Django: `DJANGO_DEBUG`, `DJANGO_SECRET_KEY`, `DJANGO_ALLOWED_HOSTS`, `DJANGO_SETTINGS_MODULE`.
- Integrações (futuro): `ZAPSIGN_API_KEY`, `ZAPSIGN_BASE_URL`, `AI_PROVIDER_API_KEY`.

## Comandos Rápidos
- Primeira vez: `make env && make build && make bootstrap && make up`.
- Após criar o projeto: `make migrate` e acesse `http://localhost:8000`.
- Acessar containers: `make web/sh` (web), `make db/psql` (psql no db).
- Rodar testes: `make test`.
