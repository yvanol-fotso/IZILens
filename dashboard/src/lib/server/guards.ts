import { error, redirect, type RequestEvent } from '@sveltejs/kit';
import { can, type Permission } from '$lib/config/permissions';

type GuardEvent = Pick<RequestEvent, 'locals' | 'url'>;

export function requireUser(event: GuardEvent) {
	if (!event.locals.user) redirect(303, `/login?next=${encodeURIComponent(event.url.pathname)}`);
	return event.locals.user;
}

export function requirePermission(event: GuardEvent, permission: Permission) {
	const user = requireUser(event);
	if (!can(user.role, permission)) error(403, { message: 'forbidden', code: 'forbidden' });
	return user;
}

export const requireSuperAdmin = (event: GuardEvent) => requirePermission(event, 'admin:access');


export const requireStaff = (event: GuardEvent) => requirePermission(event, 'admin:access');