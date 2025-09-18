# Technical Implementation Plan: Quote Submission & Standardization

## Overview
Multi-channel quote collection system with AI-powered standardization that converts any format (PDF, email, photo, form) into comparable structured data for side-by-side analysis.

## Technical Architecture

### System Design
```
┌─────────────────────────────────────────────────────┐
│               Quote Submission Channels              │
│  PDF Upload | Email | Photo Capture | Web Form      │
└────────┬───────────┬──────────┬──────────┬─────────┘
         │           │          │          │
    ┌────▼───────────▼──────────▼──────────▼────┐
    │         Ingestion & Validation Layer       │
    │    (File validation, spam filtering)       │
    └────────────────────┬───────────────────────┘
                         │
    ┌────────────────────▼───────────────────────┐
    │        Standardization Engine              │
    │  (OCR, NLP, Pattern Matching, Mapping)     │
    └────────────────────┬───────────────────────┘
                         │
    ┌────────────────────▼───────────────────────┐
    │         Structured Data Store              │
    │    (Quotes, Line Items, Confidence)        │
    └────────────────────┬───────────────────────┘
                         │
    ┌────────────────────▼───────────────────────┐
    │        Comparison & Analytics              │
    │    (Side-by-side, Insights, Alerts)        │
    └─────────────────────────────────────────────┘
```

### Technology Stack
- **OCR Service**: AWS Textract or Google Document AI
- **Email Processing**: SendGrid Inbound Parse + AWS SES
- **Image Processing**: Sharp.js for enhancement
- **NLP**: OpenAI GPT-4 for extraction & mapping
- **Storage**: AWS S3 for originals, PostgreSQL for structured
- **Queue**: Redis + Bull for async processing
- **Real-time**: WebSocket for live updates

## Core Components

### 1. Multi-Channel Ingestion System
```typescript
interface QuoteSubmission {
  id: string;
  projectId: string;
  contractorId: string;
  method: 'pdf' | 'email' | 'photo' | 'form';
  originalContent: Buffer | string;
  metadata: {
    submittedAt: Date;
    fileSize?: number;
    mimeType?: string;
    emailHeaders?: Record<string, string>;
  };
  status: SubmissionStatus;
}

class IngestionService {
  async handlePDFUpload(file: File): Promise<QuoteSubmission>
  async handleEmailWebhook(payload: InboundEmail): Promise<QuoteSubmission>
  async handlePhotoCapture(images: Blob[]): Promise<QuoteSubmission>
  async handleFormSubmission(data: QuoteForm): Promise<QuoteSubmission>
}
```

### 2. Standardization Engine
```python
class StandardizationEngine:
    def __init__(self):
        self.ocr_client = TextractClient()
        self.nlp_client = OpenAIClient()
        self.pattern_matcher = PatternMatcher()
    
    async def process_quote(submission: QuoteSubmission) -> StandardizedQuote:
        # Step 1: Extract text
        raw_text = await self.extract_text(submission)
        
        # Step 2: Parse with NLP
        structured_data = await self.nlp_parse(raw_text)
        
        # Step 3: Pattern matching for prices/dates
        extracted_fields = self.pattern_matcher.extract(raw_text)
        
        # Step 4: Map to standard schema
        standardized = self.map_to_schema(structured_data, extracted_fields)
        
        # Step 5: Calculate confidence
        confidence = self.calculate_confidence(standardized)
        
        return StandardizedQuote(
            data=standardized,
            confidence=confidence,
            original_id=submission.id
        )
```

### 3. Data Extraction Patterns
```python
EXTRACTION_PATTERNS = {
    'total_price': [
        r'\$[\d,]+\.?\d*',
        r'total[:\s]+\$?[\d,]+',
        r'quote[:\s]+\$?[\d,]+',
        r'estimate[:\s]+\$?[\d,]+'
    ],
    'start_date': [
        r'\d{1,2}/\d{1,2}/\d{2,4}',
        r'(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\s+\d{1,2}',
        r'(tomorrow|next week|asap|immediately)'
    ],
    'duration': [
        r'\d+\s*(days?|weeks?|hours?)',
        r'completion[:\s]+\d+\s*(days?|weeks?)'
    ],
    'warranty': [
        r'\d+\s*(year|month|day)s?\s*warranty',
        r'guaranteed?\s*for\s*\d+\s*(year|month)s?'
    ]
}
```

### 4. Standardized Quote Schema
```typescript
interface StandardizedQuote {
  // Core Fields
  quoteId: string;
  projectId: string;
  contractorId: string;
  
  // Pricing
  pricing: {
    total: number;
    confidence: number;
    breakdown?: {
      labor?: number;
      materials?: number;
      other?: number;
      tax?: number;
    };
    paymentTerms?: string;
  };
  
  // Timeline
  timeline: {
    startDate?: Date;
    duration?: number; // days
    completionDate?: Date;
    availability?: string;
    confidence: number;
  };
  
  // Scope
  scope: {
    included: string[];
    excluded: string[];
    materials: {
      provided: string[];
      required: string[];
    };
    assumptions: string[];
    confidence: number;
  };
  
  // Terms
  terms: {
    warranty?: string;
    insurance?: string;
    license?: string;
    cancellation?: string;
    confidence: number;
  };
  
  // Meta
  metadata: {
    submissionMethod: string;
    submittedAt: Date;
    processedAt: Date;
    overallConfidence: number;
    flagsForReview: string[];
    version: number;
  };
}
```

## Database Schema

### Quote Tables
```sql
-- Main quotes table
CREATE TABLE quotes (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  project_id UUID REFERENCES projects(id) NOT NULL,
  contractor_id UUID REFERENCES user_profiles(id) NOT NULL,
  submission_method quote_submission_method NOT NULL,
  original_file_url TEXT,
  standardized_data JSONB NOT NULL,
  confidence_score DECIMAL(3,2) CHECK (confidence_score >= 0 AND confidence_score <= 1),
  status quote_status DEFAULT 'processing',
  version INTEGER DEFAULT 1,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Line items for detailed breakdown
CREATE TABLE quote_items (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  quote_id UUID REFERENCES quotes(id) ON DELETE CASCADE,
  item_type VARCHAR(50), -- 'labor', 'material', 'other'
  description TEXT,
  quantity DECIMAL,
  unit_price DECIMAL,
  total_price DECIMAL,
  confidence DECIMAL(3,2)
);

-- Extraction confidence tracking
CREATE TABLE quote_extractions (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  quote_id UUID REFERENCES quotes(id) ON DELETE CASCADE,
  field_name VARCHAR(100),
  extracted_value TEXT,
  confidence DECIMAL(3,2),
  extraction_method VARCHAR(50) -- 'ocr', 'nlp', 'pattern', 'form'
);
```

## API Endpoints

### Submission Endpoints
```
POST /api/quotes/upload-pdf
  → Upload PDF quote file
  
POST /api/quotes/submit-photos
  → Submit quote via photos
  
POST /api/quotes/submit-form
  → Submit via structured form
  
GET /api/quotes/email-address/{projectId}
  → Get unique email for project
  
POST /api/webhooks/inbound-email
  → SendGrid webhook for emails
```

### Management Endpoints
```
GET /api/quotes/project/{projectId}
  → Get all quotes for project
  
GET /api/quotes/{quoteId}
  → Get specific quote details
  
PUT /api/quotes/{quoteId}/clarify
  → Submit clarification
  
GET /api/quotes/compare/{projectId}
  → Get comparison matrix
  
POST /api/quotes/{quoteId}/extract-retry
  → Retry extraction
```

## Implementation Phases

### Phase 1: Form Submission (Day 1)
- Build web form interface
- Create quote database tables
- Implement direct submission API
- Add to comparison view

### Phase 2: PDF Upload (Day 2)
- Implement file upload endpoint
- Integrate AWS Textract
- Build extraction pipeline
- Add confidence scoring

### Phase 3: Email Integration (Day 3)
- Set up SendGrid inbound parse
- Create project email addresses
- Build email parser
- Handle attachments

### Phase 4: Photo Capture (Day 4)
- Build mobile camera interface
- Implement image enhancement
- Add OCR for photos
- Support handwriting

### Phase 5: Standardization Engine (Day 5)
- Implement NLP parsing
- Build pattern matchers
- Create mapping logic
- Calculate confidence scores

### Phase 6: Comparison Interface (Day 6)
- Build side-by-side view
- Create comparison matrix
- Add smart insights
- Implement filtering/sorting

## Performance Optimization

### Processing Pipeline
```typescript
class QuoteProcessor {
  private queue: Queue;
  
  async processQuote(submissionId: string) {
    // Stage 1: Quick extraction (< 5s)
    const quickExtract = await this.quickOCR(submissionId);
    await this.saveInitialExtract(quickExtract);
    
    // Stage 2: Deep extraction (async, < 30s)
    await this.queue.add('deep-extraction', {
      submissionId,
      priority: this.calculatePriority()
    });
    
    // Stage 3: Enrichment (async, background)
    await this.queue.add('enrichment', {
      submissionId,
      delay: 60000 // 1 minute later
    });
  }
}
```

### Caching Strategy
- Cache OCR results for 24 hours
- Cache standardized quotes until updated
- Pre-compute comparison matrices
- Store extraction patterns in Redis

## Security & Validation

### File Validation
```typescript
const FILE_VALIDATORS = {
  pdf: {
    maxSize: 25 * 1024 * 1024, // 25MB
    mimeTypes: ['application/pdf'],
    virusScan: true
  },
  image: {
    maxSize: 10 * 1024 * 1024, // 10MB
    mimeTypes: ['image/jpeg', 'image/png', 'image/heif'],
    dimensions: { maxWidth: 4096, maxHeight: 4096 }
  }
};
```

### Email Security
- SPF/DKIM verification
- Attachment scanning
- Spam filtering
- Rate limiting per contractor

## Testing Strategy

### Unit Tests
- Pattern matcher accuracy
- Field extraction precision
- Confidence calculations
- Schema mapping

### Integration Tests
- End-to-end submission flows
- OCR service integration
- Email webhook handling
- Real-time updates

### Performance Tests
- 100 concurrent uploads
- OCR processing time < 10s
- Standardization < 5s
- Comparison load < 2s

## Monitoring & Analytics

### Key Metrics
- Standardization success rate (target: 85%)
- Average confidence score
- Processing time by method
- Clarification request rate

### Alerts
- Confidence score < 70%
- Processing time > 30s
- Failed extractions > 10%
- Queue backup > 100 items

## Success Criteria

- ✅ 4+ submission methods working
- ✅ 85% successful standardization
- ✅ < 30 second processing time
- ✅ 95% price extraction accuracy
- ✅ Side-by-side comparison working
- ✅ Mobile-optimized interfaces
- ✅ Real-time status updates