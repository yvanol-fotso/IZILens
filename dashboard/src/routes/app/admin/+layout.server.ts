import { requireSuperAdmin } from '$lib/server/guards';
import type { LayoutServerLoad } from './$types';

/** Double verrou : hooks.server.ts redirige déjà, ceci protège aussi les appels de données directs. */
export const load: LayoutServerLoad = (event) => {
	requireSuperAdmin(event);
	return {};
};
