import type { Role } from '$lib/types';

export type Permission =
	| 'cases:read'
	| 'cases:create'
	| 'cases:decide'
	| 'keys:manage'
	| 'users:manage'
	| 'audit:read'
	| 'settings:write'
	| 'liveness:manage'
	| 'admin:access';

const MATRIX: Record<Role, Permission[]> = {
	super_admin: [
		'cases:read', 'cases:create', 'cases:decide', 'keys:manage', 'users:manage',
		'audit:read', 'settings:write', 'liveness:manage', 'admin:access'
	],
	admin: ['cases:read', 'cases:create', 'cases:decide', 'keys:manage', 'users:manage', 'audit:read', 'settings:write', 'liveness:manage'],
	reviewer: ['cases:read', 'cases:decide', 'liveness:manage'],
	viewer: ['cases:read'],
	integration: ['cases:read', 'cases:create']
};

export function can(role: Role | undefined | null, permission: Permission): boolean {
	return !!role && MATRIX[role]?.includes(permission);
}

export const ASSIGNABLE_ROLES: Role[] = ['admin', 'reviewer', 'viewer', 'integration'];
