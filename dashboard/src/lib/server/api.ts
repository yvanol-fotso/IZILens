import { error, redirect, type RequestEvent } from '@sveltejs/kit';
import { BackendError, backendJson, type RequestOptions } from './backend';
import type { Paged } from '$lib/types';

type Ev = Pick<RequestEvent, 'locals' | 'url'>;

/** Convertit une erreur backend en réponse SvelteKit appropriée. */
export function toKitError(e: unknown, url?: URL): never {
	if (e instanceof BackendError) {
		if (e.status === 401) redirect(303, `/login?error=session${url ? `&next=${encodeURIComponent(url.pathname)}` : ''}`);
		if (e.status === 403) error(403, { message: e.detail, code: 'forbidden' });
		if (e.status === 404) error(404, { message: e.detail, code: 'not_found' });
		if (e.status === 503) error(503, { message: 'backend_unreachable', code: 'backend_unreachable' });
		error(e.status >= 400 && e.status < 600 ? e.status : 500, { message: e.detail });
	}
	throw e;
}

/** Retire les valeurs vides et accepte les deux formes de pagination : tableau ou {items,total}. */
export function toPaged<T>(raw: unknown, page: number, pageSize: number, filter?: (item: T) => boolean): Paged<T> {
	if (Array.isArray(raw)) {
		const all = filter ? (raw as T[]).filter(filter) : (raw as T[]);
		const sliced = all.length > pageSize ? all.slice((page - 1) * pageSize, page * pageSize) : all;
		return { items: sliced, total: all.length, page, pageSize };
	}
	const o = (raw ?? {}) as Record<string, any>;
	const items: T[] = o.items ?? o.results ?? o.data ?? [];
	return { items, total: o.total ?? o.count ?? items.length, page, pageSize };
}

export function toList<T>(raw: unknown): T[] {
	if (Array.isArray(raw)) return raw as T[];
	const o = (raw ?? {}) as Record<string, any>;
	return (o.items ?? o.results ?? o.data ?? []) as T[];
}

/** Client backend lié à la session de la requête courante (jeton jamais exposé au navigateur). */
export function createApi(event: Ev) {
	const token = event.locals.accessToken;

	async function call<T>(path: string, opts: RequestOptions = {}): Promise<T> {
		try {
			return await backendJson<T>(path, { ...opts, token });
		} catch (e) {
			toKitError(e, event.url);
		}
	}

	return {
		get: <T>(path: string, query?: RequestOptions['query']) => call<T>(path, { query }),
		post: <T>(path: string, json?: unknown) => call<T>(path, { method: 'POST', json: json ?? {} }),
		postForm: <T>(path: string, form: FormData) => call<T>(path, { method: 'POST', form }),
		patch: <T>(path: string, json: unknown) => call<T>(path, { method: 'PATCH', json }),
		del: <T>(path: string) => call<T>(path, { method: 'DELETE' }),
		paged: async <T>(path: string, query: Record<string, any>, page: number, pageSize: number, filter?: (i: T) => boolean) =>
			toPaged<T>(await call<unknown>(path, { query: { ...query, page, page_size: pageSize } }), page, pageSize, filter),
		list: async <T>(path: string, query?: RequestOptions['query']) => toList<T>(await call<unknown>(path, { query })),
		/** Valeur de repli si le module/endpoint n'existe pas encore. */
		safe: async <T>(promise: Promise<T>, fallback: T): Promise<T> => {
			try {
				return await promise;
			} catch {
				return fallback;
			}
		}
	};
}

export type Api = ReturnType<typeof createApi>;

/** Pour les form actions : renvoie un message d'erreur sans lever. */
export function actionError(e: unknown): { status: number; message: string } {
	if (e instanceof BackendError) return { status: e.status, message: e.detail };
	if (e && typeof e === 'object' && 'body' in e) {
		const b = (e as any).body;
		return { status: (e as any).status ?? 500, message: b?.message ?? 'error' };
	}
	return { status: 500, message: 'error' };
}
