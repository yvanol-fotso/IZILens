import { createApi } from '$lib/server/api';
import { toOrganization } from '$lib/server/auth/service';
import { EP } from '$lib/server/endpoints';
import type { UserRecord } from '$lib/types';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async (event) => {
	const api = createApi(event);
	const [members, orgs] = await Promise.all([api.list<UserRecord>(EP.users.list), api.safe(api.list<any>(EP.org.list), [])]);
	const orgNames = Object.fromEntries(orgs.map(toOrganization).filter(Boolean).map((o) => [o!.id, o!.name]));
	return { members, orgNames };
};
