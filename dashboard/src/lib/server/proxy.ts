import { json, type RequestEvent } from '@sveltejs/kit';
import { backendUrl } from './backend';

const HOP_BY_HOP = ['connection', 'keep-alive', 'transfer-encoding', 'content-encoding', 'content-length', 'set-cookie'];

interface ProxyOptions {
	/** Préfixe côté backend (après BACKEND_API_PREFIX). */
	target: string;
	/** Chemins interdits (regex sur le sous-chemin). */
	deny?: RegExp[];
}

/**
 * Proxy générique navigateur → backend : ajoute le Bearer depuis le cookie httpOnly,
 * le navigateur ne voit jamais le jeton.
 */
export async function proxyToBackend(event: RequestEvent, { target, deny = [] }: ProxyOptions): Promise<Response> {
	const { request, url, locals } = event;
	const sub = (event.params.path ?? '').replace(/^\/+/, '');
	if (!locals.accessToken) return json({ detail: 'Unauthorized' }, { status: 401 });
	if (sub.split('/').includes('..') || deny.some((r) => r.test(sub))) return json({ detail: 'Forbidden' }, { status: 403 });

	const headers = new Headers();
	for (const h of ['content-type', 'accept', 'accept-language']) {
		const v = request.headers.get(h);
		if (v) headers.set(h, v);
	}
	headers.set('authorization', `Bearer ${locals.accessToken}`);

	const hasBody = !['GET', 'HEAD'].includes(request.method);
	let upstream: Response;
	try {
		upstream = await fetch(backendUrl(`${target}/${sub}`) + url.search, {
			method: request.method,
			headers,
			body: hasBody ? await request.arrayBuffer() : undefined
		});
	} catch {
		return json({ detail: 'backend_unreachable' }, { status: 503 });
	}

	const out = new Headers();
	upstream.headers.forEach((v, k) => {
		if (!HOP_BY_HOP.includes(k.toLowerCase())) out.set(k, v);
	});
	out.set('cache-control', 'private, no-store');
	return new Response(upstream.body, { status: upstream.status, headers: out });
}
