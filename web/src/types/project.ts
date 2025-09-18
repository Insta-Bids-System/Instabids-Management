export type ProjectCategory =
  | 'plumbing'
  | 'electrical'
  | 'hvac'
  | 'roofing'
  | 'painting'
  | 'landscaping'
  | 'carpentry'
  | 'general_maintenance'
  | 'other'

export type ProjectUrgency = 'emergency' | 'urgent' | 'routine' | 'scheduled'

export type BudgetRange =
  | 'under_500'
  | '500_1000'
  | '1000_5000'
  | '5000_10000'
  | 'over_10000'
  | 'open'

export interface PropertySummary {
  id: string
  name: string
  address: string
  city: string
  state: string
  zip: string
  access_notes?: string | null
}

export interface ProjectMediaItem {
  file: File
  caption: string
  isPrimary: boolean
}

export interface ProjectWizardValues {
  property_id: string
  title: string
  description: string
  category: ProjectCategory | ''
  urgency: ProjectUrgency
  bid_deadline: string
  preferred_start_date: string
  completion_deadline: string
  budget_min: string
  budget_max: string
  budget_range: BudgetRange | ''
  payment_terms: string
  requires_insurance: boolean
  requires_license: boolean
  minimum_bids: number
  is_open_bidding: boolean
  contractor_ids: string[]
  location_details: string
  special_conditions: string
  access_notes: {
    gate_code: string
    lockbox_code: string
    key_location: string
    onsite_contact_name: string
    onsite_contact_phone: string
    parking_instructions: string
    work_hours: string
    hazards: string
    pets_on_property: boolean
  }
  media: ProjectMediaItem[]
}

export interface ProjectReviewSection {
  title: string
  items: Array<{ label: string; value: string }>
}
