import { env } from '$env/dynamic/private';

export class BackendError extends Error {
	constructor(
		public status: number,
		public detail: string,
		public data?: unknown
	) {
		super(detail);
	}
}

export const backendBase = () => (env.BACKEND_SERVICE_URL ?? 'http://127.0.0.1:8000').replace(/\/$/, '');
export const apiPrefix = () => env.BACKEND_API_PREFIX ?? '/api/v1';
export const backendUrl = (path: string) => `${backendBase()}${apiPrefix()}${path.startsWith('/') ? path : `/${path}`}`;

/** Extrait un message lisible des erreurs FastAPI ({detail: str | [{msg}] }). */
export function extractDetail(data: unknown, fallback: string): string {
	if (!data || typeof data !== 'object') return typeof data === 'string' && data ? data : fallback;
	const d = data as Record<string, any>;
	const v = d.detail ?? d.message ?? d.error;
	if (typeof v === 'string') return v;
	if (Array.isArray(v)) return v.map((x) => x?.msg ?? JSON.stringify(x)).join(', ');
	if (v && typeof v === 'object') return v.message ?? JSON.stringify(v);
	return fallback;
}

export interface RequestOptions {
	method?: string;
	token?: string | null;
	query?: Record<string, string | number | boolean | undefined | null>;
	json?: unknown;
	form?: FormData | URLSearchParams;
	headers?: Record<string, string>;
}

export async function backendRequest(path: string, opts: RequestOptions = {}): Promise<Response> {
	const url = new URL(backendUrl(path));
	for (const [k, v] of Object.entries(opts.query ?? {})) {
		if (v !== undefined && v !== null && v !== '') url.searchParams.set(k, String(v));
	}
	const headers = new Headers(opts.headers);
	if (opts.token) headers.set('authorization', `Bearer ${opts.token}`);
	headers.set('accept', headers.get('accept') ?? 'application/json');

	let body: BodyInit | undefined;
	if (opts.json !== undefined) {
		headers.set('content-type', 'application/json');
		body = JSON.stringify(opts.json);
	} else if (opts.form) {
		body = opts.form;
	}

	try {
		return await fetch(url, { method: opts.method ?? (body ? 'POST' : 'GET'), headers, body });
	} catch {
		throw new BackendError(503, 'backend_unreachable');
	}
}

export async function backendJson<T = unknown>(path: string, opts: RequestOptions = {}): Promise<T> {
	const res = await backendRequest(path, opts);
	const text = await res.text();
	let data: unknown = null;
	if (text) {
		try {
			data = JSON.parse(text);
		} catch {
			data = text;
		}
	}
	if (!res.ok) throw new BackendError(res.status, extractDetail(data, res.statusText), data);
	return data as T;
}
