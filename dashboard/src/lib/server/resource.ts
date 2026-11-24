import { fail, error, type RequestEvent } from '@sveltejs/kit';
import { can } from '$lib/config/permissions';
import type { Action, Field, ResourceDef } from '$lib/config/resources';
import type { Paged } from '$lib/types';
import { createApi, actionError, toPaged } from './api';
import { BackendError, backendJson, type RequestOptions } from './backend';

type Ev = Pick<RequestEvent, 'locals' | 'url' | 'params'> & Partial<Pick<RequestEvent, 'request'>>;
export type Row = Record<string, any>;

export interface ListData { def: string; items: Row[]; total: number; page: number; pageSize: number; unavailable: boolean; filters: Record<string, string> }

const isMissing = (e: unknown) => e instanceof BackendError && [404, 405, 501].includes(e.status);

/** Charge une liste paginée. Si le module n'existe pas encore côté backend (404/501) : `unavailable`, pas d'erreur. */
export async function loadList(event: Ev, def: ResourceDef): Promise<ListData> {
	const sp = event.url.searchParams;
	const page = Math.max(1, Number(sp.get('page') || 1));
	const pageSize = def.pageSize ?? 20;
	const filters: Record<string, string> = {};
	const query: Record<string, string> = {};
	for (const f of def.filters ?? []) {
		if (f.type === 'range') {
			for (const k of [`${f.key}_from`, `${f.key}_to`]) { const v = sp.get(k); if (v) { filters[k] = v; query[k] = v; } }
		} else {
			const v = sp.get(f.key);
			if (v) { filters[f.key] = v; query[f.key] = v; }
		}
	}
	try {
		const res: Paged<Row> = await createApi(event as any).paged<Row>(def.endpoint, query, page, pageSize);
		return { def: def.key, items: res.items, total: res.total, page, pageSize, unavailable: false, filters };
	} catch (e: any) {
		if (e?.status === 404 || e?.status === 501) return { def: def.key, items: [], total: 0, page, pageSize, unavailable: true, filters };
		throw e;
	}
}

export async function loadDetail(event: Ev, def: ResourceDef, id: string) {
	const api = createApi(event as any);
	const row = await api.get<Row>(`${def.endpoint}/${id}`);
	const related: Record<string, Row[]> = {};
	if (def.detail) {
		await Promise.all(def.detail.related?.map(async (r) => {
			related[r.key] = await api.safe(api.list<Row>(r.path.replace('{id}', id)), []);
		}) ?? []);
	}
	return { row, related };
}

// ── Formulaires ─────────────────────────────────────────────────────────────
export interface Parsed { values: Record<string, any>; files: [string, File][]; errors: Record<string, string> }

function parseOne(fd: FormData, f: Field, key: string, out: Parsed, container: Record<string, any>) {
	const err = (m = 'contact.errors.required') => (out.errors[key] = m);
	if (f.type === 'file') {
		const list = fd.getAll(key).filter((x): x is File => x instanceof File && x.size > 0);
		if (f.required && !list.length) err();
		for (const file of list) out.files.push([key, file]);
		return;
	}
	if (f.type === 'multiselect') {
		const v = fd.getAll(key).map(String);
		if (f.required && !v.length) err();
		container[f.name] = v;
		return;
	}
	if (f.type === 'switch') { container[f.name] = fd.get(key) === 'on'; return; }
	const raw = String(fd.get(key) ?? '').trim();
	if (!raw) { if (f.required) err(); return; }
	if (f.type === 'number') {
		const n = Number(raw);
		if (Number.isNaN(n) || (f.min !== undefined && n < f.min) || (f.max !== undefined && n > f.max)) return err('auth.errors.generic');
		container[f.name] = n;
	} else if (f.type === 'email') {
		if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(raw)) return err('auth.errors.email');
		container[f.name] = raw.toLowerCase();
	} else if (f.type === 'url') {
		try { new URL(raw); container[f.name] = raw; } catch { err('auth.errors.generic'); }
	} else container[f.name] = raw;
}

/** Lit un FormData selon les champs déclarés (champs simples, multiselect, switch, fichiers, répéteurs `name[0][sub]`). */
export function parseFields(fd: FormData, fields: Field[]): Parsed {
	const out: Parsed = { values: {}, files: [], errors: {} };
	for (const f of fields) {
		if (f.type === 'repeater') {
			const idx = new Set<number>();
			for (const k of fd.keys()) { const m = k.match(new RegExp(`^${f.name}\\[(\\d+)\\]`)); if (m) idx.add(Number(m[1])); }
			const rows: Record<string, any>[] = [];
			for (const i of [...idx].sort((a, b) => a - b)) {
				const row: Record<string, any> = {};
				for (const sf of f.fields ?? []) parseOne(fd, sf, `${f.name}[${i}][${sf.name}]`, out, row);
				if (Object.keys(row).length || out.files.some(([k]) => k.startsWith(`${f.name}[${i}]`))) rows.push(row);
			}
			out.values[f.name] = rows;
			continue;
		}
		parseOne(fd, f, f.name, out, out.values);
	}
	return out;
}

/** JSON si aucun fichier ; sinon multipart : `payload` (JSON) + un champ par fichier (clé = chemin du champ). */
export function bodyFor(values: Record<string, any>, files: [string, File][]): Pick<RequestOptions, 'json' | 'form'> {
	if (!files.length) return { json: values };
	const fd = new FormData();
	fd.set('payload', JSON.stringify(values));
	for (const [k, f] of files) fd.append(k, f, f.name);
	return { form: fd };
}

const fill = (path: string, id?: string | null) => (id ? path.replace('{id}', id) : path);

export async function createRecord(event: Ev, def: ResourceDef) {
	const c = def.create;
	if (!c || !event.locals.user || !can(event.locals.user.role, c.permission)) error(403, { message: 'forbidden', code: 'forbidden' });
	const parsed = parseFields(await event.request!.formData(), c.fields);
	if (Object.keys(parsed.errors).length) return fail(400, { ok: false, op: 'create', errors: parsed.errors });
	try {
		const created = await backendJson<Row>(c.path ?? def.endpoint, { method: 'POST', token: event.locals.accessToken, ...bodyFor(parsed.values, parsed.files), headers: envHeader(event) });
		return { ok: true, op: 'create', id: created?.id as string | undefined };
	} catch (e) {
		const er = actionError(e);
		return fail(er.status >= 400 && er.status < 600 ? er.status : 400, { ok: false, op: 'create', message: er.message });
	}
}

export async function updateRecord(event: Ev, def: ResourceDef, id: string) {
	const c = def.create;
	if (!def.edit || !c || !event.locals.user || !can(event.locals.user.role, c.permission)) error(403, { message: 'forbidden', code: 'forbidden' });
	const fields = c.fields.map((f) => (f.secret ? { ...f, required: false } : { ...f, required: false }));
	const parsed = parseFields(await event.request!.formData(), fields);
	try {
		await backendJson(`${def.endpoint}/${id}`, { method: 'PATCH', token: event.locals.accessToken, ...bodyFor(parsed.values, parsed.files), headers: envHeader(event) });
		return { ok: true, op: 'update' };
	} catch (e) {
		return fail(400, { ok: false, op: 'update', message: actionError(e).message });
	}
}

/** Exécute une action déclarée (motif obligatoire, MFA « step-up » pour les actions critiques). */
export async function runAction(event: Ev, def: ResourceDef, id?: string | null) {
	const fd = await event.request!.formData();
	const action: Action | undefined = def.actions?.find((a) => a.id === String(fd.get('__action')));
	id = id ?? String(fd.get('__id') ?? '');
	if (!action || !event.locals.user || !can(event.locals.user.role, action.permission)) error(403, { message: 'forbidden', code: 'forbidden' });
	const parsed = parseFields(fd, action.fields ?? []);
	const reason = String(fd.get('reason') ?? '').trim();
	const stepUp = String(fd.get('step_up_code') ?? '').trim();
	if (action.reason && !reason) parsed.errors.reason = 'contact.errors.required';
	if (action.critical && !/^\d{6}$/.test(stepUp)) parsed.errors.step_up_code = 'auth.errors.required';
	if (Object.keys(parsed.errors).length) return fail(400, { ok: false, op: action.id, errors: parsed.errors });

	const values = { ...parsed.values, ...(action.reason ? { reason } : {}) };
	const headers = { ...envHeader(event), ...(action.critical ? { 'x-step-up-code': stepUp } : {}) };
	try {
		await backendJson(fill(action.path, id), { method: action.method, token: event.locals.accessToken, ...bodyFor(values, parsed.files), headers });
		return { ok: true, op: action.id };
	} catch (e) {
		const er = actionError(e);
		return fail(er.status >= 400 && er.status < 600 ? er.status : 400, { ok: false, op: action.id, message: er.message });
	}
}

/** Environnement courant (Sandbox / Production) transmis au backend. */
export const envHeader = (event: Ev): Record<string, string> => {
	const cookie = (event as any).cookies?.get?.('izi_env');
	return cookie === 'production' || cookie === 'sandbox' ? { 'x-izi-environment': cookie } : {};
};
export { isMissing, toPaged };
