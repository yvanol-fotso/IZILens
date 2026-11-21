import { backendBase, apiPrefix, backendRequest } from '$lib/server/backend';
import { EP } from '$lib/server/endpoints';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ url }) => {
	const res = await backendRequest(EP.health).catch(() => null);
	return { healthy: !!res?.ok, apiBase: `${backendBase()}${apiPrefix()}`, origin: url.origin };
};
