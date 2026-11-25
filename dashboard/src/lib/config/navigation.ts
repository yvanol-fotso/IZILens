import type { Component } from 'svelte';
import {
	LayoutDashboard, FileCheck2, FilePlus2, ScanFace, Fingerprint, ShieldAlert, ChartColumn,
	KeyRound, Users, ScrollText, Settings, Code, Building2, Megaphone, Server, UserCog, Gauge
} from '@lucide/svelte';
import type { ModuleId, Role } from '$lib/types';
import { can, type Permission } from './permissions';

export interface NavItem {
	key: string; // clé i18n sous app.nav.*
	href: string;
	icon: Component<any>;
	permission?: Permission;
	module?: ModuleId;
	soon?: boolean;
	exact?: boolean;
}
export interface NavGroup {
	key: string; // clé i18n sous app.groups.*
	items: NavItem[];
}

/** Navigation du tableau de bord (utilisateur / organisation). */
export const appNav: NavGroup[] = [
	{
		key: 'main',
		items: [
			{ key: 'overview', href: '/app', icon: LayoutDashboard, exact: true },
			{ key: 'verifications', href: '/app/verifications', icon: FileCheck2, permission: 'cases:read', exact: true },
			{ key: 'newVerification', href: '/app/verifications/new', icon: FilePlus2, permission: 'cases:create' },
			{ key: 'analytics', href: '/app/analytics', icon: ChartColumn, permission: 'cases:read' }
		]
	},
	{
		key: 'modules',
		items: [
			{ key: 'liveness', href: '/app/liveness', icon: ScanFace, module: 'liveness', soon: true },
			{ key: 'biometrics', href: '/app/biometrics', icon: Fingerprint, module: 'biometrics', soon: true },
			{ key: 'aml', href: '/app/aml', icon: ShieldAlert, module: 'aml', soon: true }
		]
	},
	{
		key: 'workspace',
		items: [
			{ key: 'apiKeys', href: '/app/api-keys', icon: KeyRound, permission: 'keys:manage' },
			{ key: 'developers', href: '/app/developers', icon: Code },
			{ key: 'team', href: '/app/team', icon: Users, permission: 'users:manage' },
			{ key: 'audit', href: '/app/audit', icon: ScrollText, permission: 'audit:read' },
			{ key: 'settings', href: '/app/settings', icon: Settings }
		]
	}
];

/** Navigation de l'espace Kafintech (super_admin uniquement) — /app/admin/* */
export const adminNav: NavItem[] = [
	{ key: 'adminOverview', href: '/app/admin', icon: Gauge, exact: true },
	{ key: 'tenants', href: '/app/admin/tenants', icon: Building2 },
	{ key: 'members', href: '/app/admin/members', icon: UserCog },
	{ key: 'announcements', href: '/app/admin/announcements', icon: Megaphone, soon: true },
	{ key: 'system', href: '/app/admin/system', icon: Server }
];

/**
 * Filtre un menu selon les permissions de l'utilisateur.
 * Accepte une liste de groupes ou une liste plate d'éléments (alors regroupés dans un groupe « admin »).
 */
export function visibleGroups(
	nav: NavGroup[] | NavItem[],
	user?: { role?: Role | null } | null
): NavGroup[] {
	const groups: NavGroup[] =
		nav.length > 0 && 'items' in nav[0]
			? (nav as NavGroup[])
			: [{ key: 'admin', items: nav as NavItem[] }];

	return groups
		.map((g) => ({
			...g,
			items: g.items.filter((i) => !i.permission || can(user?.role, i.permission))
		}))
		.filter((g) => g.items.length > 0);
}

/** Navigation publique (clés sous nav.*). */
export interface MarketingLink { key: string; href: string; enabled: boolean }
export const marketingNav: MarketingLink[] = [
	{ key: 'solutions', href: '/solutions', enabled: true },
	{ key: 'developers', href: '/developers', enabled: true },
	{ key: 'resources', href: '/resources', enabled: true },
	{ key: 'about', href: '/about', enabled: true },
	{ key: 'contact', href: '/contact', enabled: true }
];

export type { Role };