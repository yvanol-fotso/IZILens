import { humanize } from '$lib/config/resources';

type T = (key: string, params?: Record<string, string | number>) => string;
const pick = (t: T, key: string, fallback: string) => {
	const v = t(key);
	return v === key ? fallback : v;
};
/** Libellé d'un champ/colonne : rx.f.<clé> sinon la clé « humanisée ». */
export const fieldLabel = (t: T, key: string) => pick(t, `rx.f.${key}`, humanize(key));
/** Libellé d'une valeur d'énumération : rx.o.<valeur> sinon valeur humanisée. */
export const optLabel = (t: T, value: unknown) => pick(t, `rx.o.${String(value)}`, humanize(String(value)));
export const sectionLabel = (t: T, key: string) => pick(t, `rx.s.${key}`, humanize(key));
export const resTitle = (t: T, scope: string, key: string) => pick(t, `rx.r.${key}.title`, humanize(key));
export const resDesc = (t: T, key: string) => pick(t, `rx.r.${key}.desc`, '');
export const actionLabel = (t: T, id: string) => pick(t, `rx.a.${id}`, humanize(id));

const GOOD = ['active', 'approved', 'paid', 'passed', 'resolved', 'published', 'succeeded', 'success', 'confirmed_ok', 'reviewed', 'verified', 'delivered', 'accept', 'low'];
const BAD = ['rejected', 'failed', 'overdue', 'suspended', 'revoked', 'denied', 'failure', 'high', 'disabled', 'void', 'expired', 'confirmed', 'refunded', 'failing', 'inactive', 'cancelled'];
const WARN = ['pending', 'manual_review', 'review', 'due', 'in_review', 'open', 'new', 'assigned', 'in_progress', 'waiting_for_customer', 'medium', 'scheduled', 'escalated', 'draft', 'pending_validation', 'processing'];
export type Tone = 'success' | 'danger' | 'warning' | 'neutral' | 'info';
export const toneFor = (v: unknown): Tone => {
	const s = String(v ?? '').toLowerCase();
	if (GOOD.includes(s)) return 'success';
	if (BAD.includes(s)) return 'danger';
	if (WARN.includes(s)) return 'warning';
	return 'neutral';
};
