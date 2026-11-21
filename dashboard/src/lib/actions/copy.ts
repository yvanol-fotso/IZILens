import { toastSuccess } from '$lib/stores/toast';

/** `use:copy={{ text, message }}` — copie au clic et notifie. */
export function copy(node: HTMLElement, params: { text: string; message?: string }) {
	let current = params;
	const handler = async () => {
		try {
			await navigator.clipboard.writeText(current.text);
			toastSuccess(current.message ?? 'Copié');
		} catch {
			/* presse-papiers indisponible */
		}
	};
	node.addEventListener('click', handler);
	return {
		update(next: { text: string; message?: string }) {
			current = next;
		},
		destroy() {
			node.removeEventListener('click', handler);
		}
	};
}
