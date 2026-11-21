import type { Component } from 'svelte';
import {
	LayoutDashboard, FileCheck2, FilePlus2, ScanFace, Fingerprint, ShieldAlert, ChartColumn,
	KeyRound, Users, ScrollText, Settings, Code, Building2, Megaphone, Server, UserCog, Gauge,
	User, FileText, Cpu, Lock, Globe, Layers, Activity
} from '@lucide/svelte';
import type { ModuleId, Role } from '$lib/types';
import type { Permission } from './permissions';

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

/** Menu « Solutions » du site vitrine : clés sous solutions.items.* */
export interface SolutionLink { key: string; icon: Component<any>; href: string }
export const solutionGroups: { key: string; items: SolutionLink[] }[] = [
	{
		key: 'verification',
		items: [
			{ key: 'identity', icon: User, href: '/#platform' },
			{ key: 'document', icon: FileText, href: '/#platform' },
			{ key: 'biometric', icon: Fingerprint, href: '/#platform' },
			{ key: 'liveness', icon: ScanFace, href: '/#platform' }
		]
	},
	{
		key: 'compliance',
		items: [
			{ key: 'aml', icon: ShieldAlert, href: '/#platform' },
			{ key: 'sanctions', icon: Globe, href: '/#platform' },
			{ key: 'pep', icon: Users, href: '/#platform' },
			{ key: 'media', icon: FileText, href: '/#platform' }
		]
	},
	{
		key: 'platform',
		items: [
			{ key: 'api', icon: Cpu, href: '/#developers' },
			{ key: 'analytics', icon: Activity, href: '/#platform' },
			{ key: 'security', icon: Lock, href: '/privacy' },
			{ key: 'coverage', icon: Layers, href: '/#coverage' }
		]
	}
];

/**
 * Navigation publique. `enabled: false` = destination pas encore publiée : l'entrée n'est PAS rendue
 * (la spec interdit les liens « # » ou vides). Passez à true dès que la page existe.
 */
export interface MarketingLink { key: string; href: string; enabled: boolean; external?: boolean }
export const marketingNav: MarketingLink[] = [
	{ key: 'platform', href: '/#platform', enabled: true },
	{ key: 'industries', href: '/#industries', enabled: false },
	{ key: 'coverage', href: '/#coverage', enabled: true },
	{ key: 'why', href: '/#why', enabled: true },
	{ key: 'resources', href: '/resources', enabled: false },
	{ key: 'company', href: '/company', enabled: false }
];

/** Colonnes du pied de page. Sans `href` = simple texte (page non publiée). */
export const footerSolutions = [
	{ key: 'identity', href: '/#platform' },
	{ key: 'biometric', href: '/#platform' },
	{ key: 'kyb', href: '/#platform' },
	{ key: 'aml', href: '/#platform' },
	{ key: 'fraud', href: '/#why' },
	{ key: 'coverage', href: '/#coverage' }
] as { key: string; href?: string }[];

export const footerIndustries = ['financial', 'fintech', 'ecommerce', 'crypto', 'mobility', 'platforms'].map((key) => ({ key })) as { key: string; href?: string }[];

export type { Role };
