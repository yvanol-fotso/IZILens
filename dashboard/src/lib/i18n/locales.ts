export const LOCALES = ['fr', 'en'] as const;
export type Locale = (typeof LOCALES)[number];

export const DEFAULT_LOCALE: Locale = 'fr';
export const LOCALE_COOKIE = 'izi_locale';

export const LOCALE_LABELS: Record<Locale, { name: string; short: string; flag: string }> = {
	fr: { name: 'Français', short: 'FR', flag: '🇫🇷' },
	en: { name: 'English', short: 'EN', flag: '🇬🇧' }
};

export function isLocale(value: unknown): value is Locale {
	return typeof value === 'string' && (LOCALES as readonly string[]).includes(value);
}

/** Cookie > en-tête Accept-Language > langue par défaut. */
export function resolveLocale(cookie?: string | null, acceptLanguage?: string | null): Locale {
	if (isLocale(cookie)) return cookie;
	if (acceptLanguage) {
		for (const part of acceptLanguage.split(',')) {
			const code = part.trim().slice(0, 2).toLowerCase();
			if (isLocale(code)) return code;
		}
	}
	return DEFAULT_LOCALE;
}
