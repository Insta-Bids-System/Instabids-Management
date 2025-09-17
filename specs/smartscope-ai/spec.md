# SmartScope AI Specification

## Feature Name: AI-Powered Scope Extraction

## Overview
Use OpenAI Vision to automatically analyze property maintenance photos and generate standardized work scopes, enabling contractors to understand project requirements without site visits.

## User Stories

### As a Property Manager
- I want AI to identify maintenance issues from photos
- I want detailed scope descriptions generated automatically
- I want to avoid explaining the same issue multiple times
- I want contractors to understand the work needed
- I want to reduce back-and-forth clarifications

### As a Contractor
- I want clear understanding of work required
- I want to identify potential issues from photos
- I want to estimate accurately without site visits
- I want to know materials and tools needed
- I want to spot additional problems

### As the Platform
- I want consistent scope descriptions
- I want reduced clarification requests
- I want faster quote turnaround
- I want better quote accuracy

## Functional Requirements

### Photo Analysis Pipeline

1. **Image Preprocessing**
   - Auto-orientation correction
   - Resolution optimization
   - Multiple angle detection
   - Image quality assessment
   - Brightness/contrast adjustment

2. **AI Analysis Request**
   - Send to OpenAI Vision API
   - Include context prompts
   - Property type context
   - Category-specific analysis
   - Multi-image correlation

3. **Scope Generation**
   - Problem identification
   - Severity assessment
   - Work required description
   - Materials needed
   - Time estimate suggestion
   - Safety considerations

### Analysis Categories

1. **Plumbing**
   - Leak detection and source
   - Pipe material identification
   - Fixture type and condition
   - Water damage assessment
   - Drainage issues
   - Required parts list

2. **Electrical**
   - Outlet/switch issues
   - Panel problems
   - Wiring visible issues
   - Code violations spotted
   - Safety hazards
   - Upgrade recommendations

3. **HVAC**
   - Unit type and model
   - Visible damage/wear
   - Ductwork issues
   - Filter condition
   - Thermostat problems
   - Maintenance needs

4. **Roofing**
   - Shingle/tile damage
   - Leak indicators
   - Gutter issues
   - Flashing problems
   - Structural concerns
   - Weather damage

5. **General Maintenance**
   - Paint needs
   - Drywall damage
   - Flooring issues
   - Appliance problems
   - Pest indicators
   - Cleaning requirements

### AI Prompting Strategy

1. **Context Provision**
   ```
   Analyze these maintenance photos:
   - Property Type: [Residential/Commercial]
   - Area: [Kitchen/Bathroom/etc]
   - Reported Issue: [PM Description]
   - Category: [Plumbing/Electrical/etc]
   ```

2. **Analysis Instructions**
   ```
   Identify:
   1. Primary problem
   2. Secondary issues
   3. Severity (Emergency/High/Medium/Low)
   4. Required repairs
   5. Materials needed
   6. Estimated time
   7. Safety concerns
   8. Access requirements
   ```

3. **Output Format**
   ```json
   {
     "primary_issue": "Leaking pipe under sink",
     "severity": "High",
     "scope_items": [
       "Replace P-trap assembly",
       "Check supply line connections",
       "Test for additional leaks"
     ],
     "materials": [
       "1.5\" P-trap kit",
       "Plumber's tape",
       "Pipe compound"
     ],
     "estimated_hours": 1.5,
     "safety_notes": "Water shutoff required",
     "additional_observations": [
       "Possible water damage to cabinet"
     ],
     "confidence": 0.92
   }
   ```

### Scope Enhancement

1. **Human Review Interface**
   - AI-generated scope display
   - Edit capabilities
   - Add/remove items
   - Adjust estimates
   - Flag inaccuracies

2. **Learning Feedback**
   - Contractor corrections
   - PM validations
   - Actual vs estimated
   - Pattern recognition
   - Improvement tracking

3. **Scope Standardization**
   - Consistent terminology
   - Industry-standard descriptions
   - Code reference inclusion
   - Material specifications
   - Tool requirements

### Integration Points

1. **Project Creation**
   - Trigger on photo upload
   - Process during creation
   - Display results immediately
   - Allow override/edit

2. **Contractor View**
   - Show AI analysis
   - Highlight uncertainties
   - Display confidence scores
   - Link to photos

3. **Quote Comparison**
   - Match quote items to scope
   - Identify missing items
   - Flag over-scoping
   - Calculate completeness

## Non-Functional Requirements

### Performance
- Analysis completion < 15 seconds
- Batch processing for multiple photos
- Async processing with status updates
- Caching of results

### Accuracy Targets
- Primary issue identification > 90%
- Severity assessment > 85%
- Material identification > 75%
- Time estimates ±30%

### API Management
- Rate limiting (100 requests/min)
- Cost tracking per project
- Fallback for API failures
- Response caching

## User Interface

### Analysis Display
```
AI Scope Analysis ✨

Primary Issue: Leaking P-trap under kitchen sink
Severity: 🔴 High - Active water leak

Scope of Work:
✓ Replace P-trap assembly
✓ Inspect supply lines
✓ Check for cabinet damage
✓ Test all connections

Materials Needed:
• 1.5" P-trap kit
• Plumber's tape
• Pipe compound

Estimated Time: 1-2 hours

⚠️ Additional Observations:
- Possible water damage to cabinet floor
- Garbage disposal showing wear

Confidence: 92%
[Edit Scope] [Add Items] [Approve]
```

### Contractor Quote View
```
Project Scope (AI-Generated)

📸 Based on 4 photos analyzed

What We Found:
[Primary issue description]

Work Required:
1. [Scope item 1]
2. [Scope item 2]

View Analysis: [Expand]
View Photos: [Gallery]
Questions? [Ask PM]
```

## Business Logic

### Confidence Thresholds
- >90%: Display as primary
- 70-90%: Display with indicator
- <70%: Show as "possible"
- <50%: Don't display

### Cost Management
- Track API usage per organization
- Set monthly limits
- Batch similar requests
- Cache frequent patterns

### Fallback Logic
1. If API fails → Manual scope entry
2. If low confidence → Request more photos
3. If unclear → Prompt PM for details

## Success Criteria
- [ ] 80% scope accuracy per contractor feedback
- [ ] 50% reduction in clarification requests
- [ ] 90% of projects use AI scope
- [ ] 30% faster quote submissions
- [ ] 85% contractor satisfaction with scopes

## Dependencies
- OpenAI API access (needed)
- Photo upload system (complete)
- Project creation flow (pending)
- Contractor viewing interface (pending)

## Security Considerations
- No PII in API requests
- Secure API key management
- Photo sanitization
- Rate limiting per user
- Audit trail of analyses

## Cost Considerations
- OpenAI Vision API: ~$0.01 per image
- Average 5 images per project
- Target: <$0.10 per project
- Monthly budget: $500 initial

## Future Enhancements
- Custom model training
- Video analysis
- Before/after comparison
- Predictive maintenance
- Cost estimation
- Code compliance checking
- 3D reconstruction
- AR visualization