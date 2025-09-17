# Quote Submission & Standardization Specification

## Feature Name: Multi-Format Quote Collection System

## Overview
Enable contractors to submit quotes in their preferred format (PDF, email, photo, web form) while automatically standardizing all submissions into a comparable format for property managers.

## User Stories

### As a Contractor
- I want to submit quotes in my existing format without learning new systems
- I want to email quotes directly like I always do
- I want to upload my standard PDF quotes
- I want to take a photo of handwritten quotes
- I want quick confirmation my quote was received

### As a Property Manager
- I want all quotes displayed in the same format
- I want to compare prices side-by-side
- I want to see what's included vs excluded
- I want to understand timelines clearly
- I want to identify missing items across quotes

## Functional Requirements

### Submission Methods

1. **PDF Upload**
   - Drag-and-drop interface
   - Mobile file selection
   - Multiple page support
   - File size limit: 25MB
   - Automatic text extraction
   - Receipt confirmation

2. **Email Submission**
   - Unique project email address
   - Format: project-[ID]@bid.instabids.com
   - Accept attachments (PDF, images)
   - Parse email body for details
   - Auto-reply with confirmation
   - Support for forwarded emails

3. **Photo Submission**
   - Mobile camera capture
   - Multiple photos per quote
   - Image enhancement (auto-crop, brighten)
   - OCR text extraction
   - Handwriting recognition
   - Support for whiteboards/paper

4. **Web Form**
   - Simple structured form
   - Progressive disclosure
   - Save draft capability
   - Pre-filled contractor info
   - Mobile-optimized
   - Offline capability

### Web Form Structure

1. **Price Section**
   - Total price (required)
   - Labor cost (optional)
   - Materials cost (optional)
   - Additional fees (optional)
   - Tax calculation
   - Payment terms

2. **Timeline Section**
   - Start date availability
   - Estimated duration
   - Completion date
   - Working hours
   - Weather dependencies
   - Scheduling constraints

3. **Scope Section**
   - Work included (checklist + custom)
   - Materials provided
   - Materials needed from owner
   - Exclusions (important)
   - Assumptions made
   - Change order process

4. **Terms Section**
   - Warranty period
   - Payment schedule
   - Cancellation policy
   - Insurance coverage
   - License numbers
   - References available

### Standardization Engine

1. **Data Extraction**
   - OCR for images/PDFs
   - Pattern recognition for prices
   - Date parsing
   - Contractor info extraction
   - Line item detection
   - Terms identification

2. **Field Mapping**
   - Price components
   - Timeline elements
   - Scope items
   - Terms and conditions
   - Contact information
   - Special notes

3. **Standardized Output Format**
   ```
   CONTRACTOR: [Name]
   SUBMITTED: [Date/Time]
   
   PRICING
   - Total: $X,XXX
   - Labor: $X,XXX
   - Materials: $X,XXX
   - Other: $X,XXX
   
   TIMELINE
   - Can Start: [Date]
   - Duration: X days
   - Complete By: [Date]
   
   INCLUDED
   - [Item 1]
   - [Item 2]
   
   EXCLUDED
   - [Item 1]
   - [Item 2]
   
   NOTES
   - [Special conditions]
   ```

4. **Confidence Scoring**
   - High confidence (>90%): Auto-display
   - Medium (70-90%): Flag for review
   - Low (<70%): Request clarification

### Quote Management

1. **Quote Status**
   - Received
   - Processing
   - Standardized
   - Needs Clarification
   - Updated
   - Withdrawn

2. **Version Control**
   - Track quote updates
   - Show revision history
   - Compare versions
   - Latest version indicator

3. **Clarification System**
   - Auto-detect missing info
   - Request specific fields
   - Contractor notifications
   - Easy update mechanism

### Comparison Interface

1. **Side-by-Side View**
   - Up to 4 quotes visible
   - Synchronized scrolling
   - Highlight differences
   - Show missing items
   - Price variance indicators

2. **Comparison Matrix**
   ```
   Item        | Contractor A | Contractor B | Contractor C
   --------------------------------------------------------
   Total Price | $2,500       | $2,800       | $2,200
   Start Date  | Tomorrow     | Next Week    | 3 Days
   Duration    | 2 days       | 1 day        | 3 days
   Warranty    | 1 year       | 6 months     | 1 year
   [+] Included Items
   [+] Excluded Items
   ```

3. **Smart Insights**
   - Lowest price indicator
   - Fastest completion
   - Best warranty
   - Most comprehensive
   - Missing items alerts

## Non-Functional Requirements

### Performance
- Quote processing < 30 seconds
- OCR extraction < 10 seconds
- Standardization < 5 seconds
- Comparison load < 2 seconds

### Accuracy
- Price extraction > 95%
- Date extraction > 90%
- Contractor info > 98%
- Overall standardization > 85%

### Compatibility
- PDF versions 1.4+
- Image formats: JPG, PNG, HEIF
- Email clients: all major
- Browsers: Chrome, Safari, Firefox, Edge

## User Interface

### Contractor Submission
```
Submit Your Quote

Choose Method:
[📄 Upload PDF]
[📧 Email Instructions]
[📸 Take Photo]
[✍️ Fill Form]

Uploading...
[████████__] 80%

✓ Quote Received!
Project: Kitchen Plumbing Repair
Property: 123 Main St
Submitted: Just now

[View Project] [Submit Another]
```

### PM Comparison View
```
Quotes for: Kitchen Plumbing Repair
Status: 4 Quotes Received

[List View] [Compare View] [Download All]

┌─────────────┬─────────────┬─────────────┐
│ Joe's       │ Quick Fix   │ Pro Service │
│ Plumbing    │ Plumbers    │ Inc         │
├─────────────┼─────────────┼─────────────┤
│ $2,500      │ $2,800      │ $2,200*     │
│ Tomorrow    │ Next Week   │ In 3 Days   │
│ 2 days      │ 1 day*      │ 3 days      │
│ ⚠ Missing   │ ✓ Complete  │ ✓ Complete  │
└─────────────┴─────────────┴─────────────┘
* Lowest/Fastest

[Award Job] [Request Clarification]
```

## Business Logic

### Extraction Rules
- Currency: Look for $, USD, "dollars"
- Dates: MM/DD, Month DD, "next week"
- Duration: "days", "hours", "weeks"
- Phone: XXX-XXX-XXXX patterns
- Email: standard email regex

### Standardization Logic
1. Parse document/image/email
2. Extract structured data
3. Map to standard fields
4. Calculate confidence scores
5. Flag missing required fields
6. Format for display

### Auto-Actions
- Send receipt confirmation
- Process standardization
- Notify PM of new quote
- Request missing info
- Update comparison table

## Success Criteria
- [ ] 80% quotes successfully standardized
- [ ] 90% contractors submit successfully first try
- [ ] PM can compare in < 30 seconds
- [ ] 95% accurate price extraction
- [ ] Support 4+ submission methods

## Dependencies
- Project creation system (pending)
- Contractor profiles (pending)
- OCR service (needed)
- Email service (needed)
- File storage (complete)

## Security Considerations
- Validate file types and sizes
- Scan uploads for malware
- Secure email parsing
- Rate limit submissions
- Audit trail of all quotes
- Data encryption at rest

## Future Enhancements
- AI-powered quote analysis
- Historical price comparison
- Automated negotiation
- Quote templates
- Bulk quote requests
- API for contractor systems