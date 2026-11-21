import { authConfig } from '$lib/server/auth/config';
import { backendBase, backendRequest } from '$lib/server/backend';
import { EP } from '$lib/server/endpoints';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async () => {
	const res = await backendRequest(EP.health).catch(() => null);
	return { healthy: !!res?.ok, baseUrl: backendBase(), oidc: authConfig.googleConfigured, loginFormat: authConfig.loginFormat };
};
