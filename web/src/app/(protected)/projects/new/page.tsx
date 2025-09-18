'use client'

import { useAuth } from '@/contexts/AuthContext'
import { createClient } from '@/lib/supabase'
import {
  BudgetRange,
  ProjectCategory,
  ProjectMediaItem,
  ProjectReviewSection,
  ProjectUrgency,
  ProjectWizardValues,
  PropertySummary
} from '@/types/project'
import { zodResolver } from '@hookform/resolvers/zod'
import clsx from 'clsx'
import { useRouter } from 'next/navigation'
import { Dispatch, SetStateAction, useEffect, useMemo, useState } from 'react'
import { Controller, FormProvider, useForm } from 'react-hook-form'
import { z } from 'zod'

type ProjectWizardFormValues = Omit<ProjectWizardValues, 'media'>

type StepDefinition = {
  id: string
  title: string
  description: string
}

const categoryOptions: { label: string; value: ProjectCategory }[] = [
  { label: 'Plumbing', value: 'plumbing' },
  { label: 'Electrical', value: 'electrical' },
  { label: 'HVAC', value: 'hvac' },
  { label: 'Roofing', value: 'roofing' },
  { label: 'Painting', value: 'painting' },
  { label: 'Landscaping', value: 'landscaping' },
  { label: 'Carpentry', value: 'carpentry' },
  { label: 'General Maintenance', value: 'general_maintenance' },
  { label: 'Other', value: 'other' }
]

const urgencyOptions: { label: string; value: ProjectUrgency; helper: string }[] = [
  { label: 'Emergency', value: 'emergency', helper: 'Response within 4 hours' },
  { label: 'Urgent', value: 'urgent', helper: 'Response within 24 hours' },
  { label: 'Routine', value: 'routine', helper: 'Response within 72 hours' },
  { label: 'Scheduled', value: 'scheduled', helper: 'Set a future date' }
]

const budgetRangeOptions: { label: string; value: BudgetRange }[] = [
  { label: 'Under $500', value: 'under_500' },
  { label: '$500 - $1,000', value: '500_1000' },
  { label: '$1,000 - $5,000', value: '1000_5000' },
  { label: '$5,000 - $10,000', value: '5000_10000' },
  { label: 'Over $10,000', value: 'over_10000' },
  { label: 'Open to quotes', value: 'open' }
]

const steps: StepDefinition[] = [
  {
    id: 'property',
    title: 'Select property',
    description: 'Choose the property that requires maintenance.'
  },
  {
    id: 'issue',
    title: 'Describe the issue',
    description: 'Provide details contractors need to understand the job.'
  },
  {
    id: 'timeline',
    title: 'Set urgency & timeline',
    description: 'Define deadlines and when the work should start.'
  },
  {
    id: 'media',
    title: 'Add photos & videos',
    description: 'Help contractors visualize the scope of work.'
  },
  {
    id: 'preferences',
    title: 'Set preferences & access',
    description: 'Share budget expectations and onsite instructions.'
  },
  {
    id: 'review',
    title: 'Review & publish',
    description: 'Double-check details before saving or publishing.'
  }
]

const accessNotesSchema = z.object({
  gate_code: z.string().max(50).optional().or(z.literal('')),
  lockbox_code: z.string().max(50).optional().or(z.literal('')),
  key_location: z.string().max(255).optional().or(z.literal('')),
  onsite_contact_name: z.string().max(255).optional().or(z.literal('')),
  onsite_contact_phone: z
    .string()
    .regex(/^$|^\+?1?\d{9,15}$/u, 'Use international format e.g. +1234567890'),
  parking_instructions: z.string().max(500).optional().or(z.literal('')),
  work_hours: z.string().max(255).optional().or(z.literal('')),
  hazards: z.string().max(500).optional().or(z.literal('')),
  pets_on_property: z.boolean()
})

const projectWizardSchema = z.object({
  property_id: z.string().uuid('Select a property before continuing'),
  title: z
    .string()
    .min(3, 'Title must be at least 3 characters')
    .max(100, 'Title must be 100 characters or fewer'),
  description: z
    .string()
    .min(30, 'Description must be at least 30 characters')
    .max(2000, 'Description must be 2000 characters or fewer'),
  category: z
    .enum([
      'plumbing',
      'electrical',
      'hvac',
      'roofing',
      'painting',
      'landscaping',
      'carpentry',
      'general_maintenance',
      'other'
    ], {
      errorMap: () => ({ message: 'Select a project category' })
    }),
  urgency: z.enum(['emergency', 'urgent', 'routine', 'scheduled']),
  bid_deadline: z
    .string()
    .min(1, 'Set a bid deadline')
    .refine((value) => {
      const deadline = new Date(value)
      const now = new Date()
      const max = new Date(now.getTime() + 7 * 24 * 60 * 60 * 1000)
      return deadline > now && deadline <= max
    }, 'Deadline must be within the next 7 days'),
  preferred_start_date: z.string().optional().or(z.literal('')),
  completion_deadline: z.string().optional().or(z.literal('')),
  budget_min: z.string().optional().or(z.literal('')),
  budget_max: z.string().optional().or(z.literal('')),
  budget_range: z
    .enum(['under_500', '500_1000', '1000_5000', '5000_10000', 'over_10000', 'open'])
    .optional()
    .or(z.literal('')),
  payment_terms: z.string().max(500).optional().or(z.literal('')),
  requires_insurance: z.boolean(),
  requires_license: z.boolean(),
  minimum_bids: z.number().min(1).max(20),
  is_open_bidding: z.boolean(),
  contractor_ids: z.array(z.string()),
  location_details: z.string().max(500).optional().or(z.literal('')),
  special_conditions: z.string().max(1000).optional().or(z.literal('')),
  access_notes: accessNotesSchema
}).superRefine((data, ctx) => {
  if (data.preferred_start_date) {
    const start = new Date(data.preferred_start_date)
    const today = new Date()
    today.setHours(0, 0, 0, 0)
    if (start < today) {
      ctx.addIssue({
        code: z.ZodIssueCode.custom,
        message: 'Start date cannot be in the past',
        path: ['preferred_start_date']
      })
    }
    if (data.bid_deadline) {
      const deadline = new Date(data.bid_deadline)
      if (deadline > start) {
        ctx.addIssue({
          code: z.ZodIssueCode.custom,
          message: 'Bid deadline must be on or before the start date',
          path: ['bid_deadline']
        })
      }
    }
  }
  if (data.completion_deadline && data.preferred_start_date) {
    const completion = new Date(data.completion_deadline)
    const start = new Date(data.preferred_start_date)
    if (completion <= start) {
      ctx.addIssue({
        code: z.ZodIssueCode.custom,
        message: 'Completion must be after the start date',
        path: ['completion_deadline']
      })
    }
  }
  if (data.budget_min && data.budget_max) {
    const min = Number(data.budget_min)
    const max = Number(data.budget_max)
    if (!Number.isNaN(min) && !Number.isNaN(max) && min > max) {
      ctx.addIssue({
        code: z.ZodIssueCode.custom,
        message: 'Minimum budget cannot exceed maximum budget',
        path: ['budget_min']
      })
    }
  }
})

const defaultValues: ProjectWizardFormValues = {
  property_id: '',
  title: '',
  description: '',
  category: '' as ProjectCategory,
  urgency: 'routine',
  bid_deadline: '',
  preferred_start_date: '',
  completion_deadline: '',
  budget_min: '',
  budget_max: '',
  budget_range: '' as BudgetRange,
  payment_terms: '',
  requires_insurance: true,
  requires_license: true,
  minimum_bids: 3,
  is_open_bidding: false,
  contractor_ids: [],
  location_details: '',
  special_conditions: '',
  access_notes: {
    gate_code: '',
    lockbox_code: '',
    key_location: '',
    onsite_contact_name: '',
    onsite_contact_phone: '',
    parking_instructions: '',
    work_hours: '',
    hazards: '',
    pets_on_property: false
  }
}

const stepFieldMap: Record<string, string[]> = {
  property: ['property_id'],
  issue: ['title', 'description', 'category'],
  timeline: ['urgency', 'bid_deadline', 'preferred_start_date', 'completion_deadline'],
  media: [],
  preferences: [
    'budget_min',
    'budget_max',
    'budget_range',
    'payment_terms',
    'requires_insurance',
    'requires_license',
    'minimum_bids',
    'is_open_bidding',
    'contractor_ids',
    'location_details',
    'special_conditions',
    'access_notes.gate_code',
    'access_notes.lockbox_code',
    'access_notes.key_location',
    'access_notes.onsite_contact_name',
    'access_notes.onsite_contact_phone',
    'access_notes.parking_instructions',
    'access_notes.work_hours',
    'access_notes.hazards',
    'access_notes.pets_on_property'
  ],
  review: []
}

function StepHeader({ stepIndex }: { stepIndex: number }) {
  return (
    <div className="flex items-center gap-4">
      <div className="flex items-center gap-2">
        {steps.map((step, index) => {
          const isActive = index === stepIndex
          const isCompleted = index < stepIndex
          return (
            <div key={step.id} className="flex items-center">
              <div
                className={clsx(
                  'flex h-10 w-10 items-center justify-center rounded-full border-2 text-sm font-semibold',
                  {
                    'border-blue-600 bg-blue-600 text-white': isActive,
                    'border-blue-600 bg-blue-50 text-blue-600': isCompleted,
                    'border-gray-300 text-gray-500': !isActive && !isCompleted
                  }
                )}
              >
                {index + 1}
              </div>
              {index < steps.length - 1 && (
                <div
                  className={clsx('mx-2 h-0.5 w-10 rounded', {
                    'bg-blue-600': isCompleted,
                    'bg-gray-200': !isCompleted
                  })}
                />
              )}
            </div>
          )
        })}
      </div>
      <div>
        <h1 className="text-2xl font-bold text-gray-900">{steps[stepIndex].title}</h1>
        <p className="text-sm text-gray-600">{steps[stepIndex].description}</p>
      </div>
    </div>
  )
}

function PropertiesSelect({
  properties,
  loading,
  error,
  selectedId,
  onChange,
  fieldError
}: {
  properties: PropertySummary[]
  loading: boolean
  error: string | null
  selectedId: string
  onChange: (value: string) => void
  fieldError: string | null
}) {
  return (
    <div className="space-y-4">
      <label className="block text-sm font-medium text-gray-700" htmlFor="property">
        Property
      </label>
      <select
        id="property"
        className="w-full rounded border border-gray-300 p-3 text-sm focus:border-blue-600 focus:outline-none"
        value={selectedId}
        onChange={(event) => onChange(event.target.value)}
      >
        <option value="">Select a property...</option>
        {properties.map((property) => (
          <option key={property.id} value={property.id}>
            {property.name} — {property.city}, {property.state}
          </option>
        ))}
      </select>
      {loading && <p className="text-sm text-gray-500">Loading properties...</p>}
      {error && <p className="text-sm text-red-600">{error}</p>}
      {fieldError && <p className="text-sm text-red-600">{fieldError}</p>}
    </div>
  )
}

function PropertyPreview({ property }: { property: PropertySummary | undefined }) {
  if (!property) {
    return null
  }

  return (
    <div className="rounded border border-gray-200 bg-gray-50 p-4 text-sm text-gray-700">
      <h2 className="font-semibold text-gray-900">{property.name}</h2>
      <p>
        {property.address}, {property.city}, {property.state} {property.zip}
      </p>
      {property.access_notes && (
        <p className="mt-2 text-gray-600">Access notes: {property.access_notes}</p>
      )}
    </div>
  )
}

function MediaManager({
  items,
  setItems
}: {
  items: ProjectMediaItem[]
  setItems: Dispatch<SetStateAction<ProjectMediaItem[]>>
}) {
  const [error, setError] = useState<string | null>(null)

  const photoCount = items.filter((item) => item.file.type.startsWith('image/')).length
  const videoCount = items.filter((item) => item.file.type.startsWith('video/')).length

  function updateItems(updater: (current: ProjectMediaItem[]) => ProjectMediaItem[]) {
    setItems((current) => updater(current))
  }

  function handleFilesChange(event: React.ChangeEvent<HTMLInputElement>) {
    const files = Array.from(event.target.files ?? [])
    if (!files.length) {
      return
    }

    const nextItems: ProjectMediaItem[] = [...items]
    let nextPhotoCount = photoCount
    let nextVideoCount = videoCount
    const warnings: string[] = []

    files.forEach((file) => {
      const isImage = file.type.startsWith('image/')
      const isVideo = file.type.startsWith('video/')

      if (!isImage && !isVideo) {
        warnings.push(`${file.name} is not a supported file type.`)
        return
      }

      if (isImage) {
        if (file.size > 10 * 1024 * 1024) {
          warnings.push(`${file.name} exceeds the 10MB limit for photos.`)
          return
        }
        if (nextPhotoCount >= 10) {
          warnings.push('Maximum of 10 photos allowed. Additional photos were skipped.')
          return
        }
        nextPhotoCount += 1
      }

      if (isVideo) {
        if (file.size > 100 * 1024 * 1024) {
          warnings.push(`${file.name} exceeds the 100MB limit for videos.`)
          return
        }
        if (nextVideoCount >= 3) {
          warnings.push('Maximum of 3 videos allowed. Additional videos were skipped.')
          return
        }
        nextVideoCount += 1
      }

      nextItems.push({ file, caption: '', isPrimary: false })
    })

    if (!nextItems.some((item) => item.isPrimary) && nextItems.length) {
      nextItems[0].isPrimary = true
    }

    setError(warnings.length ? warnings.join(' ') : null)
    setItems(nextItems)
    event.target.value = ''
  }

  function updateCaption(index: number, caption: string) {
    updateItems((current) =>
      current.map((item, idx) =>
        idx === index
          ? {
              ...item,
              caption
            }
          : item
      )
    )
  }

  function togglePrimary(index: number) {
    updateItems((current) =>
      current.map((item, idx) => ({ ...item, isPrimary: idx === index }))
    )
  }

  function removeItem(index: number) {
    updateItems((current) => {
      const next = current.filter((_, idx) => idx !== index)
      if (next.length && !next.some((item) => item.isPrimary)) {
        next[0].isPrimary = true
      }
      return next
    })
  }

  return (
    <div className="space-y-4">
      <div>
        <label className="block text-sm font-medium text-gray-700">Upload media</label>
        <input
          type="file"
          accept="image/*,video/*"
          multiple
          onChange={handleFilesChange}
          className="mt-2 w-full rounded border border-dashed border-gray-300 p-8 text-center text-sm text-gray-600"
        />
        <p className="mt-2 text-xs text-gray-500">
          Up to 10 photos (10MB each) and 3 videos (100MB each). First upload becomes the primary photo.
        </p>
        {error && <p className="mt-2 text-sm text-red-600">{error}</p>}
      </div>

      {items.length > 0 && (
        <div className="space-y-4">
          {items.map((item, index) => (
            <div key={`${item.file.name}-${index}`} className="flex flex-col gap-2 rounded border border-gray-200 p-4 sm:flex-row sm:items-center">
              <div className="flex-1">
                <p className="text-sm font-medium text-gray-900">{item.file.name}</p>
                <p className="text-xs text-gray-500">
                  {(item.file.size / (1024 * 1024)).toFixed(1)} MB · {item.file.type}
                </p>
                <label className="mt-2 block text-xs font-medium text-gray-600" htmlFor={`caption-${index}`}>
                  Caption
                </label>
                <input
                  id={`caption-${index}`}
                  className="mt-1 w-full rounded border border-gray-300 p-2 text-sm focus:border-blue-600 focus:outline-none"
                  placeholder="Optional description"
                  value={item.caption}
                  onChange={(event) => updateCaption(index, event.target.value)}
                />
              </div>
              <div className="flex flex-col gap-2 sm:items-end">
                <button
                  type="button"
                  onClick={() => togglePrimary(index)}
                  className={clsx(
                    'rounded px-3 py-2 text-sm font-medium',
                    item.isPrimary
                      ? 'bg-blue-600 text-white'
                      : 'border border-gray-300 text-gray-600 hover:bg-gray-100'
                  )}
                >
                  {item.isPrimary ? 'Primary media' : 'Make primary'}
                </button>
                <button
                  type="button"
                  onClick={() => removeItem(index)}
                  className="text-sm text-red-600 hover:underline"
                >
                  Remove
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

function ReviewPanel({ sections }: { sections: ProjectReviewSection[] }) {
  return (
    <div className="space-y-6">
      {sections.map((section) => (
        <div key={section.title} className="rounded border border-gray-200 p-4">
          <h3 className="text-sm font-semibold uppercase tracking-wide text-gray-500">
            {section.title}
          </h3>
          <dl className="mt-4 space-y-2 text-sm">
            {section.items.map((item) => (
              <div key={item.label} className="flex">
                <dt className="w-48 text-gray-500">{item.label}</dt>
                <dd className="flex-1 text-gray-900">{item.value || '—'}</dd>
              </div>
            ))}
          </dl>
        </div>
      ))}
    </div>
  )
}

function formatDate(value: string | undefined) {
  if (!value) return ''
  try {
    return new Date(value).toLocaleString()
  } catch (error) {
    return value
  }
}

export default function NewProjectPage() {
  const methods = useForm<ProjectWizardFormValues>({
    resolver: zodResolver(projectWizardSchema),
    defaultValues,
    mode: 'onBlur'
  })
  const { user } = useAuth()
  const router = useRouter()
  const [currentStep, setCurrentStep] = useState(0)
  const [properties, setProperties] = useState<PropertySummary[]>([])
  const [propertiesLoading, setPropertiesLoading] = useState(false)
  const [propertiesError, setPropertiesError] = useState<string | null>(null)
  const [mediaItems, setMediaItems] = useState<ProjectMediaItem[]>([])
  const [submitState, setSubmitState] = useState<'idle' | 'submitting' | 'success' | 'error'>('idle')
  const [submitError, setSubmitError] = useState<string | null>(null)

  const supabase = useMemo(() => createClient(), [])
  const apiUrl = process.env.NEXT_PUBLIC_API_URL
  const propertyId = methods.watch('property_id')

  useEffect(() => {
    if (!apiUrl) {
      setPropertiesError('API URL is not configured')
      return
    }

    async function loadProperties() {
      setPropertiesLoading(true)
      setPropertiesError(null)
      try {
        const session = await supabase.auth.getSession()
        const token = session.data.session?.access_token
        const response = await fetch(`${apiUrl}/api/properties?per_page=100`, {
          headers: token
            ? {
                Authorization: `Bearer ${token}`
              }
            : undefined,
          credentials: 'include'
        })

        if (!response.ok) {
          throw new Error('Unable to load properties')
        }

        const data = await response.json()
        setProperties(data.properties ?? [])
      } catch (error) {
        setPropertiesError(error instanceof Error ? error.message : 'Failed to load properties')
      } finally {
        setPropertiesLoading(false)
      }
    }

    void loadProperties()
  }, [apiUrl, supabase])

  const selectedProperty = useMemo(
    () => properties.find((property) => property.id === propertyId),
    [properties, propertyId]
  )

  const isLastStep = currentStep === steps.length - 1

  async function handleNextStep() {
    const stepId = steps[currentStep].id
    const fieldsToValidate = stepFieldMap[stepId]
    if (fieldsToValidate.length) {
      const isValid = await methods.trigger(fieldsToValidate as any)
      if (!isValid) {
        return
      }
    }
    setCurrentStep((prev) => Math.min(prev + 1, steps.length - 1))
  }

  function handlePrevStep() {
    setCurrentStep((prev) => Math.max(prev - 1, 0))
  }

  function buildPayload(values: ProjectWizardFormValues, publish: boolean) {
    const virtualAccessEntries = Object.entries(values.access_notes).filter(([key, value]) => {
      if (typeof value === 'boolean') {
        return value
      }
      return value !== undefined && value !== null && String(value).trim() !== ''
    })

    const virtualAccess = virtualAccessEntries.length
      ? Object.fromEntries(virtualAccessEntries)
      : undefined

    return {
      property_id: values.property_id,
      title: values.title,
      description: values.description,
      category: values.category,
      urgency: values.urgency,
      bid_deadline: new Date(values.bid_deadline).toISOString(),
      preferred_start_date: values.preferred_start_date || undefined,
      completion_deadline: values.completion_deadline || undefined,
      budget_min: values.budget_min ? Number(values.budget_min) : undefined,
      budget_max: values.budget_max ? Number(values.budget_max) : undefined,
      budget_range: values.budget_range || undefined,
      insurance_required: values.requires_insurance,
      license_required: values.requires_license,
      minimum_bids: values.minimum_bids,
      is_open_bidding: values.is_open_bidding,
      location_details: values.location_details || undefined,
      special_conditions: values.special_conditions || undefined,
      virtual_access: virtualAccess,
      publish,
      status: publish ? 'open_for_bids' : 'draft'
    }
  }

  const onSubmit = async (values: ProjectWizardFormValues, publish: boolean) => {
    if (!apiUrl) {
      setSubmitError('API URL is not configured')
      setSubmitState('error')
      return
    }

    setSubmitState('submitting')
    setSubmitError(null)

    try {
      const session = await supabase.auth.getSession()
      const token = session.data.session?.access_token
      const payload = buildPayload(values, publish)
      const response = await fetch(`${apiUrl}/api/projects`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(token ? { Authorization: `Bearer ${token}` } : {})
        },
        body: JSON.stringify(payload)
      })

      if (!response.ok) {
        const errorBody = await response.json().catch(() => null)
        throw new Error(errorBody?.detail ?? 'Failed to save project')
      }

      setSubmitState('success')

      if (publish) {
        router.push('/projects')
      } else {
        router.refresh()
      }
    } catch (error) {
      setSubmitState('error')
      setSubmitError(error instanceof Error ? error.message : 'Something went wrong')
    }
  }

  function renderStep(stepId: string) {
    switch (stepId) {
      case 'property':
        return (
          <div className="space-y-6">
            <PropertiesSelect
              properties={properties}
              loading={propertiesLoading}
              error={propertiesError}
              selectedId={methods.watch('property_id')}
              onChange={(value) => methods.setValue('property_id', value, { shouldValidate: true })}
              fieldError={methods.formState.errors.property_id?.message ?? null}
            />
            <PropertyPreview property={selectedProperty} />
          </div>
        )
      case 'issue':
        return (
          <div className="space-y-6">
            <div>
              <label className="block text-sm font-medium text-gray-700" htmlFor="title">
                Title
              </label>
              <input
                id="title"
                className="mt-2 w-full rounded border border-gray-300 p-3 text-sm focus:border-blue-600 focus:outline-none"
                placeholder="Describe the job in a sentence"
                {...methods.register('title')}
              />
              {methods.formState.errors.title && (
                <p className="mt-1 text-sm text-red-600">{methods.formState.errors.title.message}</p>
              )}
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700" htmlFor="description">
                Detailed description
              </label>
              <textarea
                id="description"
                rows={6}
                className="mt-2 w-full rounded border border-gray-300 p-3 text-sm focus:border-blue-600 focus:outline-none"
                placeholder="Explain the issue, location within the property, and any helpful context"
                {...methods.register('description')}
              />
              {methods.formState.errors.description && (
                <p className="mt-1 text-sm text-red-600">{methods.formState.errors.description.message}</p>
              )}
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">Category</label>
              <div className="mt-2 grid gap-3 sm:grid-cols-2">
                {categoryOptions.map((option) => {
                  const selected = methods.watch('category') === option.value
                  return (
                    <button
                      key={option.value}
                      type="button"
                      onClick={() => methods.setValue('category', option.value, { shouldValidate: true })}
                      className={clsx(
                        'rounded border p-3 text-left text-sm transition hover:border-blue-600',
                        selected ? 'border-blue-600 bg-blue-50 text-blue-700' : 'border-gray-200 text-gray-700'
                      )}
                    >
                      {option.label}
                    </button>
                  )
                })}
              </div>
              {methods.formState.errors.category && (
                <p className="mt-1 text-sm text-red-600">{methods.formState.errors.category.message}</p>
              )}
            </div>
          </div>
        )
      case 'timeline':
        return (
          <div className="space-y-6">
            <div>
              <label className="block text-sm font-medium text-gray-700">Urgency</label>
              <div className="mt-3 grid gap-3 md:grid-cols-2">
                {urgencyOptions.map((option) => {
                  const selected = methods.watch('urgency') === option.value
                  return (
                    <button
                      key={option.value}
                      type="button"
                      onClick={() => methods.setValue('urgency', option.value, { shouldValidate: true })}
                      className={clsx(
                        'rounded border p-3 text-left text-sm transition hover:border-blue-600',
                        selected ? 'border-blue-600 bg-blue-50 text-blue-700' : 'border-gray-200 text-gray-700'
                      )}
                    >
                      <span className="font-medium">{option.label}</span>
                      <span className="block text-xs text-gray-500">{option.helper}</span>
                    </button>
                  )
                })}
              </div>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700" htmlFor="bid_deadline">
                Bid deadline
              </label>
              <input
                id="bid_deadline"
                type="datetime-local"
                className="mt-2 w-full rounded border border-gray-300 p-3 text-sm focus:border-blue-600 focus:outline-none"
                {...methods.register('bid_deadline')}
              />
              {methods.formState.errors.bid_deadline && (
                <p className="mt-1 text-sm text-red-600">{methods.formState.errors.bid_deadline.message}</p>
              )}
            </div>
            <div className="grid gap-4 sm:grid-cols-2">
              <div>
                <label className="block text-sm font-medium text-gray-700" htmlFor="preferred_start_date">
                  Preferred start date
                </label>
                <input
                  id="preferred_start_date"
                  type="date"
                  className="mt-2 w-full rounded border border-gray-300 p-3 text-sm focus:border-blue-600 focus:outline-none"
                  {...methods.register('preferred_start_date')}
                />
                {methods.formState.errors.preferred_start_date && (
                  <p className="mt-1 text-sm text-red-600">
                    {methods.formState.errors.preferred_start_date.message}
                  </p>
                )}
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700" htmlFor="completion_deadline">
                  Completion deadline (optional)
                </label>
                <input
                  id="completion_deadline"
                  type="date"
                  className="mt-2 w-full rounded border border-gray-300 p-3 text-sm focus:border-blue-600 focus:outline-none"
                  {...methods.register('completion_deadline')}
                />
                {methods.formState.errors.completion_deadline && (
                  <p className="mt-1 text-sm text-red-600">
                    {methods.formState.errors.completion_deadline.message}
                  </p>
                )}
              </div>
            </div>
          </div>
        )
      case 'media':
        return <MediaManager items={mediaItems} setItems={setMediaItems} />
      case 'preferences':
        return (
          <div className="space-y-6">
            <div className="grid gap-4 md:grid-cols-2">
              <div>
                <label className="block text-sm font-medium text-gray-700" htmlFor="budget_min">
                  Minimum budget
                </label>
                <input
                  id="budget_min"
                  type="number"
                  min={0}
                  className="mt-2 w-full rounded border border-gray-300 p-3 text-sm focus:border-blue-600 focus:outline-none"
                  {...methods.register('budget_min')}
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700" htmlFor="budget_max">
                  Maximum budget
                </label>
                <input
                  id="budget_max"
                  type="number"
                  min={0}
                  className="mt-2 w-full rounded border border-gray-300 p-3 text-sm focus:border-blue-600 focus:outline-none"
                  {...methods.register('budget_max')}
                />
              </div>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">Budget range</label>
              <div className="mt-2 grid gap-3 sm:grid-cols-2">
                {budgetRangeOptions.map((option) => {
                  const selected = methods.watch('budget_range') === option.value
                  return (
                    <button
                      key={option.value}
                      type="button"
                      onClick={() => methods.setValue('budget_range', option.value, { shouldValidate: true })}
                      className={clsx(
                        'rounded border p-3 text-left text-sm transition hover:border-blue-600',
                        selected ? 'border-blue-600 bg-blue-50 text-blue-700' : 'border-gray-200 text-gray-700'
                      )}
                    >
                      {option.label}
                    </button>
                  )
                })}
              </div>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700" htmlFor="payment_terms">
                Payment terms (optional)
              </label>
              <textarea
                id="payment_terms"
                rows={3}
                className="mt-2 w-full rounded border border-gray-300 p-3 text-sm focus:border-blue-600 focus:outline-none"
                placeholder="E.g. Net 30, deposit required"
                {...methods.register('payment_terms')}
              />
            </div>
            <div className="grid gap-4 sm:grid-cols-2">
              <label className="flex items-center gap-2 text-sm font-medium text-gray-700">
                <input type="checkbox" {...methods.register('requires_insurance', { valueAsBoolean: true })} />
                Require insurance proof
              </label>
              <label className="flex items-center gap-2 text-sm font-medium text-gray-700">
                <input type="checkbox" {...methods.register('requires_license', { valueAsBoolean: true })} />
                Require license verification
              </label>
            </div>
            <div className="grid gap-4 sm:grid-cols-2">
              <div>
                <label className="block text-sm font-medium text-gray-700" htmlFor="minimum_bids">
                  Minimum bids required
                </label>
                <input
                  id="minimum_bids"
                  type="number"
                  min={1}
                  max={20}
                  className="mt-2 w-full rounded border border-gray-300 p-3 text-sm focus:border-blue-600 focus:outline-none"
                  {...methods.register('minimum_bids', { valueAsNumber: true })}
                />
              </div>
              <label className="mt-6 flex items-center gap-2 text-sm font-medium text-gray-700">
                <input type="checkbox" {...methods.register('is_open_bidding', { valueAsBoolean: true })} />
                Open bidding to all contractors
              </label>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700" htmlFor="contractor_ids">
                Invite specific contractors (IDs, comma separated)
              </label>
              <Controller
                name="contractor_ids"
                control={methods.control}
                render={({ field }) => (
                  <input
                    id="contractor_ids"
                    className="mt-2 w-full rounded border border-gray-300 p-3 text-sm focus:border-blue-600 focus:outline-none"
                    placeholder="abc-123, def-456"
                    value={field.value.join(', ')}
                    onChange={(event) => {
                      const values = event.target.value
                        .split(',')
                        .map((item) => item.trim())
                        .filter(Boolean)
                      field.onChange(values)
                    }}
                  />
                )}
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700" htmlFor="location_details">
                Location within property
              </label>
              <input
                id="location_details"
                className="mt-2 w-full rounded border border-gray-300 p-3 text-sm focus:border-blue-600 focus:outline-none"
                placeholder="E.g. Building B, unit 304, mechanical room"
                {...methods.register('location_details')}
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700" htmlFor="special_conditions">
                Special conditions (optional)
              </label>
              <textarea
                id="special_conditions"
                rows={3}
                className="mt-2 w-full rounded border border-gray-300 p-3 text-sm focus:border-blue-600 focus:outline-none"
                placeholder="Pets on site, alarm codes, hazardous materials, etc."
                {...methods.register('special_conditions')}
              />
            </div>
            <div className="grid gap-4 md:grid-cols-2">
              <div>
                <label className="block text-sm font-medium text-gray-700" htmlFor="gate_code">
                  Gate code
                </label>
                <input
                  id="gate_code"
                  className="mt-2 w-full rounded border border-gray-300 p-3 text-sm focus:border-blue-600 focus:outline-none"
                  {...methods.register('access_notes.gate_code')}
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700" htmlFor="lockbox_code">
                  Lockbox code
                </label>
                <input
                  id="lockbox_code"
                  className="mt-2 w-full rounded border border-gray-300 p-3 text-sm focus:border-blue-600 focus:outline-none"
                  {...methods.register('access_notes.lockbox_code')}
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700" htmlFor="key_location">
                  Key location
                </label>
                <input
                  id="key_location"
                  className="mt-2 w-full rounded border border-gray-300 p-3 text-sm focus:border-blue-600 focus:outline-none"
                  {...methods.register('access_notes.key_location')}
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700" htmlFor="onsite_contact_name">
                  Onsite contact name
                </label>
                <input
                  id="onsite_contact_name"
                  className="mt-2 w-full rounded border border-gray-300 p-3 text-sm focus:border-blue-600 focus:outline-none"
                  {...methods.register('access_notes.onsite_contact_name')}
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700" htmlFor="onsite_contact_phone">
                  Onsite contact phone
                </label>
                <input
                  id="onsite_contact_phone"
                  className="mt-2 w-full rounded border border-gray-300 p-3 text-sm focus:border-blue-600 focus:outline-none"
                  {...methods.register('access_notes.onsite_contact_phone')}
                />
                {methods.formState.errors.access_notes?.onsite_contact_phone && (
                  <p className="mt-1 text-sm text-red-600">
                    {methods.formState.errors.access_notes.onsite_contact_phone.message}
                  </p>
                )}
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700" htmlFor="parking_instructions">
                  Parking instructions
                </label>
                <input
                  id="parking_instructions"
                  className="mt-2 w-full rounded border border-gray-300 p-3 text-sm focus:border-blue-600 focus:outline-none"
                  {...methods.register('access_notes.parking_instructions')}
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700" htmlFor="work_hours">
                  Work hour restrictions
                </label>
                <input
                  id="work_hours"
                  className="mt-2 w-full rounded border border-gray-300 p-3 text-sm focus:border-blue-600 focus:outline-none"
                  {...methods.register('access_notes.work_hours')}
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700" htmlFor="hazards">
                  Hazards to note
                </label>
                <input
                  id="hazards"
                  className="mt-2 w-full rounded border border-gray-300 p-3 text-sm focus:border-blue-600 focus:outline-none"
                  {...methods.register('access_notes.hazards')}
                />
              </div>
              <label className="flex items-center gap-2 text-sm font-medium text-gray-700">
                <input
                  type="checkbox"
                  {...methods.register('access_notes.pets_on_property', { valueAsBoolean: true })}
                />
                Pets on property
              </label>
            </div>
          </div>
        )
      case 'review': {
        const values = methods.getValues()
        const reviewSections: ProjectReviewSection[] = [
          {
            title: 'Project details',
            items: [
              { label: 'Property', value: selectedProperty?.name ?? '' },
              { label: 'Title', value: values.title },
              { label: 'Description', value: values.description },
              { label: 'Category', value: values.category },
              { label: 'Urgency', value: values.urgency }
            ]
          },
          {
            title: 'Timeline',
            items: [
              { label: 'Bid deadline', value: formatDate(values.bid_deadline) },
              { label: 'Preferred start', value: values.preferred_start_date },
              { label: 'Completion deadline', value: values.completion_deadline }
            ]
          },
          {
            title: 'Budget & requirements',
            items: [
              { label: 'Budget min', value: values.budget_min ? `$${values.budget_min}` : '' },
              { label: 'Budget max', value: values.budget_max ? `$${values.budget_max}` : '' },
              { label: 'Budget range', value: values.budget_range ?? '' },
              { label: 'Payment terms', value: values.payment_terms },
              { label: 'Insurance required', value: values.requires_insurance ? 'Yes' : 'No' },
              { label: 'License required', value: values.requires_license ? 'Yes' : 'No' },
              { label: 'Minimum bids', value: String(values.minimum_bids) },
              { label: 'Open bidding', value: values.is_open_bidding ? 'Yes' : 'No' }
            ]
          },
          {
            title: 'Access instructions',
            items: [
              { label: 'Location details', value: values.location_details },
              { label: 'Special conditions', value: values.special_conditions },
              { label: 'Gate code', value: values.access_notes.gate_code },
              { label: 'Lockbox code', value: values.access_notes.lockbox_code },
              { label: 'Key location', value: values.access_notes.key_location },
              { label: 'Onsite contact', value: values.access_notes.onsite_contact_name },
              { label: 'Contact phone', value: values.access_notes.onsite_contact_phone },
              { label: 'Parking', value: values.access_notes.parking_instructions },
              { label: 'Work hours', value: values.access_notes.work_hours },
              { label: 'Hazards', value: values.access_notes.hazards },
              { label: 'Pets on property', value: values.access_notes.pets_on_property ? 'Yes' : 'No' }
            ]
          }
        ]

        return (
          <div className="space-y-6">
            <ReviewPanel sections={reviewSections} />
            {mediaItems.length > 0 && (
              <div className="rounded border border-gray-200 p-4">
                <h3 className="text-sm font-semibold uppercase tracking-wide text-gray-500">Media</h3>
                <ul className="mt-4 space-y-2 text-sm">
                  {mediaItems.map((item, index) => (
                    <li key={`${item.file.name}-${index}`} className="flex items-center justify-between">
                      <span>
                        {item.file.name} ({item.file.type})
                        {item.isPrimary && <span className="ml-2 rounded bg-blue-100 px-2 py-1 text-xs text-blue-700">Primary</span>}
                      </span>
                      {item.caption && <span className="text-gray-500">Caption: {item.caption}</span>}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        )
      }
      default:
        return null
    }
  }

  return (
    <FormProvider {...methods}>
      <div className="mx-auto max-w-5xl space-y-10 py-10">
        <StepHeader stepIndex={currentStep} />
        <div className="rounded border border-gray-200 bg-white p-6 shadow-sm">
          {renderStep(steps[currentStep].id)}
        </div>
        <div className="flex flex-col-reverse gap-3 sm:flex-row sm:items-center sm:justify-between">
          <div>
            {submitState === 'error' && submitError && (
              <p className="text-sm text-red-600">{submitError}</p>
            )}
            {submitState === 'success' && (
              <p className="text-sm text-green-600">Project saved successfully.</p>
            )}
          </div>
          <div className="flex gap-3">
            {currentStep > 0 && (
              <button
                type="button"
                className="rounded border border-gray-300 px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50"
                onClick={handlePrevStep}
              >
                Back
              </button>
            )}
            {!isLastStep && (
              <button
                type="button"
                className="rounded bg-blue-600 px-4 py-2 text-sm font-semibold text-white hover:bg-blue-700"
                onClick={() => void handleNextStep()}
              >
                Next
              </button>
            )}
            {isLastStep && (
              <>
                <button
                  type="button"
                  className="rounded border border-gray-300 px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50"
                  disabled={submitState === 'submitting'}
                  onClick={() =>
                    methods.handleSubmit(async (data) => {
                      await onSubmit(data, false)
                    })()
                  }
                >
                  Save draft
                </button>
                <button
                  type="button"
                  className="rounded bg-blue-600 px-4 py-2 text-sm font-semibold text-white hover:bg-blue-700"
                  disabled={submitState === 'submitting'}
                  onClick={() =>
                    methods.handleSubmit(async (data) => {
                      await onSubmit(data, true)
                    })()
                  }
                >
                  {submitState === 'submitting' ? 'Publishing...' : 'Publish project'}
                </button>
              </>
            )}
          </div>
        </div>
      </div>
    </FormProvider>
  )
}
