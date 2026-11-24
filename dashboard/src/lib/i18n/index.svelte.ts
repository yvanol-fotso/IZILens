import { getContext, setContext } from 'svelte';
import { translate, translateList } from './translate';
import type { Locale } from './locales';

const KEY = Symbol('izi-i18n');

/** Instance i18n par requête (contexte Svelte) : pas d'état global partagé côté serveur. */
export class I18n {
	locale = $state<Locale>('fr');

	constructor(initial: Locale) {
		this.locale = initial;
	}

	list = (key: string) => translateList(this.locale, key);
	t = (key: string, params?: Record<string, string | number>) => translate(this.locale, key, params);
}

export function setI18n(initial: Locale): I18n {
	const instance = new I18n(initial);
	setContext(KEY, instance);
	return instance;
}

export function getI18n(): I18n {
	return getContext<I18n>(KEY);
}
