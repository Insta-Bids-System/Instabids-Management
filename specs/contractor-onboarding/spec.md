# Contractor Onboarding Specification

## Feature Name: Contractor Registration & Profile

## Overview
Enable contractors to register, get verified, and set up comprehensive profiles that showcase their capabilities and define their service parameters for automatic job matching.

## User Stories

### As a Contractor
- I want to register quickly and start receiving job invitations
- I want to showcase my credentials and past work
- I want to define my service areas and specialties
- I want to control what types of jobs I receive
- I want to set my availability preferences

### As a Property Manager
- I want to see verified contractor credentials
- I want to know contractor service areas
- I want to view contractor specialties and experience
- I want to see contractor ratings and past work
- I want emergency availability indicators

### As an Admin
- I want to verify contractor licenses
- I want to validate insurance coverage
- I want to track contractor performance
- I want to manage contractor approvals

## Functional Requirements

### Registration Flow

1. **Basic Information**
   - Business name (required)
   - Contact name (required)
   - Email address (required, unique)
   - Phone number (required, SMS capable)
   - Business type:
     - Sole Proprietor
     - LLC
     - Corporation
     - Partnership

2. **Business Details**
   - Years in business
   - Number of employees
   - Business address
   - Website (optional)
   - Business description (500 chars)

3. **Credentials Upload**
   - Business license (required)
     - License number
     - Expiration date
     - Issuing authority
     - PDF/image upload
   - Insurance certificate (required)
     - General liability coverage amount
     - Expiration date
     - Carrier name
     - PDF upload
   - Additional certifications (optional)
     - Trade certifications
     - Manufacturer certifications
     - Safety certifications

4. **Trade Specialties**
   - Primary trade (required):
     - Plumbing
     - Electrical
     - HVAC
     - Roofing
     - Painting
     - Landscaping
     - Carpentry
     - General Handyman
   - Secondary trades (optional, max 3)
   - Specific services (checkboxes):
     - Emergency repairs
     - Preventive maintenance
     - New installations
     - Renovations
     - Inspections

5. **Service Areas**
   - Service area definition:
     - By ZIP codes (comma-separated)
     - By radius from address (miles)
     - By city/county selection
   - Maximum travel distance
   - Travel fee structure (optional)

6. **Availability Settings**
   - Regular hours:
     - Monday-Friday hours
     - Weekend availability
     - Holiday availability
   - Emergency availability:
     - 24/7 emergency service (yes/no)
     - Emergency response time
     - Emergency fee structure
   - Scheduling preferences:
     - Minimum notice required
     - Booking window (days out)
     - Blackout dates

7. **Job Preferences**
   - Minimum job size ($)
   - Maximum jobs per week
   - Property types served:
     - Residential
     - Commercial
     - Multi-family
     - HOA/Condo
   - Excluded job types
   - Budget ranges accepted

### Profile Setup

1. **Company Profile**
   - Company logo upload
   - Cover photo
   - About us section (1000 chars)
   - Mission statement
   - Awards and recognition

2. **Portfolio**
   - Past work photos (up to 20)
   - Before/after galleries
   - Project descriptions
   - Project categories
   - Customer testimonials

3. **Team Information**
   - Team size
   - Key personnel
   - Team photos (optional)
   - Certifications per team member

4. **Pricing Information**
   - Hourly rates (optional)
   - Service call fees
   - Payment methods accepted
   - Payment terms
   - Warranty information

### Verification Process

1. **Automated Checks**
   - License number validation (API)
   - Insurance verification
   - Business entity verification
   - Phone number verification (SMS)
   - Email verification

2. **Manual Review Queue**
   - Document authenticity check
   - Coverage adequacy review
   - Credential expiration tracking
   - Flag suspicious registrations

3. **Verification Statuses**
   - Pending Review
   - Additional Info Required
   - Verified
   - Rejected
   - Suspended

### Profile Management

1. **Profile Visibility**
   - Public profile URL
   - Search visibility toggle
   - Contact info privacy settings

2. **Update Capabilities**
   - Edit all profile sections
   - Update credentials before expiry
   - Seasonal availability changes
   - Service area modifications

3. **Performance Metrics**
   - Jobs completed
   - Average rating
   - Response rate
   - On-time completion rate
   - Customer satisfaction score

## Non-Functional Requirements

### Performance
- Registration completion < 10 minutes
- Document upload < 10 seconds
- Verification within 24 hours
- Profile load < 2 seconds

### Data Validation
- License format validation
- Insurance minimums check
- Phone number format
- ZIP code validation
- File size limits (10MB)

### Compliance
- State licensing requirements
- Insurance minimums by state
- Data privacy (CCPA/GDPR)
- Document retention policies

## User Interface

### Registration Wizard
```
Welcome, Contractor!
Let's get your business verified

Step 1: Business Info
Business Name: [___________]
Contact Name: [___________]
Email: [___________]
Phone: [___________]

Step 2: Upload Credentials
License: [Upload] ✓ Uploaded
Insurance: [Upload] ⏳ Uploading

Step 3: Define Services
Primary Trade: [Plumbing v]
☑ Emergency Service
☑ Preventive Maintenance

Step 4: Set Service Area
○ ZIP Codes: [___________]
● Radius: [25 miles v]

Step 5: Set Availability
Regular Hours: [Set Hours]
☑ Available for Emergencies

[Back] [Save Draft] [Continue]
```

### Contractor Dashboard
```
Dashboard | Profile | Jobs | Calendar | Settings

Welcome back, John's Plumbing!
Verification: ✓ Verified

Today's Overview:
• 3 New Job Invitations
• 2 Pending Quotes
• 1 Awarded Job

Quick Actions:
[Update Availability]
[View Invitations]
[Update Credentials]
```

## Business Logic

### Auto-Approval Rules
- Valid license + insurance = auto-approve
- Expired credentials = auto-suspend
- Missing info = pending status

### Job Matching Rules
1. Trade must match exactly
2. Service area must include property
3. Job size >= minimum preference
4. Contractor must be available
5. Not at weekly job limit

### Notification Triggers
- Registration complete
- Verification status change
- Credential expiring (30 days)
- New job match
- Profile view by PM

## Success Criteria
- [ ] Contractors verified within 24 hours
- [ ] 90% complete profiles
- [ ] 80% set emergency availability
- [ ] 95% accurate job matching
- [ ] 70% accept rate on invitations

## Dependencies
- User authentication system (complete)
- File upload system (complete)
- Notification system (pending)
- License verification API (pending)
- Insurance verification service (pending)

## Security Considerations
- Secure document storage
- PII data encryption
- Document access controls
- Audit trail of changes
- Suspicious pattern detection

## Future Enhancements
- Background check integration
- Customer review system
- Crew member management
- Equipment tracking
- Automatic license renewal
- Partner/supplier network
- Financial verification