import { fail, redirect } from '@sveltejs/kit';
import { actionError, createApi } from '$lib/server/api';
import { EP } from '$lib/server/endpoints';
import { requirePermission } from '$lib/server/guards';
import type { Actions, PageServerLoad } from './$types';

const MAX = 8 * 1024 * 1024;

export const load: PageServerLoad = (event) => {
	requirePermission(event, 'cases:create');
	return {};
};

export const actions: Actions = {
	default: async (event) => {
		requirePermission(event, 'cases:create');
		const d = await event.request.formData();
		const front = d.get('front');
		const back = d.get('back');
		const reference = String(d.get('reference') ?? '').trim();

		if (!(front instanceof File) || front.size === 0) return fail(400, { ok: false, message: 'verifications.upload.fileRequired' });
		if (front.size > MAX || (back instanceof File && back.size > MAX)) return fail(413, { ok: false, message: 'verifications.upload.sizeHint' });

		const out = new FormData();
		out.set('document_type', String(d.get('document_type') ?? 'cni_cm'));
		if (reference) out.set('reference', reference);
		out.set('front', front, front.name);
		if (back instanceof File && back.size > 0) out.set('back', back, back.name);

		let id: string | undefined;
		try {
			const created = await createApi(event).postForm<{ id?: string }>(EP.kyc.cases, out);
			id = created?.id;
		} catch (e) {
			const err = actionError(e);
			return fail(err.status >= 400 && err.status < 600 ? err.status : 500, { ok: false, message: err.message });
		}
		redirect(303, id ? `/app/verifications/${id}` : '/app/verifications');
	}
};
