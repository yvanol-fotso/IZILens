import { fail } from '@sveltejs/kit';
import { actionError, createApi } from '$lib/server/api';
import { backendJson } from '$lib/server/backend';
import { EPX } from '$lib/server/endpoints';
import { requirePermission } from '$lib/server/guards';
import type { KycCase } from '$lib/types';
import type { Actions, PageServerLoad } from './$types';

export const load: PageServerLoad = async (event) => {
	requirePermission(event, 'adm:kyc');
	const api = createApi(event);
	const kyc = await api.get<KycCase & Record<string, any>>(EPX.admin.kyc(event.params.id));
	const history = await api.safe(api.list<any>(`${EPX.admin.kyc(event.params.id)}/history`), []);
	return { kyc, history };
};

export const actions: Actions = {
	decide: async (event) => {
		requirePermission(event, 'adm:kyc:review');
		const fd = await event.request.formData();
		const decision = String(fd.get('decision'));
		const reason = String(fd.get('reason') ?? '').trim();
		const evidence = String(fd.get('evidence') ?? '').trim();
		if (!['approved', 'rejected', 'request_new'].includes(decision)) return fail(400, { ok: false, message: 'errors.generic' });
		if (!reason) return fail(400, { ok: false, message: 'verifications.detail.reasonRequired' });
		try {
			// Décision humaine : identité de l'agent, date, motif et justificatifs conservés côté backend.
			await backendJson(EPX.admin.kycDecision(event.params.id), { method: 'POST', token: event.locals.accessToken, json: { decision, reason, evidence } });
		} catch (e) {
			const er = actionError(e);
			return fail(er.status === 409 ? 409 : 400, { ok: false, message: er.status === 409 ? 'verifications.detail.alreadyDecided' : er.message });
		}
		return { ok: true };
	}
};
