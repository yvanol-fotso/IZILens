import { error, redirect, type RequestEvent } from '@sveltejs/kit';
import { can, type Permission } from '$lib/config/permissions';

export function requireUser(event: Pick<RequestEvent, 'locals' | 'url'>) {
	if (!event.locals.user) redirect(303, `/login?next=${encodeURIComponent(event.url.pathname)}`);
	return event.locals.user;
}

export function requirePermission(event: Pick<RequestEvent, 'locals' | 'url'>, permission: Permission) {
	const user = requireUser(event);
	if (!can(user.role, permission)) error(403, { message: 'forbidden', code: 'forbidden' });
	return user;
}

export const requireSuperAdmin = (event: Pick<RequestEvent, 'locals' | 'url'>) => requirePermission(event, 'admin:access');
