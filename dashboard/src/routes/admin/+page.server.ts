import { createApi } from '$lib/server/api';
import { EPX } from '$lib/server/endpoints';
import { requirePermission } from '$lib/server/guards';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async (event) => {
	requirePermission(event, 'adm:dashboard');
	const sp = event.url.searchParams;
	const query = { range: sp.get('range') ?? '30d', from: sp.get('from') ?? undefined, to: sp.get('to') ?? undefined, country: sp.get('country') ?? undefined, service: sp.get('service') ?? undefined, client_id: sp.get('client_id') ?? undefined };
	try {
		return { dash: await createApi(event).get<any>(EPX.admin.dashboard, query), unavailable: false, query };
	} catch (e: any) {
		if (e?.status === 404 || e?.status === 501) return { dash: null, unavailable: true, query };
		throw e;
	}
};
