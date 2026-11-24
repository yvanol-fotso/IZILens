import fr from './fr';
import en from './en';
import type { Locale } from './locales';

const dictionaries = { fr, en } as const;

function lookup(dict: unknown, key: string): string | undefined {
	let cur: unknown = dict;
	for (const part of key.split('.')) {
		if (cur && typeof cur === 'object' && part in (cur as object)) cur = (cur as Record<string, unknown>)[part];
		else return undefined;
	}
	return typeof cur === 'string' ? cur : undefined;
}

/** Traduction pure (utilisable côté serveur et client). `{name}` est interpolé. */
export function translate(locale: Locale, key: string, params?: Record<string, string | number>): string {
	const raw = lookup(dictionaries[locale], key) ?? lookup(dictionaries.fr, key) ?? key;
	if (!params) return raw;
	return raw.replace(/\{(\w+)\}/g, (_, k) => (k in params ? String(params[k]) : `{${k}}`));
}

/** Liste de chaînes (ex. fonctionnalités, cas d'usage) : `["a","b"]` dans le dictionnaire. */
export function translateList(locale: Locale, key: string): string[] {
	for (const l of [locale, 'fr'] as const) {
		let cur: unknown = dictionaries[l];
		for (const part of key.split('.')) cur = cur && typeof cur === 'object' ? (cur as Record<string, unknown>)[part] : undefined;
		if (Array.isArray(cur)) return cur as string[];
	}
	return [];
}
