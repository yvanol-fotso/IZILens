import { dev } from '$app/environment';
import { randomBytes } from 'node:crypto';
import { BackendError, backendJson } from './backend';
import { EP } from './endpoints';

export type RequestKind = 'contact' | 'demo';
export interface ContactPayload { kind: RequestKind; locale: string; fields: Record<string, unknown> }

const hits = new Map<string, number[]>();
/** Limiteur en mémoire : 5 envois / 10 min / IP (un seul process — Redis en production multi-instances). */
export function rateLimited(ip: string, max = 5, windowMs = 10 * 60_000): boolean {
	const now = Date.now();
	const list = (hits.get(ip) ?? []).filter((t) => now - t < windowMs);
	list.push(now);
	hits.set(ip, list);
	if (hits.size > 5000) hits.clear();
	return list.length > max;
}

const localReference = () => `IZI-${new Date().getFullYear()}-${randomBytes(3).toString('hex').toUpperCase()}`;

/**
 * Transmet la demande au back-office (POST /public/contact-requests → { reference }).
 * Tant que cette route n'existe pas : en développement on simule (référence locale, demande journalisée),
 * en production on renvoie une erreur plutôt que de prétendre qu'elle a été transmise.
 */
export async function submitContact(payload: ContactPayload): Promise<{ reference: string; simulated: boolean }> {
	try {
		const res = await backendJson<{ reference?: string }>(EP.public.contact, { method: 'POST', json: payload });
		return { reference: res.reference ?? localReference(), simulated: false };
	} catch (e) {
		if (dev && e instanceof BackendError && (e.status === 404 || e.status === 503)) {
			console.info('[contact:simulé]', JSON.stringify(payload));
			return { reference: localReference(), simulated: true };
		}
		throw e;
	}
}
