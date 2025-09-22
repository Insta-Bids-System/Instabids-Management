# Supabase Infrastructure Bootstrap Guide

This guide provisions the storage buckets, Edge Functions, and webhook endpoints required by the quote submission, project creation, and SmartScope workflows. It couples one-click automation for the storage layer with explicit Supabase CLI playbooks for the compute/webhook pieces so that the infrastructure can be recreated consistently across environments.

## Prerequisites

1. Install the [Supabase CLI](https://supabase.com/docs/guides/cli) `>= 1.204.4`.
2. Authenticate with the Instabids project owner account:
   ```bash
   supabase login --token "$SUPABASE_ACCESS_TOKEN"
   supabase link --project-ref "$SUPABASE_PROJECT_REF"
   ```
3. Export the environment variables expected by the automation script:
   ```bash
   export SUPABASE_URL="https://lmbpvkfcfhdfaihigfdu.supabase.co"
   export SUPABASE_SERVICE_ROLE_KEY="<service_role_key>"
   export SUPABASE_ACCESS_TOKEN="<personal_access_token>"
   export SUPABASE_PROJECT_REF="lmbpvkfcfhdfaihigfdu"
   ```

The service-role key is required only when applying changes; a dry-run can be executed without it.

## Step 1 – Provision Storage Buckets Automatically

Run the bootstrap helper to create and tag all storage buckets used throughout the marketplace:

```bash
python scripts/bootstrap_supabase_infra.py --apply storage
```

Buckets created:

| Bucket | Visibility | Purpose |
| ------ | ---------- | ------- |
| `project-media` | private | Raw project photos and SmartScope captures. |
| `quote-intake` | private | Original PDFs, emails, and photo uploads for quotes. |
| `quote-standardized` | private | JSON exports from the AI standardization pipeline. |
| `contractor-artifacts` | private | Compliance documents uploaded during contractor onboarding. |

The script is idempotent; reruns will skip buckets that already exist. Validate bucket creation in the Supabase dashboard or with `supabase storage list-buckets`.

### Optional Dry Run

To review the operations without modifying Supabase, append `--dry-run`:

```bash
python scripts/bootstrap_supabase_infra.py --dry-run storage
```

## Step 2 – Deploy Edge Functions

Create the `supabase/functions` directory (already tracked in the repository once the functions are authored) and scaffold the two core functions:

```bash
supabase functions new quote-email-intake
supabase functions new quote-webhook-relay
```

1. **`quote-email-intake`** handles SendGrid/SES inbound parse payloads, validates attachments, and writes the raw payload into the `quote-intake` bucket before enqueueing standardization jobs.
2. **`quote-webhook-relay`** forwards status changes from background processors (OCR/AI) to the Next.js app via realtime channels.

After editing the generated `index.ts`, deploy and manage secrets:

```bash
supabase secrets set SENDGRID_SIGNING_SECRET=<secret> QUEUE_URL=<redis_url>
supabase functions deploy quote-email-intake
supabase functions deploy quote-webhook-relay
```

Confirm successful deployment:

```bash
supabase functions list
supabase functions logs quote-email-intake --tail
```

## Step 3 – Register Webhook Endpoints

The inbound email provider (SendGrid Inbound Parse or AWS SES) and background job processor require publicly reachable HTTPS endpoints. Supabase Edge Functions expose these automatically once deployed. Map them as follows:

1. **Inbound Email:** Point `https://bid.instabids.com/email/quotes` (or the auto-generated Supabase Edge URL) to the Inbound Parse configuration.
2. **Background Processor Callbacks:** Configure your queue worker to POST job results to the `quote-webhook-relay` function URL (displayed after deployment).
3. **SmartScope Notifications (future):** Reuse the `quote-webhook-relay` endpoint or create a sibling function once SmartScope real-time hooks are implemented.

Validate delivery with curl:

```bash
curl -X POST "https://<project-ref>.functions.supabase.co/quote-webhook-relay" \
  -H 'Content-Type: application/json' \
  -d '{"event":"healthcheck"}'
```

A `200 OK` response confirms routing. Review function logs via `supabase functions logs` for the request.

## Step 4 – Document Secrets in the Monorepo

1. Add non-sensitive placeholders to `.env.example` (already done for service keys).
2. Update deployment runbooks with the secret names required by each function.
3. Store actual secrets in the platform secret manager (e.g., Vercel, AWS Parameter Store, Doppler) rather than committing them.

## Verification Checklist

- [ ] Buckets appear under **Storage → Buckets** in the Supabase dashboard.
- [ ] `supabase functions list` shows both Edge Functions with status `ACTIVE`.
- [ ] Email provider test hits the `quote-email-intake` function and stores a payload in `quote-intake/`.
- [ ] Background processor POST to `quote-webhook-relay` returns `200`.
- [ ] Secrets referenced in functions exist in the target environment.

Once all items are checked, mark Task 2 in `tasks.md` as complete.
