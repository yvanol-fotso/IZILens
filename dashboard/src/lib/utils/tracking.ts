import { get } from 'svelte/store';
import { consent, type OptionalCategory } from '$lib/stores/consent';

/**
 * Garde-fou : n'exécute `load` (ex. injection d'un script analytique) qu'avec consentement.
 * Aucun traceur facultatif ne doit être chargé en dehors de cette fonction.
 *
 *   onConsent('analytics', () => loadAnalyticsScript());
 */
export function onConsent(category: OptionalCategory, load: () => void) {
	let done = false;
	const run = () => {
		if (!done && get(consent).choices[category]) {
			done = true;
			load();
		}
	};
	run();
	const handler = () => run();
	window.addEventListener('izi:consent', handler);
	return () => window.removeEventListener('izi:consent', handler);
}
