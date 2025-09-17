# Frontend Implementation Guide - ZapSign Document Management

## Overview

This document provides a comprehensive guide for implementing the Angular frontend for the ZapSign Document Management system. The application follows a clean architecture pattern with proper separation of concerns.

## Environment Configuration

### API Base URLs
- **Development**: `http://localhost:8000`
- **Production**: `https://f3679db77f6f.ngrok-free.app`

### CORS Configuration
CORS is properly configured on the backend to accept requests from `http://localhost:4200` (Angular dev server).

## Application Flow

### 1. Companies List Page
- Display all companies in a list/table format
- Each company item should be clickable to navigate to company details

### 2. Company Details Page
- Show company information
- Display associated documents list
- Each document in the list should be clickable to navigate to document details

### 3. Document Details Page
- Show complete document information
- Include an "AI Analysis" section with a button to trigger analysis
- Display analysis results (missing topics, summary, insights)

## API Endpoints and Implementation

### Companies API

#### GET /api/companies/ (List Companies)
**Purpose**: Retrieve all companies for the main listing page

**Request**:
```typescript
// No body required
GET /api/companies/
```

**Response**:
```json
{
  "success": true,
  "code": 200,
  "message": "Companies retrieved successfully",
  "data": [
    {
      "id": 1,
      "name": "Empresa ABC Ltda",
      "api_token": "live_c5f1a6b2d8e9f0g1h2i3j4k5l6m7n8o9",
      "created_at": "2024-01-15T10:30:00.123456Z",
      "last_updated_at": "2024-01-15T10:30:00.123456Z"
    }
  ]
}
```

**Frontend Implementation**:
```typescript
// companies.service.ts
@Injectable()
export class CompaniesService {
  private apiUrl = environment.apiUrl;

  getCompanies(): Observable<ApiResponse<Company[]>> {
    return this.http.get<ApiResponse<Company[]>>(`${this.apiUrl}/api/companies/`);
  }
}

// Interface
interface Company {
  id: number;
  name: string;
  api_token: string;
  created_at: string;
  last_updated_at: string;
}
```

#### GET /api/companies/{id}/ (Get Company with Documents)
**Purpose**: Retrieve a specific company with its associated documents

**Request**:
```typescript
GET /api/companies/10/
```

**Response**:
```json
{
  "success": true,
  "code": 200,
  "message": "Company retrieved successfully",
  "data": {
    "id": 10,
    "name": "company_test",
    "api_token": "179780ba-9822-4c74-b866-f88de0f29cc045fd2d53-5917-4f26-8a99-958648fea9bb",
    "created_at": "2025-09-15T18:59:31.488118+00:00",
    "last_updated_at": "2025-09-15T18:59:31.488135+00:00",
    "documents": [
      {
        "id": 18,
        "name": "documento teste 2",
        "status": "pending"
      },
      {
        "id": 17,
        "name": "documento teste 2",
        "status": "pending"
      }
    ]
  }
}
```

**Frontend Implementation**:
```typescript
// companies.service.ts
getCompanyById(id: number): Observable<ApiResponse<CompanyWithDocuments>> {
  return this.http.get<ApiResponse<CompanyWithDocuments>>(`${this.apiUrl}/api/companies/${id}/`);
}

// Interfaces
interface CompanyWithDocuments extends Company {
  documents: DocumentSummary[];
}

interface DocumentSummary {
  id: number;
  name: string;
  status: string;
}
```

### Documents API

#### GET /api/documents/{id}/ (Get Document Details)
**Purpose**: Retrieve complete information about a specific document

**Request**:
```typescript
GET /api/documents/18/
```

**Response**:
```json
{
  "success": true,
  "code": 200,
  "message": "Document retrieved successfully",
  "data": {
    "id": 18,
    "company": {
      "id": 10,
      "name": "company_test",
      "api_token": "179780ba-9822-4c74-b866-f88de0f29cc045fd2d53-5917-4f26-8a99-958648fea9bb",
      "created_at": "2025-09-15T18:59:31.488118+00:00",
      "last_updated_at": "2025-09-15T18:59:31.488135+00:00"
    },
    "name": "documento teste 2",
    "signers": [
      {
        "id": 25,
        "name": "João Silva",
        "email": "joao@example.com",
        "token": "signer_token_abc123",
        "status": "pending",
        "external_id": "ext_signer_001",
        "created_at": "2024-03-01T14:20:00.123456Z",
        "last_updated_at": "2024-03-01T14:20:00.123456Z"
      }
    ],
    "status": "pending",
    "token": "doc_token_xyz789",
    "open_id": 45678,
    "created_by": "admin@empresa.com",
    "external_id": "ext_doc_2024_001",
    "created_at": "2024-03-01T14:20:00.000000Z",
    "last_updated_at": "2024-03-01T14:20:00.000000Z",
    "pdf_url": "https://s3.amazonaws.com/zapsign-docs/contrato-servicos-45678.pdf",
    "processing_status": "completed",
    "checksum": "sha256:a4b5c6d7e8f9g0h1i2j3k4l5m6n7o8p9q0r1s2t3u4v5w6x7y8z9",
    "version_id": "550e8400-e29b-41d4-a716-446655440000"
  }
}
```

**Frontend Implementation**:
```typescript
// documents.service.ts
@Injectable()
export class DocumentsService {
  private apiUrl = environment.apiUrl;

  getDocumentById(id: number): Observable<ApiResponse<Document>> {
    return this.http.get<ApiResponse<Document>>(`${this.apiUrl}/api/documents/${id}/`);
  }
}

// Interfaces
interface Document {
  id: number;
  company: Company;
  name: string;
  signers: Signer[];
  status: string;
  token: string;
  open_id: number;
  created_by: string;
  external_id: string;
  created_at: string;
  last_updated_at: string;
  pdf_url: string;
  processing_status: string;
  checksum: string;
  version_id: string;
}

interface Signer {
  id: number;
  name: string;
  email: string;
  token: string;
  status: string;
  external_id: string;
  created_at: string;
  last_updated_at: string;
}
```

#### POST /api/documents/{id}/analyze/ (AI Document Analysis)
**Purpose**: Trigger AI analysis for a document and retrieve insights

**Request**:
```typescript
POST /api/documents/18/analyze/
Content-Type: application/json

{
  "force_reanalysis": false  // optional, default false
}
```

**Response**:
```json
{
  "success": true,
  "code": 200,
  "message": "Document analyzed successfully",
  "data": {
    "success": true,
    "message": "Document analyzed successfully",
    "analysis": {
      "id": 21,
      "document_id": 18,
      "missing_topics": [
        "\"Seria interessante adicionar a data em que a procuração foi emitida.\"",
        "\"Que tal incluir mais detalhes sobre os poderes concedidos na procuração?\"",
        "\"Uma ideia seria fornecer informações de contato do outorgado para facilitar a comunicação.\""
      ],
      "summary": "O documento é uma procuração particular onde uma pessoa nomeia outra para representá-la em todos os atos da vida civil.",
      "insights": [
        "1. O documento fornece informações claras sobre quem está outorgando os poderes e quem está sendo nomeado como representante.",
        "2. A utilização de assinatura eletrônica via ZapSign demonstra modernidade e praticidade no processo.",
        "3. A completude das informações é satisfatória, porém a inclusão de mais detalhes poderia enriquecer o documento."
      ],
      "analyzed_at": "2025-09-17T03:10:07.434132-03:00"
    }
  }
}
```

**Frontend Implementation**:
```typescript
// documents.service.ts
analyzeDocument(documentId: number, forceReanalysis: boolean = false): Observable<ApiResponse<AnalysisResponse>> {
  const body = { force_reanalysis: forceReanalysis };
  return this.http.post<ApiResponse<AnalysisResponse>>(`${this.apiUrl}/api/documents/${documentId}/analyze/`, body);
}

// Interfaces
interface AnalysisResponse {
  success: boolean;
  message: string;
  analysis: Analysis;
}

interface Analysis {
  id: number;
  document_id: number;
  missing_topics: string[];
  summary: string;
  insights: string[];
  analyzed_at: string;
}
```

## Error Handling

All API responses follow a standardized format. Always check the `success` field:

```typescript
// Generic API Response interface
interface ApiResponse<T> {
  success: boolean;
  code: number;
  message: string;
  data?: T;
}

// Error handling example
this.documentsService.getDocumentById(id).subscribe({
  next: (response) => {
    if (response.success) {
      this.document = response.data;
    } else {
      this.handleError(response.message);
    }
  },
  error: (error) => {
    this.handleError('Erro ao carregar documento');
  }
});
```

## Common HTTP Status Codes

- **200**: Success
- **201**: Created
- **400**: Bad Request (validation errors)
- **404**: Not Found
- **409**: Conflict (already exists)
- **422**: Unprocessable Entity (analysis failed)
- **500**: Internal Server Error

## Routing Structure

Suggested Angular routing structure:

```typescript
const routes: Routes = [
  { path: '', redirectTo: '/companies', pathMatch: 'full' },
  { path: 'companies', component: CompaniesListComponent },
  { path: 'companies/:id', component: CompanyDetailsComponent },
  { path: 'documents/:id', component: DocumentDetailsComponent },
  { path: '**', redirectTo: '/companies' }
];
```

## Components Structure

### 1. CompaniesListComponent
- Display companies in a table/card layout
- Navigate to company details on click
- Handle loading and error states

### 2. CompanyDetailsComponent
- Show company information
- Display documents list with basic info (id, name, status)
- Navigate to document details on document click

### 3. DocumentDetailsComponent
- Display complete document information
- Show signers information
- Include AI Analysis section with:
  - "Analyze Document" button
  - Loading state during analysis
  - Results display with three sections:
    - **Missing Topics**: List of suggested improvements
    - **Summary**: Brief description of the document
    - **Insights**: Key observations and recommendations

## UI/UX Recommendations

### Company Details Page
- Use cards or sections to organize information
- Make documents table sortable by name, status, date
- Add status badges with different colors (pending, signed, etc.)

### Document Details Page
- Use tabbed interface for document info and analysis
- Display PDF link prominently if available
- Use collapsible sections for signers list
- Add loading spinners for analysis requests

### AI Analysis Section
- Use distinct visual styling (colored border, different background)
- Display analysis timestamp
- Allow re-analysis with confirmation dialog
- Use icons for each section (missing topics, summary, insights)

## Loading States and Error Handling

Implement proper loading states for all async operations:

```typescript
// Component example
export class DocumentDetailsComponent {
  document: Document | null = null;
  analysis: Analysis | null = null;
  isLoading = false;
  isAnalyzing = false;
  error: string | null = null;

  async analyzeDocument(): Promise<void> {
    this.isAnalyzing = true;
    this.error = null;

    try {
      const response = await this.documentsService.analyzeDocument(this.documentId).toPromise();
      if (response.success) {
        this.analysis = response.data.analysis;
      } else {
        this.error = response.message;
      }
    } catch (error) {
      this.error = 'Erro ao analisar documento';
    } finally {
      this.isAnalyzing = false;
    }
  }
}
```

## Environment Configuration

```typescript
// environment.ts (development)
export const environment = {
  production: false,
  apiUrl: 'http://localhost:8000'
};

// environment.prod.ts (production)
export const environment = {
  production: true,
  apiUrl: 'https://f3679db77f6f.ngrok-free.app'
};
```

This guide provides all the necessary information to implement a complete frontend for the ZapSign Document Management system following modern Angular best practices.