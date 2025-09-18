# 📄 ZapSign Challenge - Django Clean Architecture

[![Python Version](https://img.shields.io/badge/python-3.12-blue.svg)](https://python.org)
[![Django Version](https://img.shields.io/badge/django-5.1-green.svg)](https://djangoproject.com)
[![DRF Version](https://img.shields.io/badge/drf-3.15-orange.svg)](https://django-rest-framework.org)
[![Code Quality](https://img.shields.io/badge/type--check-pyright-blue.svg)](https://github.com/microsoft/pyright)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

Um sistema abrangente de gerenciamento de documentos com integração de assinatura eletrônica via API ZapSign, construído seguindo os princípios da Clean Architecture com Django REST Framework. Este projeto demonstra arquitetura de software de nível profissional, Desenvolvimento Orientado por Testes (TDD) e integração com serviços modernos de IA.

## Visão Geral do Projeto

Este projeto implementa um sistema completo de gerenciamento de documentos com:

- **Gestão do Ciclo de Vida de Documentos**: Upload, análise, assinatura e gerenciamento de documentos
- **Assinaturas Eletrônicas**: Integração completa com a API ZapSign para assinaturas digitais
- **Análise Alimentada por IA**: Análise de documentos usando OpenAI e ChromaDB para embeddings
- **Clean Architecture**: Separação adequada de responsabilidades com design orientado ao domínio
- **Segurança de Tipos**: Zero erros Pyright com anotações de tipo abrangentes
- **Desenvolvimento Orientado por Testes**: Suite de testes abrangente seguindo princípios TDD

### Principais Tecnologias

- **Backend**: Django 5.1, Django REST Framework 3.15
- **Banco de Dados**: PostgreSQL 16
- **IA/ML**: OpenAI API, ChromaDB, LangChain
- **Processamento PDF**: PyPDF, Python-magic
- **Containerização**: Docker & Docker Compose
- **Verificação de Tipos**: Pyright
- **Integração API**: ZapSign REST API

## ✨ Funcionalidades & Características

### 📋 Gerenciamento de Documentos
- **Operações CRUD**: Criar, ler, atualizar e deletar documentos
- **Upload de Arquivos**: Suporte para upload de documentos PDF
- **Exclusão Suave**: Documentos são excluídos com trilha de auditoria
- **Análise de Documentos**: Análise e classificação de conteúdo alimentada por IA
- **Extração de Metadados**: Extração automática de propriedades do documento

### 🏢 Gerenciamento de Empresas
- **Perfis de Empresa**: Gerenciar informações e configurações da empresa
- **Associação de Documentos**: Vincular documentos a empresas específicas
- **Gerenciamento de Token API**: Integração segura com ZapSign por empresa

### ✍️ Gerenciamento de Signatários
- **CRUD de Signatários**: Gerenciamento completo do ciclo de vida dos signatários
- **Integração ZapSign**: Sincronização automática com a plataforma ZapSign
- **Fluxo de Assinatura**: Processo simplificado de solicitação de assinatura
- **Rastreamento de Status**: Atualizações de status de assinatura em tempo real

### 🤖 Recursos Alimentados por IA
- **Análise de Documentos**: Análise inteligente de conteúdo usando OpenAI
- **Busca Semântica**: Embeddings de documentos alimentados por ChromaDB
- **Classificação de Conteúdo**: Categorização automática de documentos
- **Geração de Insights**: Resumos de documentos gerados por IA

#### 🔐 Assinaturas Eletrônicas
- **Integração ZapSign**: Integração completa de workflow
- **Solicitações de Assinatura**: Notificações automatizadas aos signatários
- **Monitoramento de Status**: Rastreamento de assinatura em tempo real
- **Finalização de Documentos**: Manuseio automático de conclusão

### 📝 Recursos de Teste
- **PDFs de Teste**: Documentos de exemplo disponíveis em `pdfTest.md` para testes e desenvolvimento
- **Coleção Postman**: Arquivo de coleção `collection/zapsignChallenge.json` com requisições prontas para testar todos os endpoints da API

## 📊 Documentação da API

### URL Base
```
http://localhost:8000/api/
```

### Coleção Postman
Para facilitar os testes da API, está disponível uma coleção completa do Postman em `collection/zapsignChallenge.json`.

**Como usar:**
1. Importe o arquivo `collection/zapsignChallenge.json` no Postman
2. Configure a variável de ambiente `localhost` para `http://localhost:8000`
3. Execute as requisições diretamente com exemplos pré-configurados

A coleção inclui todos os endpoints com exemplos de dados para:
- Empresas (CRUD completo)
- Documentos (criação, análise, adição de signatários)
- Signatários (CRUD, sincronização ZapSign, operações externas)

### Autenticação
Atualmente configurado com permissões `AllowAny` para desenvolvimento. Em produção, implemente autenticação adequada.

### Endpoints Principais

#### Empresas
```http
GET    /api/companies/           # Listar todas as empresas
POST   /api/companies/           # Criar empresa
GET    /api/companies/{id}/      # Obter empresa específica
PUT    /api/companies/{id}/      # Atualizar empresa
DELETE /api/companies/{id}/      # Deletar empresa
```

#### Documentos
```http
GET    /api/documents/                    # Listar todos os documentos
POST   /api/documents/                    # Criar documento via ZapSign
GET    /api/documents/{id}/               # Obter documento específico
DELETE /api/documents/{id}/               # Deletar documento (com sync ZapSign)
POST   /api/documents/{id}/analyze/       # Analisar documento com IA
POST   /api/documents/{id}/add-signer/    # Adicionar signatário ao documento
```

#### Signatários
```http
GET    /api/signers/                      # Listar todos os signatários
POST   /api/signers/                      # Criar signatário
GET    /api/signers/{id}/                 # Obter signatário específico
PUT    /api/signers/{id}/                 # Atualizar signatário
DELETE /api/signers/{id}/                 # Deletar signatário
PUT    /api/signers/{id}/sync/            # Sincronizar com ZapSign
PATCH  /api/signers/{id}/update-external/ # Atualizar no ZapSign
DELETE /api/signers/{id}/remove-external/ # Remover do ZapSign
```

### Exemplos de Requisições API

#### Criar Documento
```bash
curl -X POST http://localhost:8000/api/documents/ \
  -H "Content-Type: application/json" \
  -d '{
    "company_id": 1,
    "name": "Contrato de Prestação de Serviços",
    "url_pdf": "https://example.com/documento.pdf",
    "signers": [
      {
        "name": "João Silva",
        "email": "joao@example.com",
        "phone": "+5511999999999"
      }
    ]
  }'
```

#### Analisar Documento
```bash
curl -X POST http://localhost:8000/api/documents/1/analyze/ \
  -H "Content-Type: application/json" \
  -d '{
    "force_reanalysis": false
  }'
```

#### Adicionar Signatário ao Documento
```bash
curl -X POST http://localhost:8000/api/documents/1/add-signer/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Maria Santos",
    "email": "maria@example.com",
    "phone": "+5511888888888"
  }'
```

## 🛠️ Configuração & Instalação

### Pré-requisitos

- **Docker** & **Docker Compose** (recomendado)
- **Python 3.12** (para desenvolvimento local)
- **PostgreSQL 16** (se executando sem Docker)
- **Git**

### Início Rápido com Docker

1. **Clone o repositório**
   ```bash
   git clone <repository-url>
   cd zapSign-challenge
   ```

2. **Configure as variáveis de ambiente**
   ```bash
   make env  # Copia .env.example para .env
   ```

3. **Configure as variáveis de ambiente**
   Edite o arquivo `.env` com suas configurações:
   ```bash
   # Configuração da API ZapSign
   ZAPSIGN_API_URL=https://sandbox.api.zapsign.com.br/api/v1/

   # API OpenAI para Análise de Documentos
   OPENAI_API_KEY=your-openai-api-key-here

   # Configurações Django
   DJANGO_DEBUG=1
   DJANGO_SECRET_KEY=your-secret-key-here
   DJANGO_ALLOWED_HOSTS=*
   ```

4. **Construa e inicie os serviços**
   ```bash
   make build  # Construir imagens Docker
   make up     # Iniciar serviços
   ```

5. **Execute as migrações do banco de dados**
   ```bash
   make migrate
   ```

6. **Crie um superusuário (opcional)**
   ```bash
   make createsuperuser
   ```

7. **Verifique a instalação**
   ```bash
   curl http://localhost:8000/api/companies/
   ```

### Configuração para Desenvolvimento Local

1. **Crie um ambiente virtual**
   ```bash
   python3.12 -m venv venv
   source venv/bin/activate  # No Windows: venv\Scripts\activate
   ```

2. **Instale as dependências**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure o banco PostgreSQL**
   ```bash
   # Instale o PostgreSQL e crie o banco
   createdb app
   ```

4. **Configure o ambiente**
   ```bash
   cp .env.example .env
   # Edite .env com as configurações locais do banco
   ```

5. **Execute migrações e inicie o servidor**
   ```bash
   python manage.py migrate
   python manage.py runserver
   ```

## Arquitetura & Estrutura do Projeto

Este projeto segue os princípios da **Clean Architecture** com separação clara de responsabilidades:

```
zapSign-challenge/
├── core/                              # Lógica de negócio principal
│   ├── domain/
│   │   └── entities/                 # Entidades de domínio puras (sem deps Django)
│   │       ├── company.py
│   │       ├── document.py
│   │       ├── signer.py
│   │       └── document_analysis.py
│   ├── use_cases/                    # Lógica de negócio da aplicação
│   │   ├── company/
│   │   ├── document/
│   │   └── signer/
│   ├── repositories/                 # Camada de acesso a dados
│   │   ├── company_repo.py
│   │   ├── document_repo.py
│   │   └── signer_repo.py
│   ├── orm/
│   │   ├── models.py                 # Modelos Django ORM
│   │   └── mappers.py                # Mapeamento Modelo ↔ Entidade
│   ├── services/                     # Integrações de serviços externos
│   │   ├── zapsign_service.py        # Integração API ZapSign
│   │   └── analysis/                 # Serviços de análise IA
│   └── app/
│       └── providers/                # Injeção de dependência
├── api/                              # Camada da API REST
│   ├── serializers/                  # Serializers DRF
│   ├── views/                        # Viewsets/controllers DRF
│   └── routers.py                    # Roteamento da API
├── tests/                            # Suite de testes
│   ├── test_entities/                # Testes de entidades de domínio
│   ├── test_use_cases/               # Testes de casos de uso
│   └── fakes/                        # Test doubles e mocks
└── config/                           # Configuração Django
```

### Camadas da Arquitetura

1. **Camada de Domínio** (`core/domain/entities/`)
   - Entidades Python puras com lógica de negócio
   - Sem dependências externas (incluindo Django)
   - Contém regras de negócio e lógica de domínio

2. **Camada de Casos de Uso** (`core/use_cases/`)
   - Lógica de negócio da aplicação
   - Orquestra entidades de domínio e repositórios
   - Gerencia workflows e transações de negócio

3. **Camada de Repositório** (`core/repositories/`)
   - Abstração de acesso a dados
   - Converte entre entidades de domínio e modelos ORM
   - Isola o domínio dos detalhes de persistência

4. **Camada de API** (`api/`)
   - Interface API REST usando Django REST Framework
   - Serialização de requisições/respostas
   - Apenas responsabilidades específicas do HTTP

5. **Camada de Infraestrutura** (`core/orm/`, `core/services/`)
   - Modelos de banco e integrações de serviços externos
   - Implementações específicas do framework
   - Detalhes técnicos isolados da lógica de negócio

## Desenvolvimento & Testes

### Comandos de Desenvolvimento

```bash
# Gerenciamento de ambiente
make env              # Criar .env a partir do template
make build            # Construir imagens Docker
make up               # Iniciar todos os serviços
make down             # Parar todos os serviços
make logs             # Visualizar logs dos containers

# Operações Django
make migrate          # Executar migrações do banco
make createsuperuser  # Criar usuário admin Django
make manage cmd="..." # Executar qualquer comando Django

# Testes e qualidade
make test             # Executar suite de testes Django
make typecheck        # Executar verificação de tipos Pyright
make validate         # Executar typecheck e testes

# Acesso aos containers
make web/sh           # Acesso shell ao container web
make db/psql          # Acesso shell PostgreSQL
```

### Estratégia de Testes

Este projeto segue **Desenvolvimento Orientado por Testes (TDD)** com cobertura abrangente de testes:

#### Organização dos Testes
- **Testes Unitários**: Entidades de domínio e lógica de negócio
- **Testes de Integração**: Casos de uso com repositórios
- **Testes de API**: Endpoints REST e serialização
- **Testes de Serviços**: Integrações de serviços externos

#### Executando Testes
```bash
# Executar todos os testes
make test

# Executar módulos específicos de teste
make manage cmd="test tests.test_entities"
make manage cmd="test tests.test_use_cases"

# Executar com cobertura
make manage cmd="test tests --keepdb --verbosity=2"
```

#### Verificação de Tipos
```bash
# Executar verificador de tipos Pyright
make typecheck

# Ou diretamente
pyright .
```

### Padrões de Qualidade de Código

- **Segurança de Tipos**: Todo código inclui anotações de tipo abrangentes
- **Clean Architecture**: Fluxo rigoroso de dependências e separação de responsabilidades
- **Princípios SOLID**: Responsabilidade única, aberto/fechado, inversão de dependência
- **Cobertura de Testes**: Mínimo de 80% de cobertura para toda lógica de negócio
- **Documentação**: Docstrings abrangentes e comentários inline

## Exemplos de Uso

### Workflows Comuns

#### 1. Fluxo Completo de Assinatura de Documento

```bash
# 1. Criar uma empresa
curl -X POST http://localhost:8000/api/companies/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Empresa LTDA",
    "api_token": "seu-token-zapsign"
  }'

# 2. Criar documento com signatários
curl -X POST http://localhost:8000/api/documents/ \
  -H "Content-Type: application/json" \
  -d '{
    "company_id": 1,
    "name": "Contrato de Prestação de Serviços",
    "url_pdf": "https://example.com/contrato.pdf",
    "signers": [
      {
        "name": "Cliente da Silva",
        "email": "cliente@example.com",
        "phone": "+5511999999999"
      }
    ]
  }'

# 3. Analisar conteúdo do documento
curl -X POST http://localhost:8000/api/documents/1/analyze/ \
  -H "Content-Type: application/json" \
  -d '{"force_reanalysis": false}'

# 4. Adicionar signatário adicional se necessário
curl -X POST http://localhost:8000/api/documents/1/add-signer/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Representante Legal",
    "email": "legal@example.com",
    "phone": "+5511888888888"
  }'
```

#### 2. Análise de Documento e Insights

```bash
# Analisar documento para insights de conteúdo
curl -X POST http://localhost:8000/api/documents/1/analyze/ \
  -H "Content-Type: application/json" \
  -d '{
    "force_reanalysis": true
  }'

# A resposta inclui:
# - Resumo do documento
# - Tópicos e temas principais
# - Avaliação de riscos
# - Indicadores de conformidade
# - Ações sugeridas
```

### Integração Frontend

Esta API foi projetada para funcionar perfeitamente com frameworks frontend modernos:

#### Exemplo Angular/React
```typescript
// Exemplo de serviço de documentos
export class DocumentService {
  private baseUrl = 'http://localhost:8000/api';

  async criarDocumento(data: DocumentCreateRequest): Promise<Document> {
    const response = await fetch(`${this.baseUrl}/documents/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    return response.json();
  }

  async analisarDocumento(id: number): Promise<DocumentAnalysis> {
    const response = await fetch(`${this.baseUrl}/documents/${id}/analyze/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ force_reanalysis: false })
    });
    return response.json();
  }
}
```

## Detalhes Técnicos

### Integrações de Serviços Externos

#### Integração API ZapSign
- **Ambiente Sandbox**: `https://sandbox.api.zapsign.com.br/api/v1/`
- **Criação de Documentos**: Criação automática de documentos e gerenciamento de signatários
- **Sincronização em Tempo Real**: Sincronização bidirecional do status do documento
- **Tratamento de Erros**: Tratamento abrangente de erros para falhas da API

#### Integração OpenAI
- **Análise de Documentos**: Análise e resumo de conteúdo alimentado por GPT
- **Geração de Embeddings**: Embeddings de texto para busca semântica
- **Classificação de Conteúdo**: Detecção automática do tipo de documento
- **Avaliação de Riscos**: Avaliação de conformidade e riscos alimentada por IA

#### Integração ChromaDB
- **Armazenamento Vetorial**: Armazenamento eficiente de embeddings de documentos
- **Busca Semântica**: Encontrar documentos similares baseado no conteúdo
- **Pontuação de Similaridade**: Recomendações de documentos baseadas em conteúdo
- **Filtragem de Metadados**: Busca avançada com filtros de negócio

### Esquema do Banco de Dados

#### Tabelas Principais
- **Companies**: Gerenciamento de organizações com tokens de API
- **Documents**: Metadados de documentos com suporte a exclusão suave
- **Signers**: Informações de signatários com integração ZapSign
- **DocumentAnalysis**: Resultados e insights de análise IA

#### Relacionamentos Principais
- Companies → Documents (1:N)
- Documents → Signers (N:M através do ZapSign)
- Documents → DocumentAnalysis (1:1)

### Considerações de Performance

- **Indexação do Banco**: Índices otimizados para consultas comuns
- **Carregamento Preguiçoso**: Padrões eficientes de consulta ORM
- **Estratégia de Cache**: Preparado para Redis em produção
- **Pool de Conexões**: Otimização de conexões PostgreSQL
- **Tarefas em Background**: Preparado para Celery para processamento assíncrono

## Solução de Problemas

### Problemas Comuns

#### Problemas com Docker
```bash
# Container não inicia
make down && make build && make up

# Problemas de conexão com banco
make db/psql  # Testar conectividade do banco

# Visualizar logs dos containers
make logs
```

#### Problemas com Banco de Dados
```bash
# Resetar banco de dados
make down
docker volume rm zapsign-challenge_db_data
make up && make migrate
```

#### Problemas com API
```bash
# Verificar status dos serviços
make ps

# Visualizar logs do Django
make logs web

# Testar conectividade da API
curl -v http://localhost:8000/api/companies/
```

#### Problemas com Verificação de Tipos
```bash
# Instalar Pyright
npm install -g pyright

# Executar verificação de tipos
make typecheck
```

### Variáveis de Ambiente

Certifique-se de que todas as variáveis de ambiente necessárias estão configuradas no `.env`:

```bash
# Necessário para funcionalidade básica
DJANGO_SECRET_KEY=sua-chave-secreta
POSTGRES_DB=app
POSTGRES_USER=app
POSTGRES_PASSWORD=app

# Necessário para integração ZapSign
ZAPSIGN_API_URL=https://sandbox.api.zapsign.com.br/api/v1/

# Necessário para recursos de IA
OPENAI_API_KEY=sua-chave-api-openai
```

## Contribuindo

### Fluxo de Desenvolvimento

1. **Faça um fork do repositório**
2. **Crie uma branch de feature**
   ```bash
   git checkout -b feature/nome-da-sua-feature
   ```

3. **Siga a abordagem TDD**
   - Escreva testes que falham primeiro
   - Implemente código mínimo para passar nos testes
   - Refatore mantendo os testes verdes

4. **Garanta qualidade do código**
   ```bash
   make validate  # Executa typecheck e testes
   ```

5. **Submeta pull request**
   - Forneça descrição clara
   - Inclua cobertura de testes
   - Certifique-se de que todas as verificações passem

### Padrões de Código

- **Anotações de Tipo**: Todas as funções devem incluir type hints
- **Docstrings**: Métodos públicos requerem documentação
- **Clean Architecture**: Respeite os limites das camadas
- **Cobertura de Testes**: Novas funcionalidades requerem testes abrangentes
- **Tratamento de Erros**: Tratamento adequado de exceções e logging

## Licença

Este projeto está licenciado sob a Licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

## Suporte

Para suporte e dúvidas:

1. **Verifique a Documentação**: Revise este README e documentação inline do código
2. **Busque Issues**: Procure por issues existentes no GitHub
3. **Crie Issue**: Submeta relatórios detalhados de bugs ou solicitações de recursos
4. **Console do Desenvolvedor**: Use `make logs` para visualizar logs da aplicação
