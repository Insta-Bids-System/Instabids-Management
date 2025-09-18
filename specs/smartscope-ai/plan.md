# Technical Implementation Plan: SmartScope AI

## Overview
AI-powered visual analysis system using OpenAI Vision API to automatically extract detailed work scopes from property photos, enabling accurate remote quotes without site visits.

## Technical Architecture

### System Design
```
┌─────────────────────────────────────────────────────┐
│              Photo Upload Interface                 │
│         (Mobile Camera / File Upload)               │
└─────────────────────┬───────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────┐
│           Image Processing Pipeline                 │
│   (Validation, Enhancement, Optimization)           │
└─────────────────────┬───────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────┐
│            OpenAI Vision Analysis                   │
│    (Multi-image Context, Category Prompts)          │
└─────────────────────┬───────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────┐
│          Scope Extraction & Structuring             │
│    (NLP Processing, Confidence Scoring)             │
└─────────────────────┬───────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────┐
│           Human Review & Enhancement                │
│      (Edit, Approve, Feedback Loop)                 │
└─────────────────────┬───────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────┐
│          Distribution to Contractors                │
│      (Standardized Scope, Confidence Levels)        │
└─────────────────────────────────────────────────────┘
```

### Technology Stack
- **Vision AI**: OpenAI Vision API (GPT-4V)
- **Image Processing**: Sharp.js for optimization
- **Queue System**: Bull + Redis for async processing
- **Storage**: AWS S3 for images
- **Caching**: Redis for API responses
- **Monitoring**: DataDog for API usage tracking

## Core Components

### 1. Image Processing Service
```typescript
class ImageProcessor {
  private sharp = require('sharp');
  
  async prepareForAnalysis(image: Buffer): Promise<ProcessedImage> {
    // Optimize for API (max 20MB, 2048x2048)
    const optimized = await this.sharp(image)
      .resize(2048, 2048, { 
        fit: 'inside',
        withoutEnlargement: true 
      })
      .jpeg({ quality: 85 })
      .toBuffer();
    
    // Extract metadata
    const metadata = await this.extractMetadata(optimized);
    
    // Assess quality
    const quality = await this.assessQuality(optimized);
    
    return {
      buffer: optimized,
      metadata,
      quality,
      isUsable: quality.score > 0.7
    };
  }
  
  async batchPrepare(images: Buffer[]): Promise<ProcessedImage[]> {
    // Group related images
    const groups = await this.groupRelatedImages(images);
    
    // Process in parallel
    return Promise.all(
      images.map(img => this.prepareForAnalysis(img))
    );
  }
}
```

### 2. Vision AI Analysis Engine
```typescript
class SmartScopeAnalyzer {
  private openai: OpenAI;
  private promptBuilder: PromptBuilder;
  
  async analyzeProject(
    images: ProcessedImage[],
    context: ProjectContext
  ): Promise<ScopeAnalysis> {
    // Build category-specific prompt
    const prompt = this.promptBuilder.build(context);
    
    // Prepare messages with images
    const messages = [
      {
        role: "system",
        content: this.getSystemPrompt(context.category)
      },
      {
        role: "user",
        content: [
          { type: "text", text: prompt },
          ...images.map(img => ({
            type: "image_url",
            image_url: {
              url: `data:image/jpeg;base64,${img.buffer.toString('base64')}`,
              detail: "high"
            }
          }))
        ]
      }
    ];
    
    // Call OpenAI Vision
    const response = await this.openai.chat.completions.create({
      model: "gpt-4-vision-preview",
      messages,
      max_tokens: 2000,
      temperature: 0.3 // Lower for consistency
    });
    
    // Parse and structure response
    return this.parseAnalysis(response.choices[0].message.content);
  }
}
```

### 3. Prompt Engineering System
```typescript
class PromptBuilder {
  private templates = {
    plumbing: `
      Analyze these plumbing maintenance photos. Identify:
      1. Type and location of plumbing issue
      2. Affected fixtures or pipes
      3. Severity of water damage if present
      4. Required repairs and replacements
      5. Parts needed (be specific about sizes)
      6. Special tools required
      7. Estimated repair time
      8. Emergency vs routine classification
    `,
    electrical: `
      Analyze these electrical maintenance photos. Identify:
      1. Electrical components affected
      2. Visible code violations or safety hazards
      3. Required repairs or replacements
      4. Specific parts needed (amps, voltage, type)
      5. Whether permit might be required
      6. Safety precautions needed
      7. Estimated work time
      8. Urgency level based on safety
    `,
    hvac: `
      Analyze these HVAC system photos. Identify:
      1. System type and approximate age
      2. Visible problems or wear
      3. Required repairs or maintenance
      4. Parts or supplies needed
      5. Whether specialized tools required
      6. Estimated service time
      7. Seasonal urgency factors
      8. Energy efficiency concerns
    `
  };
  
  build(context: ProjectContext): string {
    const base = this.templates[context.category] || this.templates.general;
    
    return `
      ${base}
      
      Additional Context:
      - Property Type: ${context.propertyType}
      - Reported Issue: ${context.description}
      - Urgency: ${context.urgency}
      
      Format your response as structured JSON with confidence scores for each element.
    `;
  }
}
```

### 4. Scope Structuring Service
```typescript
interface StructuredScope {
  primaryIssue: {
    description: string;
    severity: 'emergency' | 'high' | 'medium' | 'low';
    confidence: number;
  };
  
  workScope: Array<{
    task: string;
    priority: number;
    estimatedTime: number;
    confidence: number;
  }>;
  
  materials: Array<{
    item: string;
    quantity: string;
    specification: string;
    confidence: number;
  }>;
  
  risks: Array<{
    risk: string;
    likelihood: 'high' | 'medium' | 'low';
    mitigation: string;
  }>;
  
  additionalObservations: string[];
  overallConfidence: number;
  processingMetadata: {
    apiVersion: string;
    processingTime: number;
    imageCount: number;
    totalTokens: number;
  };
}

class ScopeStructurer {
  structure(rawAnalysis: string): StructuredScope {
    // Parse JSON response
    const parsed = JSON.parse(rawAnalysis);
    
    // Validate required fields
    this.validateSchema(parsed);
    
    // Calculate confidence scores
    const confidence = this.calculateConfidence(parsed);
    
    // Enhance with additional data
    const enhanced = this.enhance(parsed, confidence);
    
    return enhanced;
  }
  
  private calculateConfidence(analysis: any): number {
    // Weight different factors
    const factors = {
      imageQuality: 0.2,
      detailLevel: 0.3,
      consistencyScore: 0.2,
      completeness: 0.3
    };
    
    return Object.entries(factors)
      .reduce((acc, [key, weight]) => {
        return acc + (this.scoreFactor(analysis, key) * weight);
      }, 0);
  }
}
```

## Database Schema

### SmartScope Tables
```sql
-- AI analysis records
CREATE TABLE smartscope_analyses (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  project_id UUID REFERENCES projects(id) NOT NULL,
  analysis_version INTEGER DEFAULT 1,
  raw_response JSONB NOT NULL,
  structured_scope JSONB NOT NULL,
  overall_confidence DECIMAL(3,2) CHECK (overall_confidence >= 0 AND overall_confidence <= 1),
  processing_time_ms INTEGER,
  api_tokens_used INTEGER,
  api_cost_cents INTEGER,
  status VARCHAR(50) DEFAULT 'processing',
  created_by UUID REFERENCES user_profiles(id),
  reviewed_by UUID REFERENCES user_profiles(id),
  reviewed_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Scope items extracted
CREATE TABLE scope_items (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  analysis_id UUID REFERENCES smartscope_analyses(id) ON DELETE CASCADE,
  item_type VARCHAR(50), -- 'issue', 'task', 'material', 'risk'
  description TEXT NOT NULL,
  details JSONB,
  confidence DECIMAL(3,2),
  human_verified BOOLEAN DEFAULT FALSE,
  display_order INTEGER
);

-- Feedback for improvement
CREATE TABLE scope_feedback (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  analysis_id UUID REFERENCES smartscope_analyses(id),
  user_id UUID REFERENCES user_profiles(id),
  feedback_type VARCHAR(50), -- 'accurate', 'inaccurate', 'missing', 'extra'
  details TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes
CREATE INDEX idx_analyses_project ON smartscope_analyses(project_id);
CREATE INDEX idx_analyses_confidence ON smartscope_analyses(overall_confidence);
CREATE INDEX idx_scope_items_analysis ON scope_items(analysis_id);
```

## API Endpoints

### Analysis Endpoints
```
POST /api/smartscope/analyze
  → Trigger analysis for project photos
  Body: {
    projectId: string,
    imageIds: string[],
    context: {
      category: string,
      description: string,
      urgency: string
    }
  }

GET /api/smartscope/analysis/{projectId}
  → Get analysis results for project

PUT /api/smartscope/analysis/{analysisId}
  → Update/edit analysis results

POST /api/smartscope/feedback
  → Submit accuracy feedback
```

### Scope Management
```
GET /api/smartscope/scope/{projectId}
  → Get structured scope for project

PUT /api/smartscope/scope/{projectId}/items
  → Add/edit scope items

POST /api/smartscope/scope/{projectId}/approve
  → Approve AI-generated scope

GET /api/smartscope/confidence/{projectId}
  → Get confidence breakdown
```

## Implementation Phases

### Phase 1: OpenAI Integration (Day 1-2)
- Set up OpenAI client
- Implement basic prompt templates
- Build image encoding pipeline
- Test with sample images

### Phase 2: Processing Pipeline (Day 3)
- Image optimization service
- Batch processing queue
- Response parsing
- Error handling

### Phase 3: Scope Structuring (Day 4)
- JSON schema validation
- Confidence calculations
- Database storage
- API endpoints

### Phase 4: Category Specialization (Day 5)
- Category-specific prompts
- Industry terminology
- Material specifications
- Time estimates

### Phase 5: Human Review (Day 6)
- Review interface
- Edit capabilities
- Approval workflow
- Feedback collection

### Phase 6: Integration (Day 7)
- Project creation integration
- Contractor view
- Quote comparison
- Analytics dashboard

## Performance Optimization

### API Cost Management
```typescript
class CostOptimizer {
  async optimizeRequest(images: Buffer[], context: any) {
    // Use lower resolution for initial analysis
    const lowRes = await this.createLowRes(images);
    const quickAnalysis = await this.quickAnalyze(lowRes);
    
    // Only use high-res for uncertain areas
    if (quickAnalysis.confidence < 0.8) {
      const detailed = await this.detailedAnalyze(images);
      return this.merge(quickAnalysis, detailed);
    }
    
    return quickAnalysis;
  }
  
  async batchProjects(projects: Project[]) {
    // Group similar projects
    const groups = this.groupBySimilarity(projects);
    
    // Use cached results for similar issues
    return groups.map(group => 
      this.processGroup(group)
    );
  }
}
```

### Caching Strategy
```typescript
const CACHE_CONFIG = {
  analysisResults: {
    ttl: 24 * 60 * 60, // 24 hours
    key: (projectId) => `scope:${projectId}`
  },
  promptTemplates: {
    ttl: 7 * 24 * 60 * 60, // 1 week
    key: (category) => `prompt:${category}`
  },
  commonPatterns: {
    ttl: 30 * 24 * 60 * 60, // 30 days
    key: (pattern) => `pattern:${pattern}`
  }
};
```

## Monitoring & Analytics

### Key Metrics
```typescript
interface SmartScopeMetrics {
  // Accuracy
  confidenceScores: number[];
  feedbackAccuracy: number;
  humanOverrideRate: number;
  
  // Performance  
  avgProcessingTime: number;
  apiResponseTime: number;
  queueBacklog: number;
  
  // Usage
  dailyAnalyses: number;
  tokensUsed: number;
  apiCostUSD: number;
  
  // Business Impact
  clarificationReduction: number;
  quoteTurnaroundTime: number;
  contractorSatisfaction: number;
}
```

### Alerts
- API errors > 5% → Page on-call
- Confidence < 70% → Flag for review
- Cost > $10/hour → Notify admin
- Queue > 100 items → Scale workers

## Testing Strategy

### Unit Tests
- Prompt template generation
- Image processing pipeline
- Response parsing accuracy
- Confidence calculations

### Integration Tests
- OpenAI API integration
- End-to-end analysis flow
- Database operations
- Cache invalidation

### Accuracy Tests
```typescript
class AccuracyTester {
  async testAgainstGroundTruth() {
    const testCases = await this.loadTestCases();
    
    const results = await Promise.all(
      testCases.map(async (test) => {
        const analysis = await this.analyze(test.images);
        return this.compareToTruth(analysis, test.groundTruth);
      })
    );
    
    return {
      primaryIssueAccuracy: this.calculate(results, 'primary'),
      materialsAccuracy: this.calculate(results, 'materials'),
      timeEstimateAccuracy: this.calculate(results, 'time'),
      overall: this.calculateOverall(results)
    };
  }
}
```

## Security Considerations

### API Security
- Rotate API keys monthly
- Use environment variables
- Never log API responses with PII
- Rate limit per organization

### Image Security
- Sanitize EXIF data
- Scan for malicious content
- Limit file sizes
- Validate image formats

## Success Criteria

- ✅ 90% primary issue identification accuracy
- ✅ 85% severity assessment accuracy
- ✅ < 15 second analysis time
- ✅ 80% contractor satisfaction with scopes
- ✅ 50% reduction in clarification requests
- ✅ < $0.10 per project analysis cost
- ✅ 92% overall confidence target