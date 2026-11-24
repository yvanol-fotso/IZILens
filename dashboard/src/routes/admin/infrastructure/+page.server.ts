import { createApi } from '$lib/server/api';
import { EPX } from '$lib/server/endpoints';
import { requirePermission } from '$lib/server/guards';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async (event) => {
	requirePermission(event, 'adm:infra');
	try { return { infra: await createApi(event).get<any>(EPX.admin.infra), unavailable: false }; }
	catch (e: any) { if (e?.status === 404 || e?.status === 501) return { infra: null, unavailable: true }; throw e; }
};
