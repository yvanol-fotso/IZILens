import { writable } from 'svelte/store';
import { browser } from '$app/environment';

/** Incrémentez CONSENT_VERSION quand les catégories ou les technologies changent : le consentement sera redemandé. */
export const CONSENT_VERSION = '1.0';
export const CONSENT_EFFECTIVE_DATE = '2026-11-17';
const COOKIE = 'izi_consent';
const MAX_AGE_DAYS = 180; // politique de renouvellement : 6 mois

export const OPTIONAL_CATEGORIES = ['functional', 'analytics', 'performance', 'advertising', 'unclassified'] as const;
export type OptionalCategory = (typeof OPTIONAL_CATEGORIES)[number];

export interface Consent {
	decided: boolean;
	version: string;
	timestamp: string | null;
	necessary: true;
	choices: Record<OptionalCategory, boolean>;
}

const none = (): Record<OptionalCategory, boolean> => Object.fromEntries(OPTIONAL_CATEGORIES.map((c) => [c, false])) as Record<OptionalCategory, boolean>;
const initial: Consent = { decided: false, version: CONSENT_VERSION, timestamp: null, necessary: true, choices: none() };

function read(): Consent {
	if (!browser) return initial;
	const raw = document.cookie.split('; ').find((c) => c.startsWith(COOKIE + '='));
	if (!raw) return initial;
	try {
		const parsed = JSON.parse(decodeURIComponent(raw.split('=')[1]));
		// Version différente => on redemande.
		if (parsed.version !== CONSENT_VERSION) return initial;
		return { ...initial, ...parsed, choices: { ...none(), ...parsed.choices }, decided: true };
	} catch {
		return initial;
	}
}

function persist(value: Consent) {
	if (!browser) return;
	const body = encodeURIComponent(JSON.stringify({ version: value.version, timestamp: value.timestamp, choices: value.choices }));
	document.cookie = `${COOKIE}=${body}; Path=/; Max-Age=${60 * 60 * 24 * MAX_AGE_DAYS}; SameSite=Lax`;
}

const store = writable<Consent>(read());
/** Ouvre le centre de préférences depuis n'importe où (pied de page, page Cookies). */
export const consentPanelOpen = writable(false);

function save(choices: Partial<Record<OptionalCategory, boolean>>) {
	const next: Consent = { decided: true, version: CONSENT_VERSION, timestamp: new Date().toISOString(), necessary: true, choices: { ...none(), ...choices } };
	persist(next);
	store.set(next);
	if (browser) window.dispatchEvent(new CustomEvent('izi:consent', { detail: next }));
}

export const consent = {
	subscribe: store.subscribe,
	acceptAll: () => save(Object.fromEntries(OPTIONAL_CATEGORIES.map((c) => [c, true]))),
	rejectOptional: () => save({}),
	save
};

/** Ouvre le centre de préférences (retrait / modification du consentement à tout moment). */
export function openConsentCentre() {
	consentPanelOpen.set(true);
}
