import { fail } from '@sveltejs/kit';
import { actionError, createApi } from '$lib/server/api';
import { EP } from '$lib/server/endpoints';
import { requirePermission } from '$lib/server/guards';
import type { KycCase } from '$lib/types';
import type { Actions, PageServerLoad } from './$types';

export const load: PageServerLoad = async (event) => {
	requirePermission(event, 'cases:read');
	const kyc = await createApi(event).get<KycCase>(EP.kyc.one(event.params.id));
	return { kyc };
};

export const actions: Actions = {
	decide: async (event) => {
		requirePermission(event, 'cases:decide');
		const d = await event.request.formData();
		const decision = String(d.get('decision'));
		const reason = String(d.get('reason') ?? '').trim();
		if (!['approved', 'rejected'].includes(decision)) return fail(400, { ok: false, message: 'errors.generic' });
		if (decision === 'rejected' && !reason) return fail(400, { ok: false, message: 'verifications.detail.reasonRequired' });
		try {
			await createApi(event).post(EP.kyc.decision(event.params.id), { decision, reason });
		} catch (e) {
			const err = actionError(e);
			return fail(err.status === 409 ? 409 : 400, { ok: false, message: err.status === 409 ? 'verifications.detail.alreadyDecided' : err.message });
		}
		return { ok: true };
	}
};
