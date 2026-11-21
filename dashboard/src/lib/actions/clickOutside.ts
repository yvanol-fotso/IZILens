/** Appelle `callback` quand on clique en dehors de l'élément ou qu'on appuie sur Échap. */
export function clickOutside(node: HTMLElement, callback: () => void) {
	const onClick = (e: MouseEvent) => {
		if (!node.contains(e.target as Node)) callback();
	};
	const onKey = (e: KeyboardEvent) => {
		if (e.key === 'Escape') callback();
	};
	document.addEventListener('click', onClick, true);
	document.addEventListener('keydown', onKey);
	return {
		update(next: () => void) {
			callback = next;
		},
		destroy() {
			document.removeEventListener('click', onClick, true);
			document.removeEventListener('keydown', onKey);
		}
	};
}
