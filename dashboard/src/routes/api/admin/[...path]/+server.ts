import { json, type RequestHandler } from '@sveltejs/kit';
import { proxyToBackend } from '$lib/server/proxy';

/**
 * Proxy réservé au super_admin Kafintech : /api/admin/<x> → backend /api/v1/<x>
 * (organisations, membres, audit global…). Le backend reste l'autorité finale sur les droits.
 */
const handler: RequestHandler = (event) => {
	if (event.locals.user?.role !== 'super_admin') return json({ detail: 'Forbidden' }, { status: 403 });
	return proxyToBackend(event, { target: '', deny: [/^auth(\/|$)/] });
};

export const GET = handler;
export const POST = handler;
export const PUT = handler;
export const PATCH = handler;
export const DELETE = handler;
