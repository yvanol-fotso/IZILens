import { error, fail, type RequestEvent } from '@sveltejs/kit';
import { can } from '$lib/config/permissions';
import type { ConfigPage } from '$lib/config/admin-config';
import { createApi, actionError } from './api';
import { requirePermission } from './guards';
import { backendJson } from './backend';
import { bodyFor, parseFields } from './resource';

type Ev = RequestEvent<any, any>;

export async function loadConfig(event: Ev, page: ConfigPage) {
	requirePermission(event, page.read);
	const api = createApi(event);
	try {
		const raw = await api.get<Record<string, any>>(page.endpoint);
		const { status, ...values } = raw as Record<string, any>;
		return { unavailable: false, values: (raw.values ?? values) as Record<string, any>, status: (raw.status ?? {}) as Record<string, any> };
	} catch (e: any) {
		if (e?.status === 404 || e?.status === 501) return { unavailable: true, values: {}, status: {} };
		throw e;
	}
}

export async function saveConfig(event: Ev, page: ConfigPage) {
	const user = requirePermission(event, page.write);
	if (!can(user.role, page.write)) error(403, { message: 'forbidden' });
	const fd = await event.request.formData();
	const fields = page.sections.flatMap((s) => s.fields).map((f) => ({ ...f, required: false }));
	const parsed = parseFields(fd, fields);
	// Un secret laissé vide n'est pas envoyé (inchangé côté backend).
	for (const f of fields) if (f.secret && !parsed.values[f.name]) delete parsed.values[f.name];
	const reason = String(fd.get('reason') ?? '').trim();
	const code = String(fd.get('step_up_code') ?? '').trim();
	const errors: Record<string, string> = { ...parsed.errors };
	if (!reason) errors.reason = 'contact.errors.required';
	if (page.critical && !/^\d{6}$/.test(code)) errors.step_up_code = 'auth.errors.required';
	if (Object.keys(errors).length) return fail(400, { ok: false, errors });
	try {
		await backendJson(page.endpoint, { method: 'PUT', token: event.locals.accessToken, ...bodyFor({ ...parsed.values, reason }, parsed.files), headers: { ...(page.critical ? { 'x-step-up-code': code } : {}) } });
		return { ok: true };
	} catch (e) {
		return fail(400, { ok: false, message: actionError(e).message });
	}
}
