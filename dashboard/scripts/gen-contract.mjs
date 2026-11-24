// Génère docs/FRONTEND_CONTRACT.md à partir des registres TypeScript (source unique de vérité).
// Usage : npm run contract
import { build } from 'esbuild';
import { writeFileSync, mkdirSync, readFileSync, readdirSync } from 'node:fs';
import { pathToFileURL } from 'node:url';

const out = 'node_modules/.contract/entry.mjs';
mkdirSync('node_modules/.contract', { recursive: true });
// Les registres importent des icônes Svelte : on les remplace par des valeurs nulles (inutiles pour le contrat).
const iconNames = new Set();
for (const f of readdirSync('src/lib/config')) {
	const src = readFileSync(`src/lib/config/${f}`, 'utf8');
	for (const m of src.matchAll(/import\s*\{([^}]*)\}\s*from\s*'@lucide\/svelte'/g)) m[1].split(',').map((x) => x.trim()).filter(Boolean).forEach((n) => iconNames.add(n));
}
const lucideStub = { name: 'lucide-stub', setup(b) {
	b.onResolve({ filter: /^@lucide\/svelte$/ }, () => ({ path: 'lucide', namespace: 'stub' }));
	b.onLoad({ filter: /.*/, namespace: 'stub' }, () => ({ contents: [...iconNames].map((n) => `export const ${n} = null;`).join('\n'), loader: 'js' }));
} };
await build({ entryPoints: ['scripts/contract-entry.ts'], bundle: true, format: 'esm', platform: 'node', outfile: out, logLevel: 'error', alias: { $lib: './src/lib' }, plugins: [lucideStub] });
const { ADMIN_RESOURCES, CLIENT_RESOURCES, CONFIG_PAGES, REPORTS, ALL_PERMISSIONS, STAFF_ROLES, CLIENT_ROLES, permissionsOf } = await import(pathToFileURL(process.cwd() + '/' + out).href);

const field = (f, ind = '') => `${ind}- \`${f.name}\` — ${f.type}${f.required ? ', **required**' : ''}${f.options ? ` · one of: ${f.options.map((o) => `\`${o}\``).join(', ')}` : ''}${f.secret ? ' · **write-only secret**' : ''}${f.min !== undefined || f.max !== undefined ? ` · range ${f.min ?? '…'}–${f.max ?? '…'}` : ''}${f.hint ? ` · ${f.hint}` : ''}${f.type === 'file' ? ' · multipart file part' : ''}\n` + (f.fields ? f.fields.map((s) => field(s, ind + '  ')).join('') : '');
const cols = (c) => c.map((x) => `\`${x.key}\`${x.type ? `:${x.type}` : ''}`).join(', ');

function resource(r) {
	const L = [];
	L.push(`### \`${r.key}\` — ${r.scope === 'admin' ? 'Kafintech' : 'client'}${r.exportable ? ' · exportable' : ''}`);
	L.push(`- **List**: \`GET ${r.endpoint}\` — permission \`${r.read}\`. Query: \`page\`, \`page_size\`${(r.filters ?? []).map((f) => (f.type === 'range' ? `, \`${f.key}_from\`, \`${f.key}_to\`` : `, \`${f.key}\`${f.options ? ` (${f.options.join('|')})` : ''}`)).join('')}. Response: array **or** \`{items,total}\`.`);
	L.push(`- **Row fields** (columns): ${cols(r.cols)}. id is required on every row.`);
	if (r.detail) {
		L.push(`- **Detail**: \`GET ${r.endpoint}/{id}\`${r.detailHref ? ` (UI page: \`${r.detailHref}\`)` : ''}. Fields shown: ${r.detail.sections.flatMap((s) => s.fields.map((f) => `\`${f.key}\``)).join(', ')}.`);
		for (const rel of r.detail.related ?? []) L.push(`  - **Related** \`${rel.key}\`: \`GET ${rel.path}\` → rows with ${cols(rel.cols)}`);
	}
	if (r.create) { L.push(`- **Create**: \`POST ${r.create.path ?? r.endpoint}\` — permission \`${r.create.permission}\`${r.create.fields.some((f) => f.type === 'file' || f.type === 'repeater') ? ' — **multipart/form-data**: payload (JSON) + file parts' : ' — JSON'}. Returns the created object (id).`); L.push(...r.create.fields.map((f) => field(f, '  '))); }
	if (r.edit) L.push(`- **Edit**: \`PATCH ${r.endpoint}/{id}\` (same fields, all optional; secrets left empty are unchanged).`);
	for (const a of r.actions ?? []) {
		L.push(`- **Action \`${a.id}\`**: \`${a.method} ${a.path}\` — permission \`${a.permission}\`${a.reason ? ' · body includes reason (**required**, store in audit)' : ''}${a.critical ? ' · **critical**: header X-Step-Up-Code (TOTP) must be validated' : ''}${a.when ? ` · shown when \`${a.when.key}\` ∈ ${a.when.in.join('|')} (enforce the same rule server-side)` : ''}`);
		if (a.fields?.length) L.push(...a.fields.map((f) => field(f, '  ')));
	}
	if (r.exportable) L.push(`- **Export**: \`GET ${r.endpoint}/export?format=csv|xlsx|pdf\` + the same filters as the list. Binary response with \`Content-Disposition\`.`);
	return L.join('\n');
}

const matrix = ['super_admin', ...STAFF_ROLES.filter((r) => r !== 'super_admin'), ...CLIENT_ROLES].map((r) => `| \`${r}\` | ${permissionsOf(r).map((p) => `\`${p}\``).join(' ')} |`).join('\n');

const md = `# IZI LENS — Front-end contract

> **Generated** by \`npm run contract\` from \`src/lib/config/*.ts\`. The dashboard is complete and already built against this contract:
> implement these endpoints and every screen fills in. Until an endpoint exists (HTTP 404/501) the screen shows a “module not connected yet” notice, never a crash.
> Paths are relative to \`BACKEND_API_PREFIX\` (default \`/api/v1\`).

## 1. Conventions

| Topic | Rule |
|---|---|
| Auth | \`Authorization: Bearer <access JWT>\`. The browser never sees tokens (httpOnly cookies in the SvelteKit server). |
| Environment | Client calls send \`X-IZI-Environment: sandbox\\|production\`. Sandbox operations are **never billed**. Keys, data and webhooks of both environments are separated. |
| Errors | JSON \`{detail: string \\| [{msg}]}\`. 401 → re-login · 403 → forbidden · 404/501 → “module not connected” · 409 → conflict (e.g. case already decided) · 422 → validation. |
| Pagination | \`page\` (1-based) + \`page_size\`. Respond with \`{items, total}\` (preferred) or a plain array. |
| Sensitive actions | Body field \`reason\` (stored in the audit log with actor, IP, request id, result). **Critical** actions also require header \`X-Step-Up-Code\` = current TOTP code → 403 if wrong. |
| Multipart | When a form has files: \`payload\` = JSON string of all non-file fields; each file is a part named by its field path (repeaters: \`documents[1][file]\`). |
| Secrets | API keys and provider secrets are returned in clear **once** (creation) and never again. Config GET returns \`<name>_set: true\` instead of a secret. |
| Dates | ISO 8601 UTC. Money: numbers in the major unit of \`currency\` (ISO 4217: CAD, USD, EUR, XOF, XAF, GBP — **XOF and XAF are distinct**). |
| Backend is the authority | Permissions below are enforced in the UI only for convenience; enforce them server-side. |

## 2. Roles & permissions

Staff roles (space \`/admin\`, MFA **mandatory**) and client roles (space \`/app\`). Clients have **no administrator role**: they submit, consult, pay, leave. All manual-review decisions belong to Kafintech staff. Legacy roles are mapped: \`admin\`,\`reviewer\`→\`client\`, \`viewer\`→\`client_readonly\`.

| Role | Permissions (default matrix; editable via \`PUT /admin/roles/{role}\`) |
|---|---|
${matrix}

\`GET /auth/me\` must return: \`id, email, full_name, role, organization_id, is_active, mfa_enabled, last_login_at\` (+ \`organization\` for clients: \`id, name, slug, enabled_modules (list of kyc, kyb, biometrics, monitoring, api), plan, currency, country, production_enabled\`).

## 3. Authentication endpoints

| Route | Body → Response |
|---|---|
| \`POST /auth/login\` | \`{email,password}\` (or form \`username,password\`) → \`{access_token,refresh_token}\` **or** \`{mfa_required:true, mfa_token}\` (short-lived) |
| \`POST /auth/mfa/verify\` | \`{mfa_token, code}\` (TOTP or recovery code) → tokens |
| \`POST /auth/refresh\`, \`POST /auth/logout\`, \`POST /auth/register\`, \`POST /auth/change-password\` | see README |
| \`POST /auth/oauth/google\` | \`{id_token, nonce}\` → tokens or MFA challenge |
| \`POST /auth/mfa/totp/setup\` | → \`{secret, otpauth_uri}\` |
| \`POST /auth/mfa/totp/confirm\` | \`{code}\` → \`{recovery_codes[]}\` (shown once) |
| \`POST /auth/mfa/disable\` | \`{code}\` (refused for staff) |
| \`POST /auth/passkeys/options\` | → WebAuthn creation options (JSON, base64url \`challenge\`, \`user.id\`, \`excludeCredentials[].id\`) |
| \`POST /auth/passkeys/verify\` | \`{id,rawId,type,response:{clientDataJSON,attestationObject}}\` (base64url) → passkey |
| \`GET /auth/passkeys\`, \`DELETE /auth/passkeys/{id}\` | list / remove |
| \`GET /auth/sessions\`, \`DELETE /auth/sessions/{id}\` | \`[{id,device,ip_address,last_seen_at,current}]\` |

## 4. Resources (generic list / detail / create / actions)

${[...ADMIN_RESOURCES, ...CLIENT_RESOURCES].map(resource).join('\n\n')}

## 5. Configuration pages

${Object.values(CONFIG_PAGES).map((p) => `### \`${p.key}\`\n- \`GET ${p.endpoint}\` → \`{values:{…}, status?:{…}}\` (or the values at the top level). \`PUT ${p.endpoint}\` — permission \`${p.write}\`, body = values + \`reason\`${p.critical ? ', header X-Step-Up-Code' : ''}. Versioned + audited.\n${p.sections.map((s) => `- **${s.key}**\n${s.fields.map((f) => field(f, '  ')).join('')}`).join('')}${p.key === 'providers' ? '- \`GET\` also returns \`status.{ocr,bio,aml,cloud}: {available, errors_24h, latency_ms, cost_30d, currency}\`.\n' : ''}`).join('\n')}

## 6. Dedicated endpoints

### Global dashboard — \`GET /admin/dashboard?range=today|7d|30d|90d|custom&from&to&country&service&client_id\` (\`adm:dashboard\`)
\`\`\`json
{ "clients":   {"total":0,"active":0,"new":0,"suspended":0,"pending_validation":0},
  "kyc":       {"total":0,"approved":0,"rejected":0,"pending":0,"manual_review":0},
  "kyb":       {"received":0,"approved":0,"rejected":0,"in_progress":0},
  "biometrics":{"sessions":0,"passed":0,"failed":0,"needs_review":0},
  "financial": {"currency":"CAD","revenue_month":0,"revenue_total":0,"active_subscriptions":0,"billable_consumption":0,"unpaid_invoices":0,"payments_received":0},
  "technical": {"availability_percent":99.9,"api_errors":0,"latency_ms":0,"providers":[{"name":"ocr","status":"active","latency_ms":0}],"alerts":[{"level":"high","message":""}]},
  "series":    {"daily":[{"date":"2026-11-01","kyc":0,"kyb":0,"biometrics":0}]} }
\`\`\`
Numeric keys under each block are rendered automatically (label = \`rx.f.<key>\`), so extra keys appear without front-end change.

### Pricing — \`GET|PUT /admin/pricing\`, \`GET /admin/pricing/history\` (\`adm:billing\` / \`adm:pricing:write\` + step-up + \`reason\`)
\`\`\`json
{ "version":"v3","effective_from":"2026-12-01","currencies":["CAD","USD","EUR","XOF","XAF","GBP"],
  "plans":{ "starter":{"monthly":{"CAD":0},"annual":{"CAD":0}}, "business":{"monthly":{},"annual":{}},
            "enterprise":{"monthly":{},"annual":{},"minimum_commitment":{"CAD":0}} },
  "usage":{"kyc":{"CAD":0},"kyb":{"CAD":0},"biometrics":{"CAD":0}},
  "options":{"monitoring_monthly":{"CAD":0}},
  "integration_fee":{"enabled":true,"amounts":{"CAD":0}} }
\`\`\`
\`PUT\` accepts the same shape (+ \`effective_from\`, \`reason\`) and **creates a new version**; it must never alter invoices already issued. History rows: \`version, effective_from, created_at, author, reason\`.

### Roles — \`GET /admin/roles\` → \`[{role, permissions[]}]\`; \`PUT /admin/roles/{role}\` \`{permissions[], reason}\` + step-up. \`super_admin\` is immutable.
### Infrastructure — \`GET /admin/infrastructure\` (\`adm:infra\`) read-only
\`{overall_status:"operational|degraded|down", cpu_percent, memory_percent, storage:{used_gb,total_gb}, network:{in_mbps,out_mbps}, services:[{name,status,latency_ms,uptime_percent}], databases:[{name,status,connections}], backups:[{name,last_success_at,status}], incidents:[{title,status,started_at}], capacity_alerts:[{level,message}], generated_at}\`
### Security overview — \`GET /admin/security/overview\` → \`{failed_logins_24h, suspicious_logins_24h, active_sessions, open_alerts, sensitive_access_24h, mfa_coverage_percent}\`
### Reports — \`GET /admin/reports/{id}/export?format=pdf|csv|xlsx&from&to&country&client_id\` (\`adm:reports\`). Ids: ${REPORTS.map((r) => `\`${r}\``).join(', ')}.
### Admin KYC review — \`GET /admin/kyc/cases/{id}\` (case + \`documents[]\` + \`client_name\`), \`GET …/history\`, \`GET …/documents/{doc}/content\` (image), \`POST …/decision\` \`{decision:"approved|rejected|request_new", reason, evidence}\` (\`adm:kyc:review\`; 409 if already decided). A human decision stores agent identity, date, reason and evidence.
### Client billing summary — \`GET /billing/summary\`
\`{plan, billing_cycle, currency, period, next_invoice_at, subscription_amount, usage:{kyc:{count,amount},kyb:{…},biometrics:{…}}, monitoring_amount, integration_fee, discount, minimum_applied, total_due}\`. Invoices: \`GET /billing/invoices\` (+ \`pdf_url\`), payments, usage (resources above).
### Client developer portal
- \`GET /developers/access\` → \`{status:"none|pending|approved|rejected", sandbox:true, production:false, services[], decision_reason}\`
- \`POST /developers/access-requests\` \`{organization_name, project, services[], intended_use, technical_info}\` — creating an account/request **never** activates production by itself; Kafintech validates manually (admin action \`approve\`).
- \`GET /developers/keys?environment=\`, \`POST /developers/keys\` \`{name, environment, expires_in_days?}\` → \`{id, prefix, key}\` (key shown once), \`DELETE /developers/keys/{id}\`. Production keys only after approval.
### Biometrics (client) — \`POST /biometrics/sessions\` \`{case_reference?}\` → \`{token, expires_in_minutes}\`; public mobile flow posts frames to \`POST /biometrics/sessions/{token}/frames\` \`{frames:[dataURL]}\`; \`GET|PATCH /biometrics/settings\` \`{trigger_level:"off|medium|high"}\`.
### Public requests (website forms) — \`POST /public/contact-requests\` (**unauthenticated**, rate-limited, CORS closed)
\`{kind:"contact|demo", locale, fields:{full_name,company,email,country,role,type,subject,message,phone,sector,volume,services[],consent_privacy:true,consent_marketing}}\` → \`{reference}\`. Required behaviour: persist, send the confirmation e-mail to the sender, e-mail the relevant department (routing: sales/demo/quote → Sales; partnership → Partnerships; others by category), status \`new\`. **Technical support is never created from this form** (customer portal only).

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
\`verification.created\`, \`verification.started\`, \`document.submitted\`, \`verification.completed\`, \`result.available\`, \`verification.needs_review\`. Each delivery is signed (HMAC, per-webhook secret, rotatable) and logged (\`deliveries\`: created_at, event, status_code, attempts, status) with retries.

## 9. Audit log requirements
Every sensitive operation writes an append-only event: actor (user/api_key/system), action, resource type + id, result (success|failure|denied), IP, request id, timestamp, details. Includes: account create/delete, permission changes, client suspend/activate, tariff changes, configuration changes, sensitive data access, billing actions, security actions, integration changes. Protect against modification.

## 10. Notifications (internal)
Categories: new_verification, pending_case, review_needed, technical_failure, api_incident, risk_alert, unpaid_invoice, payment_issue, provider_down. Email delivery configurable in \`settings\` (\`email_alerts\`, \`alert_recipients\`).
`;
writeFileSync('docs/FRONTEND_CONTRACT.md', md);
console.log('docs/FRONTEND_CONTRACT.md :', md.split('\n').length, 'lignes');
