import { createApi } from '$lib/server/api';
import { toOrganization } from '$lib/server/auth/service';
import { EP } from '$lib/server/endpoints';
import type { AuditLog, UserRecord } from '$lib/types';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async (event) => {
	const api = createApi(event);
	const [orgsRaw, members, audit] = await Promise.all([
		api.list<any>(EP.org.list),
		api.safe(api.list<UserRecord>(EP.users.list), []),
		api.safe(api.list<AuditLog>(EP.audit, { page_size: 8, limit: 8 }), [])
	]);
	const orgs = orgsRaw.map(toOrganization).filter(Boolean);
	return { orgCount: orgs.length, activeOrgs: orgs.filter((o) => o!.is_active).length, memberCount: members.length, audit: audit.slice(0, 8) };
};
