import { fail } from '@sveltejs/kit';
import { PRICING_CURRENCIES } from '$lib/config/admin-config';
import { can } from '$lib/config/permissions';
import { actionError, createApi } from '$lib/server/api';
import { backendJson } from '$lib/server/backend';
import { EPX } from '$lib/server/endpoints';
import { requirePermission } from '$lib/server/guards';
import type { Actions, PageServerLoad } from './$types';

export const load: PageServerLoad = async (event) => {
	requirePermission(event, 'adm:billing');
	const api = createApi(event);
	let pricing: any = null;
	let unavailable = false;
	try { pricing = await api.get<any>(EPX.admin.pricing); } catch (e: any) { if (e?.status === 404 || e?.status === 501) unavailable = true; else throw e; }
	const history = await api.safe(api.list<any>(EPX.admin.pricingHistory), []);
	return { pricing, history, unavailable, currencies: pricing?.currencies ?? PRICING_CURRENCIES };
};

/** `plans.starter.monthly.CAD` → objet imbriqué. */
function nest(entries: [string, string][]) {
	const out: Record<string, any> = {};
	for (const [k, v] of entries) {
		if (!k.startsWith('p:')) continue;
		const parts = k.slice(2).split('.');
		let cur = out;
		for (let i = 0; i < parts.length - 1; i++) cur = cur[parts[i]] ??= {};
		if (v !== '') cur[parts.at(-1)!] = Number(v);
	}
	return out;
}

export const actions: Actions = {
	save: async (event) => {
		requirePermission(event, 'adm:pricing:write');
		const fd = await event.request.formData();
		const body = nest([...fd.entries()].map(([k, v]) => [k, String(v)]));
		body.integration_fee = { ...(body.integration_fee ?? {}), enabled: fd.get('integration_enabled') === 'on' };
		body.effective_from = String(fd.get('effective_from') ?? '') || undefined;
		const reason = String(fd.get('reason') ?? '').trim();
		const code = String(fd.get('step_up_code') ?? '').trim();
		const errors: Record<string, string> = {};
		if (!reason) errors.reason = 'contact.errors.required';
		if (!/^\d{6}$/.test(code)) errors.step_up_code = 'auth.errors.required';
		if (Object.keys(errors).length) return fail(400, { ok: false, errors });
		try {
			// Crée une NOUVELLE version : les factures déjà émises ne sont jamais modifiées.
			await backendJson(EPX.admin.pricing, { method: 'PUT', token: event.locals.accessToken, json: { ...body, reason }, headers: { 'x-step-up-code': code } });
		} catch (e) { return fail(400, { ok: false, message: actionError(e).message }); }
		return { ok: true };
	}
};
void can;
