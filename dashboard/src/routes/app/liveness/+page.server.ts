import { fail } from '@sveltejs/kit';
import { actionError, createApi } from '$lib/server/api';
import { EP } from '$lib/server/endpoints';
import { requirePermission } from '$lib/server/guards';
import type { Actions, PageServerLoad } from './$types';

export const load: PageServerLoad = async (event) => {
	requirePermission(event, 'liveness:manage');
	const api = createApi(event);
	const settings = await api.safe(api.get<{ trigger_level?: string }>(EP.liveness.settings), {});
	return { triggerLevel: settings.trigger_level ?? 'off' };
};

export const actions: Actions = {
	threshold: async (event) => {
		requirePermission(event, 'liveness:manage');
		const level = String((await event.request.formData()).get('trigger_level'));
		if (!['off', 'medium', 'high'].includes(level)) return fail(400, { ok: false, message: 'errors.generic' });
		try {
			await createApi(event).patch(EP.liveness.settings, { trigger_level: level });
		} catch (e) {
			return fail(400, { ok: false, message: actionError(e).message });
		}
		return { ok: true };
	}
};
