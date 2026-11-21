import type { Locale } from '$lib/i18n/locales';

const tag = (l: Locale) => (l === 'fr' ? 'fr-CA' : 'en-CA');

export function formatDate(value: string | Date | null | undefined, locale: Locale, withTime = false): string {
	if (!value) return '—';
	const d = value instanceof Date ? value : new Date(value);
	if (Number.isNaN(d.getTime())) return '—';
	return new Intl.DateTimeFormat(tag(locale), {
		year: 'numeric',
		month: 'short',
		day: 'numeric',
		...(withTime ? { hour: '2-digit', minute: '2-digit' } : {})
	}).format(d);
}

export function formatNumber(value: number | null | undefined, locale: Locale, digits = 0): string {
	if (value === null || value === undefined || Number.isNaN(value)) return '—';
	return new Intl.NumberFormat(tag(locale), { maximumFractionDigits: digits }).format(value);
}

/** Accepte 0–1 ou 0–100. */
export function formatPercent(value: number | null | undefined, locale: Locale): string {
	if (value === null || value === undefined || Number.isNaN(value)) return '—';
	const v = value <= 1 ? value : value / 100;
	return new Intl.NumberFormat(tag(locale), { style: 'percent', maximumFractionDigits: 0 }).format(v);
}

export function formatBytes(bytes: number | null | undefined): string {
	if (!bytes) return '—';
	const units = ['o', 'Ko', 'Mo', 'Go'];
	let i = 0;
	let v = bytes;
	while (v >= 1024 && i < units.length - 1) {
		v /= 1024;
		i++;
	}
	return `${v.toFixed(i === 0 ? 0 : 1)} ${units[i]}`;
}

export function initials(name: string | null | undefined): string {
	if (!name) return '?';
	return name
		.split(/\s+/)
		.filter(Boolean)
		.slice(0, 2)
		.map((p) => p[0]?.toUpperCase())
		.join('');
}

export function safeJson(value: unknown): Record<string, unknown> | null {
	if (!value) return null;
	if (typeof value === 'object') return value as Record<string, unknown>;
	if (typeof value === 'string') {
		try {
			const parsed = JSON.parse(value);
			return parsed && typeof parsed === 'object' ? parsed : null;
		} catch {
			return null;
		}
	}
	return null;
}
