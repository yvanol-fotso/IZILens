# IZI LENS — Front-end contract

> **Generated** by `npm run contract` from `src/lib/config/*.ts`. The dashboard is complete and already built against this contract:
> implement these endpoints and every screen fills in. Until an endpoint exists (HTTP 404/501) the screen shows a “module not connected yet” notice, never a crash.
> Paths are relative to `BACKEND_API_PREFIX` (default `/api/v1`).

## 1. Conventions

| Topic | Rule |
|---|---|
| Auth | `Authorization: Bearer <access JWT>`. The browser never sees tokens (httpOnly cookies in the SvelteKit server). |
| Environment | Client calls send `X-IZI-Environment: sandbox\|production`. Sandbox operations are **never billed**. Keys, data and webhooks of both environments are separated. |
| Errors | JSON `{detail: string \| [{msg}]}`. 401 → re-login · 403 → forbidden · 404/501 → “module not connected” · 409 → conflict (e.g. case already decided) · 422 → validation. |
| Pagination | `page` (1-based) + `page_size`. Respond with `{items, total}` (preferred) or a plain array. |
| Sensitive actions | Body field `reason` (stored in the audit log with actor, IP, request id, result). **Critical** actions also require header `X-Step-Up-Code` = current TOTP code → 403 if wrong. |
| Multipart | When a form has files: `payload` = JSON string of all non-file fields; each file is a part named by its field path (repeaters: `documents[1][file]`). |
| Secrets | API keys and provider secrets are returned in clear **once** (creation) and never again. Config GET returns `<name>_set: true` instead of a secret. |
| Dates | ISO 8601 UTC. Money: numbers in the major unit of `currency` (ISO 4217: CAD, USD, EUR, XOF, XAF, GBP — **XOF and XAF are distinct**). |
| Backend is the authority | Permissions below are enforced in the UI only for convenience; enforce them server-side. |

## 2. Roles & permissions

Staff roles (space `/admin`, MFA **mandatory**) and client roles (space `/app`). Clients have **no administrator role**: they submit, consult, pay, leave. All manual-review decisions belong to Kafintech staff. Legacy roles are mapped: `admin`,`reviewer`→`client`, `viewer`→`client_readonly`.

| Role | Permissions (default matrix; editable via `PUT /admin/roles/{role}`) |
|---|---|
| `super_admin` | `adm:dashboard` `adm:clients` `adm:kyc` `adm:kyb` `adm:biometrics` `adm:monitoring` `adm:risk` `adm:aml` `adm:fraud` `adm:billing` `adm:api` `adm:reports` `adm:notifications` `adm:audit` `adm:platform` `adm:clients:write` `adm:kyc:review` `adm:kyb:review` `adm:risk:write` `adm:aml:review` `adm:billing:write` `adm:pricing:write` `adm:api:write` `adm:providers` `adm:infra` `adm:security` `adm:security:write` `adm:staff` `adm:roles` `adm:settings` `adm:content` `adm:requests` `adm:support` |
| `platform_admin` | `adm:dashboard` `adm:platform` `adm:clients` `adm:clients:write` `adm:kyc` `adm:kyb` `adm:biometrics` `adm:monitoring` `adm:api` `adm:api:write` `adm:reports` `adm:notifications` `adm:settings` `adm:content` `adm:requests` `adm:support` `adm:audit` |
| `compliance_officer` | `adm:dashboard` `adm:clients` `adm:kyc` `adm:kyc:review` `adm:kyb` `adm:kyb:review` `adm:aml` `adm:aml:review` `adm:fraud` `adm:risk` `adm:reports` `adm:audit` `adm:notifications` |
| `kyc_analyst` | `adm:dashboard` `adm:kyc` `adm:kyc:review` `adm:kyb` `adm:kyb:review` `adm:biometrics` `adm:monitoring` `adm:fraud` `adm:notifications` |
| `risk_officer` | `adm:dashboard` `adm:kyc` `adm:risk` `adm:risk:write` `adm:fraud` `adm:aml` `adm:monitoring` `adm:reports` `adm:notifications` |
| `finance_manager` | `adm:dashboard` `adm:clients` `adm:billing` `adm:billing:write` `adm:pricing:write` `adm:reports` `adm:notifications` |
| `support_agent` | `adm:dashboard` `adm:clients` `adm:monitoring` `adm:requests` `adm:support` `adm:notifications` |
| `tech_admin` | `adm:dashboard` `adm:monitoring` `adm:api` `adm:api:write` `adm:providers` `adm:infra` `adm:security` `adm:audit` `adm:notifications` |
| `read_only` | `adm:dashboard` `adm:clients` `adm:kyc` `adm:kyb` `adm:biometrics` `adm:monitoring` `adm:risk` `adm:aml` `adm:fraud` `adm:billing` `adm:api` `adm:reports` `adm:notifications` `adm:audit` |
| `client` | `cases:read` `cases:create` `kyb:read` `kyb:create` `biometrics:use` `monitoring:read` `billing:read` `developers:manage` `support:use` |
| `client_readonly` | `cases:read` `kyb:read` `monitoring:read` `billing:read` |
| `integration` | `cases:read` `cases:create` `kyb:read` `kyb:create` `biometrics:use` `monitoring:read` |

`GET /auth/me` must return: `id, email, full_name, role, organization_id, is_active, mfa_enabled, last_login_at` (+ `organization` for clients: `id, name, slug, enabled_modules (list of kyc, kyb, biometrics, monitoring, api), plan, currency, country, production_enabled`).

## 3. Authentication endpoints

| Route | Body → Response |
|---|---|
| `POST /auth/login` | `{email,password}` (or form `username,password`) → `{access_token,refresh_token}` **or** `{mfa_required:true, mfa_token}` (short-lived) |
| `POST /auth/mfa/verify` | `{mfa_token, code}` (TOTP or recovery code) → tokens |
| `POST /auth/refresh`, `POST /auth/logout`, `POST /auth/register`, `POST /auth/change-password` | see README |
| `POST /auth/oauth/google` | `{id_token, nonce}` → tokens or MFA challenge |
| `POST /auth/mfa/totp/setup` | → `{secret, otpauth_uri}` |
| `POST /auth/mfa/totp/confirm` | `{code}` → `{recovery_codes[]}` (shown once) |
| `POST /auth/mfa/disable` | `{code}` (refused for staff) |
| `POST /auth/passkeys/options` | → WebAuthn creation options (JSON, base64url `challenge`, `user.id`, `excludeCredentials[].id`) |
| `POST /auth/passkeys/verify` | `{id,rawId,type,response:{clientDataJSON,attestationObject}}` (base64url) → passkey |
| `GET /auth/passkeys`, `DELETE /auth/passkeys/{id}` | list / remove |
| `GET /auth/sessions`, `DELETE /auth/sessions/{id}` | `[{id,device,ip_address,last_seen_at,current}]` |

## 4. Resources (generic list / detail / create / actions)

### `clients` — Kafintech · exportable
- **List**: `GET /admin/clients` — permission `adm:clients`. Query: `page`, `page_size`, `search`, `status` (active|suspended|pending_validation), `plan` (starter|business|enterprise), `country`. Response: array **or** `{items,total}`.
- **Row fields** (columns): `name`, `country`, `sector`:badge, `plan`:badge, `services`:list, `verification_count`:number, `status`:status, `created_at`:date. id is required on every row.
- **Detail**: `GET /admin/clients/{id}`. Fields shown: `id`, `name`, `country`, `sector`, `created_at`, `status`, `representative_name`, `email`, `phone`, `plan`, `currency`, `services`, `verification_count`, `production_enabled`.
  - **Related** `consumption`: `GET /admin/clients/{id}/consumption` → rows with `service`:badge, `period`, `quantity`:number, `amount`:money
  - **Related** `invoices`: `GET /admin/clients/{id}/invoices` → rows with `number`:mono, `period`, `total`:money, `status`:status
  - **Related** `users`: `GET /admin/clients/{id}/users` → rows with `full_name`, `email`, `role`:badge, `last_login_at`:datetime
  - **Related** `notes`: `GET /admin/clients/{id}/notes` → rows with `created_at`:datetime, `author`, `note`
  - **Related** `activity`: `GET /admin/clients/{id}/activity` → rows with `created_at`:datetime, `action`:mono, `actor`
- **Create**: `POST /admin/clients` — permission `adm:clients:write` — JSON. Returns the created object (id).
  - `name` — text, **required**

  - `country` — text, **required** · ISO 3166-1 alpha-2

  - `sector` — select · one of: `banks`, `fintech`, `micro`, `insurance`, `telecom`, `ecommerce`, `platforms`, `other`

  - `representative_name` — text, **required**

  - `email` — email, **required**

  - `phone` — text

  - `plan` — select, **required** · one of: `starter`, `business`, `enterprise`

  - `currency` — select, **required** · one of: `CAD`, `USD`, `EUR`, `XOF`, `XAF`, `GBP`

  - `services` — multiselect · one of: `kyc`, `kyb`, `biometrics`, `monitoring`

- **Edit**: `PATCH /admin/clients/{id}` (same fields, all optional; secrets left empty are unchanged).
- **Action `suspend`**: `POST /admin/clients/{id}/suspend` — permission `adm:clients:write` · body includes reason (**required**, store in audit) · **critical**: header X-Step-Up-Code (TOTP) must be validated · shown when `status` ∈ active (enforce the same rule server-side)
- **Action `activate`**: `POST /admin/clients/{id}/activate` — permission `adm:clients:write` · body includes reason (**required**, store in audit) · shown when `status` ∈ suspended|pending_validation (enforce the same rule server-side)
- **Action `verify_documents`**: `POST /admin/clients/{id}/verify-documents` — permission `adm:clients:write` · body includes reason (**required**, store in audit)
  - `result` — select, **required** · one of: `approved`, `rejected`, `more_info`

- **Action `change_plan`**: `POST /admin/clients/{id}/plan` — permission `adm:billing:write` · body includes reason (**required**, store in audit)
  - `plan` — select, **required** · one of: `starter`, `business`, `enterprise`

  - `effective_from` — date

- **Action `add_note`**: `POST /admin/clients/{id}/notes` — permission `adm:clients:write`
  - `note` — textarea, **required**

- **Export**: `GET /admin/clients/export?format=csv|xlsx|pdf` + the same filters as the list. Binary response with `Content-Disposition`.

### `kyc` — Kafintech · exportable
- **List**: `GET /admin/kyc/cases` — permission `adm:kyc`. Query: `page`, `page_size`, `search`, `status` (pending|processing|approved|rejected|manual_review|failed|expired), `country`, `client_id`, `created_from`, `created_to`. Response: array **or** `{items,total}`.
- **Row fields** (columns): `reference`:mono, `client_name`, `country`, `document_type`:badge, `ocr_confidence`:percent, `document_result`:badge, `biometric_result`:badge, `risk_score`:number, `status`:status, `created_at`:datetime. id is required on every row.
- **Export**: `GET /admin/kyc/cases/export?format=csv|xlsx|pdf` + the same filters as the list. Binary response with `Content-Disposition`.

### `kyb` — Kafintech · exportable
- **List**: `GET /admin/kyb/cases` — permission `adm:kyb`. Query: `page`, `page_size`, `search`, `status` (pending|processing|approved|rejected|manual_review|failed|expired), `country`, `created_from`, `created_to`. Response: array **or** `{items,total}`.
- **Row fields** (columns): `legal_name`, `country`, `registration_number`:mono, `client_name`, `status`:status, `created_at`:datetime. id is required on every row.
- **Detail**: `GET /admin/kyb/cases/{id}`. Fields shown: `legal_name`, `country`, `registration_number`, `legal_form`, `client_name`, `status`, `created_at`, `decided_by`, `decided_at`, `decision_reason`.
  - **Related** `directors`: `GET /admin/kyb/cases/{id}/directors` → rows with `full_name`, `role`:badge, `nationality`, `status`:status
  - **Related** `ubos`: `GET /admin/kyb/cases/{id}/ubos` → rows with `full_name`, `ownership_percent`:percent, `nationality`, `relationship`
  - **Related** `documents`: `GET /admin/kyb/cases/{id}/documents` → rows with `document_type`:badge, `file_name`, `result`:badge, `created_at`:datetime
  - **Related** `history`: `GET /admin/kyb/cases/{id}/history` → rows with `created_at`:datetime, `actor`, `action`:mono, `reason`
- **Action `approve`**: `POST /admin/kyb/cases/{id}/decision` — permission `adm:kyb:review` · body includes reason (**required**, store in audit) · shown when `status` ∈ manual_review|pending|processing (enforce the same rule server-side)
  - `decision` — select, **required** · one of: `approved`

  - `evidence` — textarea · Éléments justificatifs de la décision

- **Action `reject`**: `POST /admin/kyb/cases/{id}/decision` — permission `adm:kyb:review` · body includes reason (**required**, store in audit) · shown when `status` ∈ manual_review|pending|processing (enforce the same rule server-side)
  - `decision` — select, **required** · one of: `rejected`

  - `evidence` — textarea · Éléments justificatifs de la décision

- **Action `request_info`**: `POST /admin/kyb/cases/{id}/request-info` — permission `adm:kyb:review`
  - `message` — textarea, **required**

- **Export**: `GET /admin/kyb/cases/export?format=csv|xlsx|pdf` + the same filters as the list. Binary response with `Content-Disposition`.

### `biometrics` — Kafintech · exportable
- **List**: `GET /admin/biometrics/sessions` — permission `adm:biometrics`. Query: `page`, `page_size`, `search`, `final_result` (passed|failed|review|expired), `engine` (internal|external), `created_from`, `created_to`. Response: array **or** `{items,total}`.
- **Row fields** (columns): `id`:mono, `client_name`, `created_at`:datetime, `liveness_result`:badge, `match_result`:badge, `final_result`:status, `failure_reason`, `engine`:badge, `provider`. id is required on every row.
- **Detail**: `GET /admin/biometrics/sessions/{id}`. Fields shown: `id`, `client_name`, `created_at`, `liveness_result`, `match_score`, `match_result`, `final_result`, `failure_reason`, `engine`, `provider`.
- **Export**: `GET /admin/biometrics/sessions/export?format=csv|xlsx|pdf` + the same filters as the list. Binary response with `Content-Disposition`.

### `monitoring` — Kafintech · exportable
- **List**: `GET /admin/monitoring/requests` — permission `adm:monitoring`. Query: `page`, `page_size`, `search`, `status` (pending|processing|approved|rejected|manual_review|failed|expired), `service` (kyc|kyb|biometrics|monitoring), `blocked` (true|false). Response: array **or** `{items,total}`.
- **Row fields** (columns): `reference`:mono, `client_name`, `service`:badge, `status`:status, `blocked`:bool, `age_minutes`:number, `updated_at`:datetime. id is required on every row.
- **Detail**: `GET /admin/monitoring/requests/{id}`. Fields shown: `reference`, `client_name`, `service`, `status`, `blocked`, `age_minutes`.
  - **Related** `events`: `GET /admin/monitoring/requests/{id}/events` → rows with `created_at`:datetime, `event`:mono, `detail`
  - **Related** `interventions`: `GET /admin/monitoring/requests/{id}/interventions` → rows with `created_at`:datetime, `author`, `note`
- **Action `relaunch`**: `POST /admin/monitoring/requests/{id}/relaunch` — permission `adm:kyc:review` · body includes reason (**required**, store in audit) · shown when `blocked` ∈ true (enforce the same rule server-side)
- **Action `note`**: `POST /admin/monitoring/requests/{id}/interventions` — permission `adm:kyc:review`
  - `note` — textarea, **required**

- **Export**: `GET /admin/monitoring/requests/export?format=csv|xlsx|pdf` + the same filters as the list. Binary response with `Content-Disposition`.

### `risk` — Kafintech · exportable
- **List**: `GET /admin/risk/cases` — permission `adm:risk`. Query: `page`, `page_size`, `search`, `risk_level` (low|medium|high), `status` (open|in_review|decided). Response: array **or** `{items,total}`.
- **Row fields** (columns): `reference`:mono, `client_name`, `service`:badge, `risk_level`:risk, `score`:number, `rule_version`:mono, `status`:status, `created_at`:datetime. id is required on every row.
- **Detail**: `GET /admin/risk/cases/{id}`. Fields shown: `reference`, `client_name`, `risk_level`, `score`, `rule_version`, `status`.
  - **Related** `signals`: `GET /admin/risk/cases/{id}/signals` → rows with `rule`, `weight`:number, `detail`
  - **Related** `history`: `GET /admin/risk/cases/{id}/history` → rows with `created_at`:datetime, `actor`, `decision`:badge, `reason`
- **Action `decide`**: `POST /admin/risk/cases/{id}/decision` — permission `adm:risk:write` · body includes reason (**required**, store in audit) · shown when `status` ∈ open|in_review (enforce the same rule server-side)
  - `decision` — select, **required** · one of: `accept`, `reject`, `escalate`

- **Export**: `GET /admin/risk/cases/export?format=csv|xlsx|pdf` + the same filters as the list. Binary response with `Content-Disposition`.

### `risk-rules` — Kafintech
- **List**: `GET /admin/risk/rules` — permission `adm:risk`. Query: `page`, `page_size`, `service` (kyc|kyb|biometrics|monitoring). Response: array **or** `{items,total}`.
- **Row fields** (columns): `name`, `service`:badge, `weight`:number, `version`:mono, `enabled`:bool, `updated_at`:datetime. id is required on every row.
- **Detail**: `GET /admin/risk/rules/{id}`. Fields shown: `name`, `service`, `condition`, `weight`, `version`, `enabled`.
  - **Related** `versions`: `GET /admin/risk/rules/{id}/versions` → rows with `version`:mono, `created_at`:datetime, `author`, `reason`
- **Create**: `POST /admin/risk/rules` — permission `adm:risk:write` — JSON. Returns the created object (id).
  - `name` — text, **required**

  - `service` — select, **required** · one of: `kyc`, `kyb`, `biometrics`, `monitoring`

  - `condition` — textarea, **required** · Expression de la règle (JSON)

  - `weight` — number, **required** · range 0–100

  - `enabled` — switch

- **Edit**: `PATCH /admin/risk/rules/{id}` (same fields, all optional; secrets left empty are unchanged).
- **Action `publish`**: `POST /admin/risk/rules/{id}/publish` — permission `adm:risk:write` · body includes reason (**required**, store in audit)

### `aml` — Kafintech · exportable
- **List**: `GET /admin/aml/alerts` — permission `adm:aml`. Query: `page`, `page_size`, `search`, `list_type` (sanctions|pep), `status` (open|in_review|confirmed|dismissed|escalated). Response: array **or** `{items,total}`.
- **Row fields** (columns): `case_reference`:mono, `client_name`, `subject_name`, `list_type`:badge, `match_score`:percent, `status`:status, `created_at`:datetime. id is required on every row.
- **Detail**: `GET /admin/aml/alerts/{id}`. Fields shown: `case_reference`, `subject_name`, `list_type`, `matched_entry`, `match_score`, `status`.
  - **Related** `history`: `GET /admin/aml/alerts/{id}/history` → rows with `created_at`:datetime, `actor`, `decision`:badge, `reason`
- **Action `confirm`**: `POST /admin/aml/alerts/{id}/decision` — permission `adm:aml:review` · body includes reason (**required**, store in audit) · **critical**: header X-Step-Up-Code (TOTP) must be validated · shown when `status` ∈ open|in_review (enforce the same rule server-side)
  - `decision` — select, **required** · one of: `confirmed`

- **Action `dismiss`**: `POST /admin/aml/alerts/{id}/decision` — permission `adm:aml:review` · body includes reason (**required**, store in audit) · shown when `status` ∈ open|in_review (enforce the same rule server-side)
  - `decision` — select, **required** · one of: `dismissed`

- **Action `escalate`**: `POST /admin/aml/alerts/{id}/decision` — permission `adm:aml:review` · body includes reason (**required**, store in audit) · shown when `status` ∈ open|in_review (enforce the same rule server-side)
  - `decision` — select, **required** · one of: `escalated`

- **Export**: `GET /admin/aml/alerts/export?format=csv|xlsx|pdf` + the same filters as the list. Binary response with `Content-Disposition`.

### `fraud` — Kafintech · exportable
- **List**: `GET /admin/fraud/signals` — permission `adm:fraud`. Query: `page`, `page_size`, `search`, `signal_type` (suspicious_document|inconsistency|repeated_attempts|biometric_anomaly|technical), `severity` (low|medium|high), `status` (open|reviewed|dismissed). Response: array **or** `{items,total}`.
- **Row fields** (columns): `signal_type`:badge, `client_name`, `subject_ref`:mono, `severity`:risk, `status`:status, `created_at`:datetime. id is required on every row.
- **Detail**: `GET /admin/fraud/signals/{id}`. Fields shown: `signal_type`, `client_name`, `subject_ref`, `severity`, `status`, `detail`.
- **Action `review`**: `POST /admin/fraud/signals/{id}/review` — permission `adm:kyc:review` · body includes reason (**required**, store in audit) · shown when `status` ∈ open (enforce the same rule server-side)
  - `decision` — select, **required** · one of: `reviewed`, `dismissed`

- **Export**: `GET /admin/fraud/signals/export?format=csv|xlsx|pdf` + the same filters as the list. Binary response with `Content-Disposition`.

### `invoices` — Kafintech · exportable
- **List**: `GET /admin/billing/invoices` — permission `adm:billing`. Query: `page`, `page_size`, `search`, `status` (draft|pending|paid|due|overdue|void), `currency` (CAD|USD|EUR|XOF|XAF|GBP), `period`. Response: array **or** `{items,total}`.
- **Row fields** (columns): `number`:mono, `client_name`, `period`, `subtotal`:money, `minimum_applied`:bool, `total`:money, `status`:status, `due_at`:date. id is required on every row.
- **Detail**: `GET /admin/billing/invoices/{id}`. Fields shown: `number`, `client_name`, `period`, `currency`, `subscription_amount`, `consumption_amount`, `options_amount`, `integration_fee`, `discount`, `subtotal`, `minimum_applied`, `total`, `status`, `issued_at`, `due_at`, `pricing_version`.
  - **Related** `lines`: `GET /admin/billing/invoices/{id}/lines` → rows with `service`:badge, `description`, `quantity`:number, `unit_price`:money, `amount`:money
  - **Related** `payments`: `GET /admin/billing/invoices/{id}/payments` → rows with `created_at`:datetime, `reference`:mono, `amount`:money, `method`:badge
  - **Related** `credit_notes`: `GET /admin/billing/invoices/{id}/credit-notes` → rows with `number`:mono, `created_at`:datetime, `amount`:money, `reason`
- **Action `mark_paid`**: `POST /admin/billing/invoices/{id}/payments` — permission `adm:billing:write` · shown when `status` ∈ pending|due|overdue (enforce the same rule server-side)
  - `reference` — text, **required**

  - `amount` — number

- **Action `send_reminder`**: `POST /admin/billing/invoices/{id}/remind` — permission `adm:billing:write` · shown when `status` ∈ pending|due|overdue (enforce the same rule server-side)
- **Action `credit_note`**: `POST /admin/billing/invoices/{id}/credit-notes` — permission `adm:billing:write` · body includes reason (**required**, store in audit) · **critical**: header X-Step-Up-Code (TOTP) must be validated
  - `amount` — number, **required** · range 0–…

- **Action `void`**: `POST /admin/billing/invoices/{id}/void` — permission `adm:billing:write` · body includes reason (**required**, store in audit) · **critical**: header X-Step-Up-Code (TOTP) must be validated · shown when `status` ∈ draft|pending (enforce the same rule server-side)
- **Export**: `GET /admin/billing/invoices/export?format=csv|xlsx|pdf` + the same filters as the list. Binary response with `Content-Disposition`.

### `payments` — Kafintech · exportable
- **List**: `GET /admin/billing/payments` — permission `adm:billing`. Query: `page`, `page_size`, `search`, `status` (succeeded|failed|pending|refunded), `currency` (CAD|USD|EUR|XOF|XAF|GBP). Response: array **or** `{items,total}`.
- **Row fields** (columns): `created_at`:datetime, `client_name`, `invoice_number`:mono, `amount`:money, `method`:badge, `status`:status, `reference`:mono. id is required on every row.
- **Export**: `GET /admin/billing/payments/export?format=csv|xlsx|pdf` + the same filters as the list. Binary response with `Content-Disposition`.

### `credit-notes` — Kafintech · exportable
- **List**: `GET /admin/billing/credit-notes` — permission `adm:billing`. Query: `page`, `page_size`, `search`. Response: array **or** `{items,total}`.
- **Row fields** (columns): `number`:mono, `created_at`:datetime, `client_name`, `invoice_number`:mono, `amount`:money, `reason`, `issued_by`. id is required on every row.
- **Export**: `GET /admin/billing/credit-notes/export?format=csv|xlsx|pdf` + the same filters as the list. Binary response with `Content-Disposition`.

### `subscriptions` — Kafintech · exportable
- **List**: `GET /admin/billing/subscriptions` — permission `adm:billing`. Query: `page`, `page_size`, `search`, `plan` (starter|business|enterprise), `status` (active|suspended|cancelled). Response: array **or** `{items,total}`.
- **Row fields** (columns): `client_name`, `plan`:badge, `billing_cycle`:badge, `amount`:money, `monitoring_option`:bool, `status`:status, `renews_at`:date. id is required on every row.
- **Detail**: `GET /admin/billing/subscriptions/{id}`. Fields shown: `client_name`, `plan`, `billing_cycle`, `currency`, `amount`, `monitoring_option`, `status`, `renews_at`, `custom_pricing`.
  - **Related** `limits`: `GET /admin/billing/subscriptions/{id}/limits` → rows with `service`:badge, `monthly_limit`:number, `used`:number, `billing_enabled`:bool
- **Action `change_cycle`**: `POST /admin/billing/subscriptions/{id}/cycle` — permission `adm:billing:write` · body includes reason (**required**, store in audit)
  - `billing_cycle` — select, **required** · one of: `monthly`, `annual`

- **Action `toggle_service`**: `POST /admin/billing/subscriptions/{id}/services` — permission `adm:billing:write` · body includes reason (**required**, store in audit)
  - `service` — select, **required** · one of: `kyc`, `kyb`, `biometrics`, `monitoring`

  - `billing_enabled` — switch

- **Action `set_limits`**: `PUT /admin/billing/subscriptions/{id}/limits` — permission `adm:billing:write` · body includes reason (**required**, store in audit)
  - `kyc_monthly_limit` — number · range 0–…

  - `kyb_monthly_limit` — number · range 0–…

  - `biometrics_monthly_limit` — number · range 0–…

- **Action `custom_pricing`**: `PUT /admin/billing/subscriptions/{id}/custom-pricing` — permission `adm:pricing:write` · body includes reason (**required**, store in audit) · **critical**: header X-Step-Up-Code (TOTP) must be validated
  - `discount_percent` — number · range 0–100

  - `kyc_unit_price` — number · range 0–…

  - `kyb_unit_price` — number · range 0–…

  - `biometrics_unit_price` — number · range 0–…

  - `enterprise_minimum` — number · range 0–…

  - `integration_fee_enabled` — switch

- **Export**: `GET /admin/billing/subscriptions/export?format=csv|xlsx|pdf` + the same filters as the list. Binary response with `Content-Disposition`.

### `usage` — Kafintech · exportable
- **List**: `GET /admin/billing/usage-records` — permission `adm:billing`. Query: `page`, `page_size`, `search`, `service` (kyc|kyb|biometrics|monitoring), `environment` (production|sandbox), `billable` (true|false), `created_from`, `created_to`. Response: array **or** `{items,total}`.
- **Row fields** (columns): `created_at`:datetime, `client_name`, `transaction_id`:mono, `service`:badge, `status`:status, `quantity`:number, `unit_price`:money, `amount`:money, `environment`:badge, `billable`:bool. id is required on every row.
- **Export**: `GET /admin/billing/usage-records/export?format=csv|xlsx|pdf` + the same filters as the list. Binary response with `Content-Disposition`.

### `provider-costs` — Kafintech · exportable
- **List**: `GET /admin/billing/provider-costs` — permission `adm:billing`. Query: `page`, `page_size`, `provider`, `period`. Response: array **or** `{items,total}`.
- **Row fields** (columns): `provider`:badge, `service`:badge, `period`, `units`:number, `unit_cost`:money, `cost`:money. id is required on every row.
- **Export**: `GET /admin/billing/provider-costs/export?format=csv|xlsx|pdf` + the same filters as the list. Binary response with `Content-Disposition`.

### `access-requests` — Kafintech · exportable
- **List**: `GET /admin/developers/access-requests` — permission `adm:api`. Query: `page`, `page_size`, `search`, `status` (pending|approved|rejected). Response: array **or** `{items,total}`.
- **Row fields** (columns): `organization_name`, `contact_email`, `services`:list, `status`:status, `created_at`:datetime. id is required on every row.
- **Detail**: `GET /admin/developers/access-requests/{id}`. Fields shown: `organization_name`, `contact_email`, `project`, `services`, `intended_use`, `technical_info`, `status`, `created_at`, `decided_by`, `decision_reason`.
- **Action `approve`**: `POST /admin/developers/access-requests/{id}/approve` — permission `adm:api:write` · body includes reason (**required**, store in audit) · **critical**: header X-Step-Up-Code (TOTP) must be validated · shown when `status` ∈ pending (enforce the same rule server-side)
  - `services` — multiselect, **required** · one of: `kyc`, `kyb`, `biometrics`, `monitoring`

  - `production` — switch

- **Action `reject`**: `POST /admin/developers/access-requests/{id}/reject` — permission `adm:api:write` · body includes reason (**required**, store in audit) · shown when `status` ∈ pending (enforce the same rule server-side)
- **Export**: `GET /admin/developers/access-requests/export?format=csv|xlsx|pdf` + the same filters as the list. Binary response with `Content-Disposition`.

### `developer-accounts` — Kafintech
- **List**: `GET /admin/developers/accounts` — permission `adm:api`. Query: `page`, `page_size`, `search`. Response: array **or** `{items,total}`.
- **Row fields** (columns): `full_name`, `email`, `organization_name`, `sandbox_access`:bool, `production_access`:bool, `created_at`:date. id is required on every row.

### `api-keys` — Kafintech · exportable
- **List**: `GET /admin/developers/keys` — permission `adm:api`. Query: `page`, `page_size`, `search`, `environment` (production|sandbox), `status` (active|revoked|expired). Response: array **or** `{items,total}`.
- **Row fields** (columns): `prefix`:mono, `client_name`, `environment`:badge, `status`:status, `last_used_at`:datetime, `created_at`:date. id is required on every row.
- **Detail**: `GET /admin/developers/keys/{id}`. Fields shown: `prefix`, `client_name`, `environment`, `status`, `last_used_at`, `created_at`, `revoked_at`.
- **Action `revoke`**: `POST /admin/developers/keys/{id}/revoke` — permission `adm:api:write` · body includes reason (**required**, store in audit) · **critical**: header X-Step-Up-Code (TOTP) must be validated · shown when `status` ∈ active (enforce the same rule server-side)
- **Export**: `GET /admin/developers/keys/export?format=csv|xlsx|pdf` + the same filters as the list. Binary response with `Content-Disposition`.

### `api-logs` — Kafintech · exportable
- **List**: `GET /admin/developers/logs` — permission `adm:api`. Query: `page`, `page_size`, `search`, `environment` (production|sandbox), `errors_only` (true), `created_from`, `created_to`. Response: array **or** `{items,total}`.
- **Row fields** (columns): `created_at`:datetime, `client_name`, `key_prefix`:mono, `method`:badge, `path`:mono, `status_code`:number, `latency_ms`:number, `environment`:badge. id is required on every row.
- **Export**: `GET /admin/developers/logs/export?format=csv|xlsx|pdf` + the same filters as the list. Binary response with `Content-Disposition`.

### `webhooks` — Kafintech
- **List**: `GET /admin/developers/webhooks` — permission `adm:api`. Query: `page`, `page_size`, `search`, `status` (active|disabled|failing). Response: array **or** `{items,total}`.
- **Row fields** (columns): `client_name`, `url`:mono, `events`:list, `environment`:badge, `status`:status, `last_delivery_status`:badge. id is required on every row.
- **Action `disable`**: `POST /admin/developers/webhooks/{id}/disable` — permission `adm:api:write` · body includes reason (**required**, store in audit) · shown when `status` ∈ active|failing (enforce the same rule server-side)

### `staff` — Kafintech · exportable
- **List**: `GET /admin/staff` — permission `adm:staff`. Query: `page`, `page_size`, `search`, `role` (super_admin|platform_admin|compliance_officer|kyc_analyst|risk_officer|finance_manager|support_agent|tech_admin|read_only), `status` (active|inactive). Response: array **or** `{items,total}`.
- **Row fields** (columns): `full_name`, `email`, `role`:badge, `status`:status, `mfa_enabled`:bool, `last_login_at`:datetime. id is required on every row.
- **Detail**: `GET /admin/staff/{id}`. Fields shown: `full_name`, `email`, `role`, `status`, `mfa_enabled`, `last_login_at`, `created_at`.
  - **Related** `logins`: `GET /admin/staff/{id}/logins` → rows with `created_at`:datetime, `ip_address`:mono, `device`, `result`:badge
  - **Related** `actions`: `GET /admin/staff/{id}/audit` → rows with `created_at`:datetime, `action`:mono, `resource_type`, `result`:badge
- **Create**: `POST /admin/staff` — permission `adm:staff` — JSON. Returns the created object (id).
  - `full_name` — text, **required**

  - `email` — email, **required**

  - `role` — select, **required** · one of: `platform_admin`, `compliance_officer`, `kyc_analyst`, `risk_officer`, `finance_manager`, `support_agent`, `tech_admin`, `read_only`

- **Edit**: `PATCH /admin/staff/{id}` (same fields, all optional; secrets left empty are unchanged).
- **Action `change_role`**: `POST /admin/staff/{id}/role` — permission `adm:roles` · body includes reason (**required**, store in audit) · **critical**: header X-Step-Up-Code (TOTP) must be validated
  - `role` — select, **required** · one of: `super_admin`, `platform_admin`, `compliance_officer`, `kyc_analyst`, `risk_officer`, `finance_manager`, `support_agent`, `tech_admin`, `read_only`

- **Action `deactivate`**: `POST /admin/staff/{id}/deactivate` — permission `adm:staff` · body includes reason (**required**, store in audit) · **critical**: header X-Step-Up-Code (TOTP) must be validated · shown when `status` ∈ active (enforce the same rule server-side)
- **Action `activate`**: `POST /admin/staff/{id}/activate` — permission `adm:staff` · body includes reason (**required**, store in audit) · shown when `status` ∈ inactive (enforce the same rule server-side)
- **Action `reset_mfa`**: `POST /admin/staff/{id}/reset-mfa` — permission `adm:staff` · body includes reason (**required**, store in audit) · **critical**: header X-Step-Up-Code (TOTP) must be validated
- **Action `revoke_sessions`**: `POST /admin/staff/{id}/revoke-sessions` — permission `adm:security:write` · body includes reason (**required**, store in audit)
- **Export**: `GET /admin/staff/export?format=csv|xlsx|pdf` + the same filters as the list. Binary response with `Content-Disposition`.

### `sessions` — Kafintech
- **List**: `GET /admin/security/sessions` — permission `adm:security`. Query: `page`, `page_size`, `search`. Response: array **or** `{items,total}`.
- **Row fields** (columns): `user_name`, `role`:badge, `ip_address`:mono, `device`, `started_at`:datetime, `last_seen_at`:datetime. id is required on every row.
- **Action `revoke`**: `POST /admin/security/sessions/{id}/revoke` — permission `adm:security:write` · body includes reason (**required**, store in audit)

### `security-events` — Kafintech · exportable
- **List**: `GET /admin/security/events` — permission `adm:security`. Query: `page`, `page_size`, `search`, `event_type` (suspicious_login|failed_login|permission_change|sensitive_access|admin_activity|incident), `severity` (low|medium|high), `created_from`, `created_to`. Response: array **or** `{items,total}`.
- **Row fields** (columns): `created_at`:datetime, `event_type`:badge, `user_name`, `ip_address`:mono, `severity`:risk, `detail`. id is required on every row.
- **Export**: `GET /admin/security/events/export?format=csv|xlsx|pdf` + the same filters as the list. Binary response with `Content-Disposition`.

### `audit` — Kafintech · exportable
- **List**: `GET /admin/audit-logs` — permission `adm:audit`. Query: `page`, `page_size`, `search`, `result` (success|failure|denied), `resource_type`, `created_from`, `created_to`. Response: array **or** `{items,total}`.
- **Row fields** (columns): `created_at`:datetime, `actor`, `action`:mono, `resource_type`, `resource_id`:mono, `result`:badge, `ip_address`:mono. id is required on every row.
- **Detail**: `GET /admin/audit-logs/{id}`. Fields shown: `id`, `created_at`, `actor`, `actor_type`, `action`, `resource_type`, `resource_id`, `result`, `ip_address`, `request_id`, `details`.
- **Export**: `GET /admin/audit-logs/export?format=csv|xlsx|pdf` + the same filters as the list. Binary response with `Content-Disposition`.

### `notifications` — Kafintech
- **List**: `GET /admin/notifications` — permission `adm:notifications`. Query: `page`, `page_size`, `category` (new_verification|pending_case|review_needed|technical_failure|api_incident|risk_alert|unpaid_invoice|payment_issue|provider_down), `read` (false|true). Response: array **or** `{items,total}`.
- **Row fields** (columns): `created_at`:datetime, `level`:risk, `category`:badge, `title`, `read`:bool. id is required on every row.
- **Action `mark_read`**: `POST /admin/notifications/{id}/read` — permission `adm:notifications` · shown when `read` ∈ false (enforce the same rule server-side)

### `requests` — Kafintech · exportable
- **List**: `GET /admin/requests` — permission `adm:requests`. Query: `page`, `page_size`, `search`, `status` (new|assigned|in_progress|waiting_for_customer|resolved|closed), `department` (sales|partnerships|integration|institutional|other). Response: array **or** `{items,total}`.
- **Row fields** (columns): `reference`:mono, `request_type`:badge, `full_name`, `company`, `country`, `department`:badge, `status`:status, `assignee_name`, `created_at`:datetime. id is required on every row.
- **Detail**: `GET /admin/requests/{id}`. Fields shown: `reference`, `request_type`, `status`, `department`, `assignee_name`, `created_at`, `full_name`, `company`, `email`, `phone`, `country`, `role`, `sector`, `estimated_volume`, `services`, `subject`, `message`.
  - **Related** `comments`: `GET /admin/requests/{id}/comments` → rows with `created_at`:datetime, `author`, `comment`
  - **Related** `history`: `GET /admin/requests/{id}/history` → rows with `created_at`:datetime, `actor`, `action`:mono
- **Action `assign`**: `POST /admin/requests/{id}/assign` — permission `adm:requests`
  - `department` — select · one of: `sales`, `partnerships`, `integration`, `institutional`, `other`

  - `assignee_id` — staff

- **Action `set_status`**: `POST /admin/requests/{id}/status` — permission `adm:requests`
  - `status` — select, **required** · one of: `new`, `assigned`, `in_progress`, `waiting_for_customer`, `resolved`, `closed`

- **Action `comment`**: `POST /admin/requests/{id}/comments` — permission `adm:requests`
  - `comment` — textarea, **required**

- **Export**: `GET /admin/requests/export?format=csv|xlsx|pdf` + the same filters as the list. Binary response with `Content-Disposition`.

### `support` — Kafintech · exportable
- **List**: `GET /admin/support/tickets` — permission `adm:support`. Query: `page`, `page_size`, `search`, `status` (open|in_progress|waiting_for_customer|resolved|closed), `priority` (low|medium|high). Response: array **or** `{items,total}`.
- **Row fields** (columns): `reference`:mono, `client_name`, `subject`, `priority`:risk, `status`:status, `assignee_name`, `updated_at`:datetime. id is required on every row.
- **Detail**: `GET /admin/support/tickets/{id}`. Fields shown: `reference`, `client_name`, `subject`, `category`, `priority`, `status`, `assignee_name`, `created_at`.
  - **Related** `messages`: `GET /admin/support/tickets/{id}/messages` → rows with `created_at`:datetime, `author`, `message`
- **Action `reply`**: `POST /admin/support/tickets/{id}/messages` — permission `adm:support`
  - `message` — textarea, **required**

- **Action `set_status`**: `POST /admin/support/tickets/{id}/status` — permission `adm:support`
  - `status` — select, **required** · one of: `open`, `in_progress`, `waiting_for_customer`, `resolved`, `closed`

- **Action `assign`**: `POST /admin/support/tickets/{id}/assign` — permission `adm:support`
  - `assignee_id` — staff, **required**

- **Export**: `GET /admin/support/tickets/export?format=csv|xlsx|pdf` + the same filters as the list. Binary response with `Content-Disposition`.

### `articles` — Kafintech
- **List**: `GET /admin/content/articles` — permission `adm:content`. Query: `page`, `page_size`, `search`, `status` (draft|review|scheduled|published|archived), `category` (kyc|kyb|biometrics|aml|fraud|fintech|trust). Response: array **or** `{items,total}`.
- **Row fields** (columns): `title_fr`, `category`:badge, `author`, `status`:status, `publish_at`:datetime, `views`:number. id is required on every row.
- **Detail**: `GET /admin/content/articles/{id}`. Fields shown: `title_fr`, `title_en`, `slug`, `category`, `status`, `publish_at`, `source_url`.
- **Create**: `POST /admin/content/articles` — permission `adm:content` — **multipart/form-data**: payload (JSON) + file parts. Returns the created object (id).
  - `title_fr` — text, **required**

  - `title_en` — text, **required**

  - `slug` — text, **required**

  - `category` — select, **required** · one of: `kyc`, `kyb`, `biometrics`, `aml`, `fraud`, `fintech`, `trust`

  - `author` — text

  - `source_name` — text · Actualité externe : nom de la source

  - `source_url` — url · Lien vers l’original (obligatoire pour une actualité externe)

  - `summary_fr` — textarea, **required**

  - `summary_en` — textarea, **required**

  - `body_fr` — textarea, **required**

  - `body_en` — textarea, **required**

  - `cover` — file · multipart file part

- **Edit**: `PATCH /admin/content/articles/{id}` (same fields, all optional; secrets left empty are unchanged).
- **Action `publish`**: `POST /admin/content/articles/{id}/publish` — permission `adm:content` · shown when `status` ∈ draft|review|scheduled (enforce the same rule server-side)
- **Action `schedule`**: `POST /admin/content/articles/{id}/schedule` — permission `adm:content` · shown when `status` ∈ draft|review (enforce the same rule server-side)
  - `publish_at` — date, **required**

- **Action `archive`**: `POST /admin/content/articles/{id}/archive` — permission `adm:content` · shown when `status` ∈ published (enforce the same rule server-side)

### `guides` — Kafintech
- **List**: `GET /admin/content/guides` — permission `adm:content`. Query: `page`, `page_size`, `search`, `access` (free|premium), `status` (draft|published|archived). Response: array **or** `{items,total}`.
- **Row fields** (columns): `title_fr`, `access`:badge, `status`:status, `downloads`:number, `updated_at`:datetime. id is required on every row.
- **Detail**: `GET /admin/content/guides/{id}`. Fields shown: `title_fr`, `title_en`, `access`, `status`, `downloads`.
- **Create**: `POST /admin/content/guides` — permission `adm:content` — **multipart/form-data**: payload (JSON) + file parts. Returns the created object (id).
  - `title_fr` — text, **required**

  - `title_en` — text, **required**

  - `description_fr` — textarea

  - `description_en` — textarea

  - `access` — select, **required** · one of: `free`, `premium`

  - `file_fr` — file · multipart file part

  - `file_en` — file · multipart file part

  - `cover` — file · multipart file part

- **Edit**: `PATCH /admin/content/guides/{id}` (same fields, all optional; secrets left empty are unchanged).
- **Action `publish`**: `POST /admin/content/guides/{id}/publish` — permission `adm:content` · shown when `status` ∈ draft (enforce the same rule server-side)
- **Action `archive`**: `POST /admin/content/guides/{id}/archive` — permission `adm:content` · shown when `status` ∈ published (enforce the same rule server-side)

### `faq` — Kafintech
- **List**: `GET /admin/content/faq` — permission `adm:content`. Query: `page`, `page_size`, `search`, `category` (general|kyc|kyb|biometrics|api|security|billing). Response: array **or** `{items,total}`.
- **Row fields** (columns): `question_fr`, `category`:badge, `position`:number, `status`:status. id is required on every row.
- **Detail**: `GET /admin/content/faq/{id}`. Fields shown: `category`, `question_fr`, `question_en`, `answer_fr`, `answer_en`, `status`.
- **Create**: `POST /admin/content/faq` — permission `adm:content` — JSON. Returns the created object (id).
  - `category` — select, **required** · one of: `general`, `kyc`, `kyb`, `biometrics`, `api`, `security`, `billing`

  - `question_fr` — text, **required**

  - `question_en` — text, **required**

  - `answer_fr` — textarea, **required**

  - `answer_en` — textarea, **required**

  - `position` — number · range 0–…

  - `status` — select · one of: `draft`, `published`

- **Edit**: `PATCH /admin/content/faq/{id}` (same fields, all optional; secrets left empty are unchanged).

### `case-studies` — Kafintech
- **List**: `GET /admin/content/case-studies` — permission `adm:content`. Query: `page`, `page_size`, `search`, `sector` (banks|fintech|micro|insurance|telecom|ecommerce|platforms|other). Response: array **or** `{items,total}`.
- **Row fields** (columns): `title_fr`, `sector`:badge, `illustrative`:bool, `status`:status. id is required on every row.
- **Detail**: `GET /admin/content/case-studies/{id}`. Fields shown: `title_fr`, `title_en`, `sector`, `illustrative`, `status`.
- **Create**: `POST /admin/content/case-studies` — permission `adm:content` — JSON. Returns the created object (id).
  - `title_fr` — text, **required**

  - `title_en` — text, **required**

  - `sector` — select, **required** · one of: `banks`, `fintech`, `micro`, `insurance`, `telecom`, `ecommerce`, `platforms`, `other`

  - `context_fr` — textarea

  - `context_en` — textarea

  - `problem_fr` — textarea

  - `problem_en` — textarea

  - `solution_fr` — textarea

  - `solution_en` — textarea

  - `modules` — multiselect · one of: `kyc`, `kyb`, `biometrics`, `monitoring`

  - `illustrative` — switch · Scénario illustratif (aucune référence client réelle sans preuve et autorisation)

  - `status` — select · one of: `draft`, `published`

- **Edit**: `PATCH /admin/content/case-studies/{id}` (same fields, all optional; secrets left empty are unchanged).

### `leads` — Kafintech · exportable
- **List**: `GET /admin/content/download-leads` — permission `adm:content`. Query: `page`, `page_size`, `search`. Response: array **or** `{items,total}`.
- **Row fields** (columns): `created_at`:datetime, `full_name`, `company`, `email`, `guide_title`, `marketing_consent`:bool. id is required on every row.
- **Export**: `GET /admin/content/download-leads/export?format=csv|xlsx|pdf` + the same filters as the list. Binary response with `Content-Disposition`.

### `kyb` — client · exportable
- **List**: `GET /kyb/cases` — permission `kyb:read`. Query: `page`, `page_size`, `search`, `status` (pending|processing|approved|rejected|manual_review|failed|expired), `created_from`, `created_to`. Response: array **or** `{items,total}`.
- **Row fields** (columns): `legal_name`, `country`, `registration_number`:mono, `reference`:mono, `status`:status, `created_at`:datetime. id is required on every row.
- **Detail**: `GET /kyb/cases/{id}`. Fields shown: `legal_name`, `country`, `registration_number`, `legal_form`, `reference`, `status`, `created_at`.
  - **Related** `directors`: `GET /kyb/cases/{id}/directors` → rows with `full_name`, `role`:badge, `nationality`, `status`:status
  - **Related** `ubos`: `GET /kyb/cases/{id}/ubos` → rows with `full_name`, `ownership_percent`:percent, `nationality`
  - **Related** `documents`: `GET /kyb/cases/{id}/documents` → rows with `document_type`:badge, `file_name`, `created_at`:datetime
  - **Related** `events`: `GET /kyb/cases/{id}/events` → rows with `created_at`:datetime, `event`:mono, `detail`
- **Create**: `POST /kyb/cases` — permission `kyb:create` — **multipart/form-data**: payload (JSON) + file parts. Returns the created object (id).
  - `legal_name` — text, **required**

  - `country` — text, **required** · ISO 3166-1 alpha-2

  - `registration_number` — text, **required**

  - `legal_form` — text

  - `reference` — text · Votre référence interne

  - `documents` — repeater
    - `document_type` — select, **required** · one of: `registration_certificate`, `articles_of_association`, `ownership_structure`, `proof_of_address`, `other`
    - `file` — file, **required** · multipart file part

  - `directors` — repeater
    - `full_name` — text, **required**
    - `role` — text, **required**
    - `nationality` — text
    - `birth_date` — date

  - `ubos` — repeater
    - `full_name` — text, **required**
    - `ownership_percent` — number, **required** · range 0–100
    - `nationality` — text
    - `birth_date` — date

- **Action `provide_info`**: `POST /kyb/cases/{id}/info` — permission `kyb:create` · shown when `status` ∈ manual_review|pending (enforce the same rule server-side)
  - `message` — textarea, **required**

  - `file` — file · multipart file part

- **Export**: `GET /kyb/cases/export?format=csv|xlsx|pdf` + the same filters as the list. Binary response with `Content-Disposition`.

### `monitoring` — client · exportable
- **List**: `GET /monitoring/requests` — permission `monitoring:read`. Query: `page`, `page_size`, `search`, `status` (pending|processing|approved|rejected|manual_review), `service` (kyc|kyb|biometrics|monitoring), `pending_only` (true). Response: array **or** `{items,total}`.
- **Row fields** (columns): `reference`:mono, `service`:badge, `status`:status, `blocked`:bool, `created_at`:datetime, `updated_at`:datetime. id is required on every row.
- **Detail**: `GET /monitoring/requests/{id}`. Fields shown: `reference`, `service`, `status`, `blocked`, `created_at`, `updated_at`.
  - **Related** `events`: `GET /monitoring/requests/{id}/events` → rows with `created_at`:datetime, `event`:mono, `detail`
  - **Related** `actions`: `GET /monitoring/requests/{id}/actions` → rows with `created_at`:datetime, `action`:mono, `actor`
- **Export**: `GET /monitoring/requests/export?format=csv|xlsx|pdf` + the same filters as the list. Binary response with `Content-Disposition`.

### `alerts` — client
- **List**: `GET /monitoring/alerts` — permission `monitoring:read`. Query: `page`, `page_size`, `read` (false|true). Response: array **or** `{items,total}`.
- **Row fields** (columns): `created_at`:datetime, `level`:risk, `category`:badge, `title`, `reference`:mono, `read`:bool. id is required on every row.
- **Action `mark_read`**: `POST /monitoring/alerts/{id}/read` — permission `monitoring:read` · shown when `read` ∈ false (enforce the same rule server-side)

### `biometrics` — client · exportable
- **List**: `GET /biometrics/sessions` — permission `biometrics:use`. Query: `page`, `page_size`, `search`, `final_result` (passed|failed|review|expired), `created_from`, `created_to`. Response: array **or** `{items,total}`.
- **Row fields** (columns): `id`:mono, `case_reference`:mono, `created_at`:datetime, `liveness_result`:badge, `match_result`:badge, `final_result`:status, `failure_reason`. id is required on every row.
- **Export**: `GET /biometrics/sessions/export?format=csv|xlsx|pdf` + the same filters as the list. Binary response with `Content-Disposition`.

### `support` — client
- **List**: `GET /support/tickets` — permission `support:use`. Query: `page`, `page_size`, `search`, `status` (open|in_progress|waiting_for_customer|resolved|closed). Response: array **or** `{items,total}`.
- **Row fields** (columns): `reference`:mono, `subject`, `category`:badge, `priority`:risk, `status`:status, `updated_at`:datetime. id is required on every row.
- **Detail**: `GET /support/tickets/{id}`. Fields shown: `reference`, `subject`, `category`, `priority`, `status`, `created_at`.
  - **Related** `messages`: `GET /support/tickets/{id}/messages` → rows with `created_at`:datetime, `author`, `message`
- **Create**: `POST /support/tickets` — permission `support:use` — **multipart/form-data**: payload (JSON) + file parts. Returns the created object (id).
  - `subject` — text, **required**

  - `category` — select, **required** · one of: `incident`, `integration`, `billing`, `verification`, `other`

  - `priority` — select, **required** · one of: `low`, `medium`, `high`

  - `message` — textarea, **required**

  - `attachment` — file · multipart file part

- **Action `reply`**: `POST /support/tickets/{id}/messages` — permission `support:use` · shown when `status` ∈ open|in_progress|waiting_for_customer (enforce the same rule server-side)
  - `message` — textarea, **required**

  - `attachment` — file · multipart file part

- **Action `close`**: `POST /support/tickets/{id}/close` — permission `support:use` · shown when `status` ∈ open|in_progress|waiting_for_customer|resolved (enforce the same rule server-side)

### `invoices` — client · exportable
- **List**: `GET /billing/invoices` — permission `billing:read`. Query: `page`, `page_size`, `status` (pending|paid|due|overdue), `period`. Response: array **or** `{items,total}`.
- **Row fields** (columns): `number`:mono, `period`, `total`:money, `status`:status, `issued_at`:date, `due_at`:date, `pdf_url`:file. id is required on every row.
- **Detail**: `GET /billing/invoices/{id}`. Fields shown: `number`, `period`, `currency`, `subscription_amount`, `consumption_amount`, `options_amount`, `integration_fee`, `discount`, `minimum_applied`, `total`, `status`, `issued_at`, `due_at`.
  - **Related** `lines`: `GET /billing/invoices/{id}/lines` → rows with `service`:badge, `description`, `quantity`:number, `unit_price`:money, `amount`:money
- **Export**: `GET /billing/invoices/export?format=csv|xlsx|pdf` + the same filters as the list. Binary response with `Content-Disposition`.

### `payments` — client · exportable
- **List**: `GET /billing/payments` — permission `billing:read`. Query: `page`, `page_size`. Response: array **or** `{items,total}`.
- **Row fields** (columns): `created_at`:datetime, `invoice_number`:mono, `amount`:money, `method`:badge, `status`:status, `reference`:mono. id is required on every row.
- **Export**: `GET /billing/payments/export?format=csv|xlsx|pdf` + the same filters as the list. Binary response with `Content-Disposition`.

### `usage` — client · exportable
- **List**: `GET /billing/usage` — permission `billing:read`. Query: `page`, `page_size`, `service` (kyc|kyb|biometrics|monitoring), `environment` (production|sandbox), `created_from`, `created_to`. Response: array **or** `{items,total}`.
- **Row fields** (columns): `created_at`:datetime, `service`:badge, `transaction_id`:mono, `status`:status, `quantity`:number, `unit_price`:money, `amount`:money, `environment`:badge. id is required on every row.
- **Export**: `GET /billing/usage/export?format=csv|xlsx|pdf` + the same filters as the list. Binary response with `Content-Disposition`.

### `webhooks` — client
- **List**: `GET /developers/webhooks` — permission `developers:manage`. Query: `page`, `page_size`. Response: array **or** `{items,total}`.
- **Row fields** (columns): `url`:mono, `events`:list, `environment`:badge, `status`:status, `last_delivery_status`:badge. id is required on every row.
- **Detail**: `GET /developers/webhooks/{id}`. Fields shown: `url`, `events`, `environment`, `status`, `created_at`.
  - **Related** `deliveries`: `GET /developers/webhooks/{id}/deliveries` → rows with `created_at`:datetime, `event`:mono, `status_code`:number, `attempts`:number, `status`:status
- **Create**: `POST /developers/webhooks` — permission `developers:manage` — JSON. Returns the created object (id).
  - `url` — url, **required**

  - `environment` — select, **required** · one of: `sandbox`, `production`

  - `events` — multiselect, **required** · one of: `verification.created`, `verification.started`, `document.submitted`, `verification.completed`, `result.available`, `verification.needs_review`

- **Edit**: `PATCH /developers/webhooks/{id}` (same fields, all optional; secrets left empty are unchanged).
- **Action `rotate_secret`**: `POST /developers/webhooks/{id}/rotate-secret` — permission `developers:manage`
- **Action `test`**: `POST /developers/webhooks/{id}/test` — permission `developers:manage`
- **Action `disable`**: `POST /developers/webhooks/{id}/disable` — permission `developers:manage` · shown when `status` ∈ active|failing (enforce the same rule server-side)
- **Action `enable`**: `POST /developers/webhooks/{id}/enable` — permission `developers:manage` · shown when `status` ∈ disabled (enforce the same rule server-side)

### `api-logs` — client · exportable
- **List**: `GET /developers/logs` — permission `developers:manage`. Query: `page`, `page_size`, `search`, `environment` (production|sandbox), `errors_only` (true), `created_from`, `created_to`. Response: array **or** `{items,total}`.
- **Row fields** (columns): `created_at`:datetime, `key_prefix`:mono, `method`:badge, `path`:mono, `status_code`:number, `latency_ms`:number, `environment`:badge. id is required on every row.
- **Export**: `GET /developers/logs/export?format=csv|xlsx|pdf` + the same filters as the list. Binary response with `Content-Disposition`.

## 5. Configuration pages

### `platform`
- `GET /admin/platform/settings` → `{values:{…}, status?:{…}}` (or the values at the top level). `PUT /admin/platform/settings` — permission `adm:platform`, body = values + `reason`, header X-Step-Up-Code. Versioned + audited.
- **modules**
  - `module_kyc` — switch
  - `module_kyb` — switch
  - `module_biometrics` — switch
  - `module_monitoring` — switch
  - `module_aml` — switch
  - `module_fraud` — switch
- **environments**
  - `sandbox_enabled` — switch
  - `production_enabled` — switch
  - `maintenance_mode` — switch · Bloque les nouvelles vérifications clients
- **localization**
  - `languages` — multiselect, **required** · one of: `fr`, `en`
  - `default_language` — select, **required** · one of: `fr`, `en`
  - `currencies` — multiselect, **required** · one of: `CAD`, `USD`, `EUR`, `XOF`, `XAF`, `GBP`
  - `default_currency` — select, **required** · one of: `CAD`, `USD`, `EUR`, `XOF`, `XAF`, `GBP`
- **operations**
  - `max_upload_mb` — number · range 1–100
  - `case_expiry_days` — number · range 1–…
  - `ocr_review_threshold` — number · range 0–1 · Seuil de confiance OCR sous lequel un dossier passe en revue manuelle (0 à 1)

### `settings`
- `GET /admin/settings` → `{values:{…}, status?:{…}}` (or the values at the top level). `PUT /admin/settings` — permission `adm:settings`, body = values + `reason`, header X-Step-Up-Code. Versioned + audited.
- **sessions**
  - `session_timeout_minutes` — number · range 5–480
  - `mfa_methods` — multiselect, **required** · one of: `totp`, `passkey`
  - `password_min_length` — number · range 12–128
- **network**
  - `ip_policy` — select · one of: `off`, `audit`, `enforce`
  - `ip_allowlist` — textarea · Une adresse ou plage CIDR par ligne
- **retention**
  - `document_retention_days` — number · range 1–…
  - `audit_retention_days` — number · range 365–…
- **alerts**
  - `email_alerts` — switch
  - `alert_recipients` — textarea · Une adresse e-mail par ligne
  - `sensitive_change_alerts` — switch
- **breakglass**
  - `breakglass_enabled` — switch · Compte de secours : accès exceptionnel, audit obligatoire
  - `breakglass_notify` — textarea · E-mails notifiés à chaque utilisation

### `providers`
- `GET /admin/providers` → `{values:{…}, status?:{…}}` (or the values at the top level). `PUT /admin/providers` — permission `adm:providers`, body = values + `reason`, header X-Step-Up-Code. Versioned + audited.
- **ocr**
  - `ocr_enabled` — switch
  - `ocr_provider` — text
  - `ocr_api_url` — url
  - `ocr_api_key` — password · **write-only secret**
  - `ocr_cost_per_unit` — number · range 0–…
  - `ocr_cost_currency` — select · one of: `CAD`, `USD`, `EUR`, `XOF`, `XAF`, `GBP`
- **bio**
  - `bio_mode` — select, **required** · one of: `internal`, `hybrid`, `external`
  - `bio_enabled` — switch
  - `bio_provider` — text
  - `bio_api_url` — url
  - `bio_api_key` — password · **write-only secret**
  - `bio_cost_per_session` — number · range 0–…
  - `bio_cost_currency` — select · one of: `CAD`, `USD`, `EUR`, `XOF`, `XAF`, `GBP`
- **aml**
  - `aml_enabled` — switch
  - `aml_provider` — text
  - `aml_api_key` — password · **write-only secret**
  - `aml_lists` — multiselect · one of: `sanctions`, `pep`, `adverse_media`
- **cloud**
  - `cloud_provider` — text
  - `cloud_region` — text
  - `storage_bucket` — text
  - `cloud_credentials` — password · **write-only secret**
- **messaging**
  - `email_provider` — text
  - `email_api_key` — password · **write-only secret**
  - `webhook_signing_secret` — password · **write-only secret**
- `GET` also returns `status.{ocr,bio,aml,cloud}: {available, errors_24h, latency_ms, cost_30d, currency}`.


## 6. Dedicated endpoints

### Global dashboard — `GET /admin/dashboard?range=today|7d|30d|90d|custom&from&to&country&service&client_id` (`adm:dashboard`)
```json
{ "clients":   {"total":0,"active":0,"new":0,"suspended":0,"pending_validation":0},
  "kyc":       {"total":0,"approved":0,"rejected":0,"pending":0,"manual_review":0},
  "kyb":       {"received":0,"approved":0,"rejected":0,"in_progress":0},
  "biometrics":{"sessions":0,"passed":0,"failed":0,"needs_review":0},
  "financial": {"currency":"CAD","revenue_month":0,"revenue_total":0,"active_subscriptions":0,"billable_consumption":0,"unpaid_invoices":0,"payments_received":0},
  "technical": {"availability_percent":99.9,"api_errors":0,"latency_ms":0,"providers":[{"name":"ocr","status":"active","latency_ms":0}],"alerts":[{"level":"high","message":""}]},
  "series":    {"daily":[{"date":"2026-11-01","kyc":0,"kyb":0,"biometrics":0}]} }
```
Numeric keys under each block are rendered automatically (label = `rx.f.<key>`), so extra keys appear without front-end change.

### Pricing — `GET|PUT /admin/pricing`, `GET /admin/pricing/history` (`adm:billing` / `adm:pricing:write` + step-up + `reason`)
```json
{ "version":"v3","effective_from":"2026-12-01","currencies":["CAD","USD","EUR","XOF","XAF","GBP"],
  "plans":{ "starter":{"monthly":{"CAD":0},"annual":{"CAD":0}}, "business":{"monthly":{},"annual":{}},
            "enterprise":{"monthly":{},"annual":{},"minimum_commitment":{"CAD":0}} },
  "usage":{"kyc":{"CAD":0},"kyb":{"CAD":0},"biometrics":{"CAD":0}},
  "options":{"monitoring_monthly":{"CAD":0}},
  "integration_fee":{"enabled":true,"amounts":{"CAD":0}} }
```
`PUT` accepts the same shape (+ `effective_from`, `reason`) and **creates a new version**; it must never alter invoices already issued. History rows: `version, effective_from, created_at, author, reason`.

### Roles — `GET /admin/roles` → `[{role, permissions[]}]`; `PUT /admin/roles/{role}` `{permissions[], reason}` + step-up. `super_admin` is immutable.
### Infrastructure — `GET /admin/infrastructure` (`adm:infra`) read-only
`{overall_status:"operational|degraded|down", cpu_percent, memory_percent, storage:{used_gb,total_gb}, network:{in_mbps,out_mbps}, services:[{name,status,latency_ms,uptime_percent}], databases:[{name,status,connections}], backups:[{name,last_success_at,status}], incidents:[{title,status,started_at}], capacity_alerts:[{level,message}], generated_at}`
### Security overview — `GET /admin/security/overview` → `{failed_logins_24h, suspicious_logins_24h, active_sessions, open_alerts, sensitive_access_24h, mfa_coverage_percent}`
### Reports — `GET /admin/reports/{id}/export?format=pdf|csv|xlsx&from&to&country&client_id` (`adm:reports`). Ids: `activity`, `financial`, `per_client`, `per_country`, `kyc_kyb`, `biometrics`, `incidents`, `provider_costs`, `technical`, `security`.
### Admin KYC review — `GET /admin/kyc/cases/{id}` (case + `documents[]` + `client_name`), `GET …/history`, `GET …/documents/{doc}/content` (image), `POST …/decision` `{decision:"approved|rejected|request_new", reason, evidence}` (`adm:kyc:review`; 409 if already decided). A human decision stores agent identity, date, reason and evidence.
### Client billing summary — `GET /billing/summary`
`{plan, billing_cycle, currency, period, next_invoice_at, subscription_amount, usage:{kyc:{count,amount},kyb:{…},biometrics:{…}}, monitoring_amount, integration_fee, discount, minimum_applied, total_due}`. Invoices: `GET /billing/invoices` (+ `pdf_url`), payments, usage (resources above).
### Client developer portal
- `GET /developers/access` → `{status:"none|pending|approved|rejected", sandbox:true, production:false, services[], decision_reason}`
- `POST /developers/access-requests` `{organization_name, project, services[], intended_use, technical_info}` — creating an account/request **never** activates production by itself; Kafintech validates manually (admin action `approve`).
- `GET /developers/keys?environment=`, `POST /developers/keys` `{name, environment, expires_in_days?}` → `{id, prefix, key}` (key shown once), `DELETE /developers/keys/{id}`. Production keys only after approval.
### Biometrics (client) — `POST /biometrics/sessions` `{case_reference?}` → `{token, expires_in_minutes}`; public mobile flow posts frames to `POST /biometrics/sessions/{token}/frames` `{frames:[dataURL]}`; `GET|PATCH /biometrics/settings` `{trigger_level:"off|medium|high"}`.
### Public requests (website forms) — `POST /public/contact-requests` (**unauthenticated**, rate-limited, CORS closed)
`{kind:"contact|demo", locale, fields:{full_name,company,email,country,role,type,subject,message,phone,sector,volume,services[],consent_privacy:true,consent_marketing}}` → `{reference}`. Required behaviour: persist, send the confirmation e-mail to the sender, e-mail the relevant department (routing: sales/demo/quote → Sales; partnership → Partnerships; others by category), status `new`. **Technical support is never created from this form** (customer portal only).

## 7. Billing rules (backend is the reference; the admin “Invoice simulator” implements the same maths)
- **Hybrid model**: monthly subscription (Starter / Business / Enterprise) **+** consumption per verification. Prices are **configuration, never hard-coded**, per currency, versioned.
- Subscription billed on the subscription anniversary; annual payment optional (annual price + discounts configurable). Consumption billed at month end.
- **KYC**: bill an executed, billable verification — not a mere case creation or a non-executed technical attempt. **KYB**: per company file effectively processed. **Biometrics & liveness**: per executed and recorded session. **Monitoring**: monthly option fee only — never per status check/event.
- Operations failed because of an IZI LENS fault are **not** billed automatically. **Sandbox is never billed.**
- **Starter / Business**: total = subscription + consumption + options (+ integration fee if enabled) − discount. No minimum.
- **Enterprise**: total = **MAX( subscription + consumption + options , contractual minimum )** — the minimum is a floor on the *total*, never an extra amount. Example: 1 000 + 300 + 200 = 1 500 → pay 1 500 (not 2 500). If computed total is 800 → pay 1 000. Applied per Enterprise account.
- Each billable operation creates a usage record: client id, transaction id, service, timestamp, status, billable quantity, unit price, currency, amount, environment, pricing version.
- Credit notes / corrections / refunds: always with reason + audit trail; issued invoices are immutable.
- Provider costs (OCR external API, biometrics hybrid, cloud) are tracked **separately** from customer prices.
- Public site shows **no prices** (quote-based).

### Initial reference values (seed only — load into the pricing table, do not hard-code)
Subscriptions (CAD/month): Starter 100 · Business 300 · Enterprise 1 000 (Enterprise minimum 1 000 CAD/month total). Consumption (CAD): KYC 1.25 / verification · KYB 8.00 / company file · Biometrics & liveness 0.90 / session · Monitoring option 50 / month. Integration fee 500 CAD (indicative, optional, toggleable). Other currencies (USD, EUR, XOF, XAF, GBP) to be priced by Kafintech — no automatic conversion.

## 8. Webhook events (client webhooks)
`verification.created`, `verification.started`, `document.submitted`, `verification.completed`, `result.available`, `verification.needs_review`. Each delivery is signed (HMAC, per-webhook secret, rotatable) and logged (`deliveries`: created_at, event, status_code, attempts, status) with retries.

## 9. Audit log requirements
Every sensitive operation writes an append-only event: actor (user/api_key/system), action, resource type + id, result (success|failure|denied), IP, request id, timestamp, details. Includes: account create/delete, permission changes, client suspend/activate, tariff changes, configuration changes, sensitive data access, billing actions, security actions, integration changes. Protect against modification.

## 10. Notifications (internal)
Categories: new_verification, pending_case, review_needed, technical_failure, api_incident, risk_alert, unpaid_invoice, payment_issue, provider_down. Email delivery configurable in `settings` (`email_alerts`, `alert_recipients`).
