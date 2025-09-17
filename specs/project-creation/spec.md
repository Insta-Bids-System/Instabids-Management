# Project Creation Specification

## Feature Name: Maintenance Project Creation

## Overview
Enable property managers to create maintenance projects in under 2 minutes, linking issues to specific properties and automatically inviting qualified contractors to submit bids.

## User Stories

### As a Property Manager
- I want to create a project quickly when issues arise
- I want contractors to understand the scope without site visits
- I want to set clear expectations for timeline and budget
- I want automatic contractor matching based on trade and location
- I want to track all projects in one place

### As a Contractor
- I want to see all project details clearly
- I want to know the urgency and timeline
- I want to see property access instructions
- I want to ask clarifying questions before bidding
- I want to know how many others are bidding

## Functional Requirements

### Project Creation Flow
1. **Property Selection**
   - Select from my properties list
   - Auto-populate property address and details
   - Show property access instructions
   - Display any property-specific notes

2. **Issue Description**
   - Project title (required, 100 chars)
   - Detailed description (required, 2000 chars)
   - Category selection:
     - Plumbing
     - Electrical
     - HVAC
     - Roofing
     - Painting
     - Landscaping
     - General Maintenance
     - Other (specify)

3. **Urgency & Timeline**
   - Urgency level:
     - Emergency (within 4 hours)
     - Urgent (within 24 hours)
     - Routine (within 72 hours)
     - Scheduled (custom date)
   - Bid deadline:
     - 24 hours
     - 48 hours
     - 72 hours
     - Custom (max 7 days)
   - Preferred start date
   - Completion deadline (optional)

4. **Documentation Upload**
   - Upload up to 10 photos (required minimum 1)
   - Upload up to 3 videos (2 min max each)
   - Take photos directly (mobile)
   - Add captions to each media
   - Reorder media items
   - Primary photo selection

5. **Budget & Preferences**
   - Budget range (optional):
     - Under $500
     - $500-$1,000
     - $1,000-$5,000
     - $5,000-$10,000
     - Over $10,000
     - Open to quotes
   - Payment terms preference
   - Insurance requirements (on/off)
   - License requirements (on/off)

6. **Contractor Invitation**
   - Auto-suggest contractors based on:
     - Trade category match
     - Service area coverage
     - Availability
     - Past performance
   - Option to invite specific contractors
   - Set minimum bids required (default 3)
   - Open vs invitation-only toggle

### Virtual Walk-Through
- Detailed location within property
- Specific access requirements:
  - Gate codes
  - Lock box codes
  - Key location
  - Contact for access
- Special conditions:
  - Pets on property
  - Hazards to note
  - Parking instructions
  - Work hour restrictions
- Virtual Q&A scheduling (optional)

### Project Management
1. **Save as Draft**
   - Save incomplete projects
   - Return to edit later
   - Draft expiry after 7 days

2. **Project Publishing**
   - Review before publishing
   - Confirmation of details
   - Immediate contractor notification
   - Project goes live status

3. **Project Tracking**
   - Unique project ID
   - QR code generation
   - Status tracking:
     - Draft
     - Open for Bids
     - Bidding Closed
     - Awarded
     - In Progress
     - Completed
   - View count
   - Bid count
   - Question count

### Contractor Discovery
1. **Automatic Matching**
   - Match by trade category
   - Filter by service area
   - Check availability
   - Verify credentials
   - Sort by rating

2. **Invitation Process**
   - Send to matched contractors
   - Stagger invitations (10 at a time)
   - Wait 2 hours between waves
   - Stop when minimum bids received

3. **Notification Methods**
   - SMS with project link
   - Email with full details
   - In-app notification
   - Include response deadline

## Non-Functional Requirements

### Performance
- Project creation < 2 minutes
- Photo upload < 5 seconds per photo
- Contractor matching < 3 seconds
- Notification dispatch < 30 seconds

### Accessibility
- Mobile-responsive design
- Offline draft capability
- Voice-to-text for descriptions
- Accessibility compliance (WCAG 2.1)

### Data Validation
- Required fields enforcement
- Photo size limit (10MB)
- Video size limit (100MB)
- Text length limits
- Profanity filtering

## User Interface

### Project Creation Wizard
```
Step 1: Select Property
[Property Dropdown v]
[Property details display]

Step 2: Describe Issue
Title: [_________________]
Description: [Text area]
Category: [Dropdown v]

Step 3: Set Timeline
Urgency: ( ) Emergency (•) Urgent ( ) Routine
Bid Deadline: [48 hours v]
Start Date: [Date picker]

Step 4: Add Photos/Videos
[Drop zone or camera]
[Thumbnail grid]

Step 5: Set Preferences
Budget: [Range selector]
[ ] Require Insurance
[ ] Require License

Step 6: Review & Publish
[Summary view]
[Edit] [Save Draft] [Publish]
```

### Mobile Interface
- Camera-first design
- Swipe between steps
- Voice recording option
- One-thumb navigation

## Business Logic

### Contractor Matching Algorithm
1. Filter by trade (exact match)
2. Filter by service area (zip code radius)
3. Filter by availability
4. Filter by credentials (if required)
5. Sort by:
   - Response rate (weight: 30%)
   - Rating (weight: 30%)
   - Completion rate (weight: 20%)
   - Price competitiveness (weight: 20%)

### Notification Rules
- Emergency: Immediate to all matched
- Urgent: Immediate to top 20
- Routine: Staggered over 24 hours
- Follow-up if < minimum bids

### Auto-Actions
- Close bidding at deadline
- Notify PM of new bids
- Alert if no bids after 24h
- Archive after 30 days inactive

## Success Criteria
- [ ] PM can create project in < 2 minutes
- [ ] 80% of projects receive 3+ bids
- [ ] First bid within 4 hours average
- [ ] 90% of contractors respond to invites
- [ ] 95% of projects have clear scope

## Dependencies
- Property management system (complete)
- User authentication (complete)
- File upload system (complete)
- Contractor profiles (pending)
- Notification system (pending)

## Security Considerations
- Validate file uploads (type, size, content)
- Sanitize all text inputs
- Rate limit project creation (10/day)
- Verify property ownership
- Audit trail of all actions

## Future Enhancements
- AI-powered scope generation
- Historical project templates
- Seasonal maintenance scheduling
- Multi-property batch projects
- Integration with work order systems