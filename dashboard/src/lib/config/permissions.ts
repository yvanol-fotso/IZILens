import type { Role } from '$lib/types';

const PERMISSIONS = [
	// Existantes
	'cases:read',
	'cases:create',
	'cases:decide',
	'keys:manage',
	'users:manage',
	'audit:read',
	'settings:write',
	'liveness:manage',
	'admin:access',
	// Client
	'kyb:read',
	'kyb:create',
	'monitoring:read',
	'biometrics:use',
	'support:use',
	'billing:read',
	'developers:manage',
	// Admin
	'adm:dashboard',
	'adm:infra',
	'adm:kyc',
	'adm:kyc:review',
	'adm:billing',
	'adm:billing:write',
	'adm:pricing:write',
	'adm:api',
	'adm:api:write',
	'adm:staff',
	'adm:roles',
	'adm:security',
	'adm:security:write',
	'adm:audit',
	'adm:notifications',
	'adm:requests',
	'adm:support',
	'adm:content',
	'adm:platform',
	'adm:settings',
	'adm:providers',
	'adm:reports'
] as const;

export type Permission = (typeof PERMISSIONS)[number];

export const ALL_PERMISSIONS: Permission[] = [...PERMISSIONS];

const CLIENT_ALL: Permission[] = [
	'cases:read', 'cases:create', 'cases:decide', 'keys:manage', 'users:manage',
	'audit:read', 'settings:write', 'liveness:manage',
	'kyb:read', 'kyb:create', 'monitoring:read', 'biometrics:use', 'support:use',
	'billing:read', 'developers:manage'
];

const MATRIX: Record<Role, Permission[]> = {
	// super_admin : tout, y compris l'espace admin
	super_admin: ALL_PERMISSIONS,
	admin: CLIENT_ALL,
	reviewer: ['cases:read', 'cases:decide', 'liveness:manage'],
	viewer: ['cases:read'],
	integration: ['cases:read', 'cases:create']
};

export function can(role: Role | undefined | null, permission: Permission): boolean {
	return !!role && !!MATRIX[role]?.includes(permission);
}

export const ASSIGNABLE_ROLES: Role[] = ['admin', 'reviewer', 'viewer', 'integration'];

// Rôles du personnel (utilisés par la page admin/roles)
export const STAFF_ROLES: string[] = [
	'super_admin',
	'platform_admin',
	'compliance_officer',
	'kyc_analyst',
	'risk_officer',
	'finance_manager',
	'support_agent',
	'tech_admin',
	'read_only'
];

// Permissions par défaut d'un rôle (vide si le rôle n'est pas dans la matrice)
export const permissionsOf = (role: string): Permission[] =>
	(MATRIX as Record<string, Permission[]>)[role] ?? [];