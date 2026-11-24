import { fail } from '@sveltejs/kit';
import { BackendError } from '$lib/server/backend';
import { rateLimited, submitContact, type RequestKind } from '$lib/server/contact';
import type { Actions, PageServerLoad } from './$types';

const EMAIL = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
const TYPES = ['sales', 'demo', 'partnership', 'integration', 'institutional', 'quote', 'developer', 'other'];
const SERVICES = ['kyc', 'kyb', 'liveness', 'monitoring', 'api', 'other'];

export const load: PageServerLoad = ({ url }) => {
	const type = url.searchParams.get('type') ?? 'sales';
	return {
		preset: {
			type: TYPES.includes(type) ? type : 'sales',
			services: (url.searchParams.get('services') ?? '').split(',').filter((s) => SERVICES.includes(s))
		}
	};
};

async function handle(kind: RequestKind, { request, getClientAddress, locals }: Parameters<NonNullable<Actions['contact']>>[0]) {
	const d = await request.formData();
	const s = (k: string, max = 200) => String(d.get(k) ?? '').trim().slice(0, max);
	const values: Record<string, string> = { full_name: s('full_name'), company: s('company'), email: s('email').toLowerCase(), country: s('country'), role: s('role'), phone: s('phone', 40), type: s('type', 30), subject: s('subject', 200), sector: s('sector'), volume: s('volume', 40) };

	// Anti-spam : champ leurre rempli ⇒ robot ; limitation par IP
	if (s('website')) return fail(400, { ok: false, kind, message: 'contact.errors.spam', values });
	let ip = 'unknown';
	try { ip = getClientAddress(); } catch { /* derrière un proxy sans en-tête */ }
	if (rateLimited(ip)) return fail(429, { ok: false, kind, message: 'contact.errors.server', values });

	const body = s(kind === 'demo' ? 'project' : 'message', 4000);
	const errors: Record<string, string> = {};
	for (const k of ['full_name', 'company', 'country'] as const) if (!values[k]) errors[k] = 'contact.errors.required';
	if (!EMAIL.test(values.email)) errors.email = 'contact.errors.email';
	if (!body) errors[kind === 'demo' ? 'project' : 'message'] = 'contact.errors.required';
	if (kind === 'contact') {
		if (!values.role) errors.role = 'contact.errors.required';
		if (!values.subject) errors.subject = 'contact.errors.required';
	}
	if (d.get('consent') !== 'on') errors.consent = 'contact.errors.consent';
	if (Object.keys(errors).length) return fail(400, { ok: false, kind, errors, values });

	const services = d.getAll('services').map(String).filter((x) => SERVICES.includes(x));
	try {
		const { reference } = await submitContact({
			kind,
			locale: locals.locale,
			fields: { ...values, type: kind === 'demo' ? 'demo' : values.type, services, message: body, consent_privacy: true, consent_marketing: d.get('marketing') === 'on' }
		});
		return { ok: true, kind, reference };
	} catch (e) {
		if (e instanceof BackendError && e.status === 422) return fail(400, { ok: false, kind, message: 'contact.errors.required', values });
		return fail(503, { ok: false, kind, message: 'contact.errors.server', values });
	}
}

export const actions: Actions = {
	contact: (event) => handle('contact', event),
	demo: (event) => handle('demo', event)
};
