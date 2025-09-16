# Documentação: Fluxo de Análise de Documentos com IA

## Visão Geral

O sistema de análise de documentos com IA implementa o módulo M4 utilizando LangChain, vector stores, RAG (Retrieval-Augmented Generation) e embeddings para analisar o conteúdo de documentos e fornecer insights inteligentes.

## Arquitetura do Sistema

### Camadas da Clean Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        API Layer                            │
│  POST /api/documents/{id}/analyze/                         │
│  DocumentAnalysisSerializer                                │
└─────────────────────────┬───────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────┐
│                    Use Cases Layer                         │
│  AnalyzeDocumentUseCase                                    │
│  GetDocumentAnalysisUseCase                                │
└─────────────────────────┬───────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────┐
│                  Services Layer                            │
│  ┌─────────────────┐  ┌─────────────────┐                 │
│  │  AIAnalysisService │  │HeuristicService │                 │
│  │  (LangChain+RAG)   │  │   (Fallback)    │                 │
│  └─────────────────┘  └─────────────────┘                 │
└─────────────────────────┬───────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────┐
│                 Domain Entities                            │
│  Document (can_be_analyzed, analyze)                       │
│  DocumentAnalysis (missing_topics, summary, insights)      │
└─────────────────────────┬───────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────┐
│               Infrastructure Layer                         │
│  DocumentAnalysisRepository                                │
│  DocumentAnalysisModel (Django ORM)                        │
│  Mappers (Entity ↔ Model)                                  │
└─────────────────────────────────────────────────────────────┘
```

## Fluxo Completo de Análise

### 1. Requisição da API

```http
POST /api/documents/{id}/analyze/
Content-Type: application/json
{
  "force_reanalysis": false  // opcional
}
```

**Localização**: `api/views/document.py:analyze()`

### 2. Validação e Orquestração

O `AnalyzeDocumentUseCase` orquestra todo o processo:

```python
# core/use_cases/analyze_document.py
def execute(self, document_id: int, force_reanalysis: bool = False) -> DocumentAnalysis:
    # 1. Busca o documento
    document = self._document_repository.get_by_id(document_id)

    # 2. Valida se pode ser analisado
    if not document.can_be_analyzed():
        raise DocumentAnalysisError("Document cannot be analyzed")

    # 3. Verifica análise existente
    if not force_reanalysis:
        existing = self._analysis_repository.get_by_document_id(document_id)
        if existing:
            return existing

    # 4. Executa análise com estratégia plugável
    analysis = self._analysis_service.analyze_document(document)

    # 5. Persiste resultado
    return self._analysis_repository.save(analysis)
```

### 3. Estratégia de Análise

O sistema utiliza o **Strategy Pattern** com dois serviços:

#### 3.1 AIAnalysisService (Produção)
**Localização**: `core/services/analysis/ai_service.py`

```python
class AIAnalysisService:
    def __init__(self):
        self.embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
        self.llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.1)
        self.vector_store = None  # ChromaDB inicializado dinamicamente
```

**Fluxo de Análise com RAG**:

1. **Document Chunking**:
   ```python
   splitter = RecursiveCharacterTextSplitter(
       chunk_size=1000,
       chunk_overlap=200,
       separators=["\n\n", "\n", ". ", " "]
   )
   chunks = splitter.split_text(document.content)
   ```

2. **Vector Store Creation**:
   ```python
   # Cria embeddings para cada chunk
   self.vector_store = Chroma.from_texts(
       texts=chunks,
       embedding=self.embeddings,
       collection_name=f"doc_{document.id}"
   )
   ```

3. **RAG Chain Setup**:
   ```python
   retriever = self.vector_store.as_retriever(search_kwargs={"k": 3})
   rag_chain = (
       {"context": retriever, "question": RunnablePassthrough()}
       | self._create_analysis_prompt()
       | self.llm
       | StrOutputParser()
   )
   ```

4. **Contextual Analysis**:
   ```python
   # Recupera chunks relevantes e gera análise contextual
   analysis_result = rag_chain.invoke(
       "Analise este documento e forneça insights estruturados"
   )
   ```

#### 3.2 HeuristicAnalysisService (Fallback)
**Localização**: `core/services/analysis/heuristic_service.py`

```python
def analyze_document(self, document: Document) -> DocumentAnalysis:
    # Análise baseada em regras simples
    doc_type = self._classify_document_type(document.content)
    missing_topics = self._identify_missing_topics(document.content, doc_type)
    summary = self._generate_summary(document.content)
    insights = self._generate_insights(document.content, doc_type)
```

### 4. Estrutura da Resposta

#### Entidade DocumentAnalysis
**Localização**: `core/domain/entities/document_analysis.py`

```python
@dataclass
class DocumentAnalysis:
    document_id: int
    missing_topics: list[str]      # Tópicos ausentes identificados
    summary: str                   # Resumo do documento
    insights: list[str]            # Insights e recomendações
    analyzed_at: datetime          # Timestamp da análise
    id: Optional[int] = None

    def has_meaningful_analysis(self) -> bool:
        return bool(self.summary and (self.missing_topics or self.insights))

    def is_complete(self) -> bool:
        return bool(self.summary and self.missing_topics and self.insights)
```

### 5. Persistência de Dados

#### Modelo Django ORM
**Localização**: `core/orm/models.py`

```python
class DocumentAnalysisModel(models.Model):
    document = models.ForeignKey('DocumentModel', on_delete=models.CASCADE)
    missing_topics = models.JSONField(default=list)
    summary = models.TextField()
    insights = models.JSONField(default=list)
    analyzed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['document']),
            models.Index(fields=['analyzed_at']),
        ]
```

#### Mapeamento Entidade ↔ Modelo
**Localização**: `core/orm/mappers.py`

```python
class DocumentAnalysisMapper:
    @staticmethod
    def to_entity(model: DocumentAnalysisModel) -> DocumentAnalysis:
        return DocumentAnalysis(
            id=model.id,
            document_id=model.document_id,
            missing_topics=model.missing_topics,
            summary=model.summary,
            insights=model.insights,
            analyzed_at=model.analyzed_at
        )

    @staticmethod
    def to_model(entity: DocumentAnalysis) -> DocumentAnalysisModel:
        # Converte entidade para modelo Django
```

## Configuração e Dependências

### Variáveis de Ambiente

```bash
# .env
OPENAI_API_KEY=your_openai_api_key_here
```

### Dependências LangChain

```bash
pip3 install langchain langchain-openai chromadb tiktoken
```

**Pacotes utilizados**:
- `langchain`: Framework principal para LLM
- `langchain-openai`: Integração com OpenAI
- `chromadb`: Vector store para embeddings
- `tiktoken`: Tokenização para OpenAI

## Exemplos de Uso

### 1. Análise Simples

```bash
curl -X POST http://localhost:8000/api/documents/1/analyze/ \
  -H "Content-Type: application/json" \
  -d '{}'
```

**Resposta**:
```json
{
  "id": 1,
  "document_id": 1,
  "missing_topics": [
    "Cláusulas de rescisão",
    "Penalidades por descumprimento",
    "Foro competente"
  ],
  "summary": "Contrato de prestação de serviços entre ZapSign e cliente, estabelecendo termos de desenvolvimento de software com prazo de 6 meses.",
  "insights": [
    "Recomenda-se incluir cláusulas específicas sobre propriedade intelectual",
    "Considerar adicionar SLA (Service Level Agreement) detalhado",
    "Definir processo de aprovação de deliverables"
  ],
  "analyzed_at": "2025-09-15T23:45:30.123456Z"
}
```

### 2. Forçar Nova Análise

```bash
curl -X POST http://localhost:8000/api/documents/1/analyze/ \
  -H "Content-Type: application/json" \
  -d '{"force_reanalysis": true}'
```

## Qualidade e Testes

### Cobertura de Testes (127 testes)

- **Entidades**: Validação de regras de negócio
- **Use Cases**: Orquestração e fluxos de erro
- **Serviços**: Análise heurística e integração
- **API**: Endpoints e serialização
- **Repositórios**: Persistência e mapeamento

**Executar testes**:
```bash
make test
```

## Tratamento de Erros

### Tipos de Erro

1. **DocumentNotFoundError**: Documento não existe
2. **DocumentAnalysisError**: Documento não pode ser analisado
3. **AIServiceError**: Falha na análise com IA
4. **ValidationError**: Dados inválidos

### Estratégia de Fallback

```python
# O sistema tenta AI primeiro, depois fallback para heurístico
try:
    return self.ai_service.analyze_document(document)
except Exception as e:
    logger.warning(f"AI analysis failed: {e}")
    return self.heuristic_service.analyze_document(document)
```

## Monitoramento e Logs

### Logs Estruturados

```python
logger.info("Starting document analysis", extra={
    "document_id": document.id,
    "service_type": "ai",
    "user_id": request.user.id
})
```

### Métricas Importantes

- Tempo de resposta da análise
- Taxa de sucesso AI vs Heuristic
- Frequência de reanálises
- Tamanho dos documentos processados

## Melhorias Futuras

1. **Cache de Análises**: Redis para análises frequentes
2. **Análise Assíncrona**: Celery para documentos grandes
3. **Múltiplos Modelos**: Suporte a diferentes LLMs
4. **Análise Incremental**: Apenas mudanças no documento
5. **Feedback Loop**: Aprendizado baseado em correções do usuário

---

**Versão**: 1.0
**Data**: 15/09/2025
**Autor**: Sistema de Documentação Automática