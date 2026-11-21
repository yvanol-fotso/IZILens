const SELECTOR = 'a[href], button:not([disabled]), textarea, input, select, [tabindex]:not([tabindex="-1"])';

/** Garde le focus clavier à l'intérieur d'un conteneur (tiroirs, menus mobiles). */
export function focusTrap(node: HTMLElement) {
	const previous = document.activeElement as HTMLElement | null;
	node.querySelector<HTMLElement>(SELECTOR)?.focus();
	const onKey = (e: KeyboardEvent) => {
		if (e.key !== 'Tab') return;
		const items = [...node.querySelectorAll<HTMLElement>(SELECTOR)];
		if (!items.length) return;
		const first = items[0];
		const last = items[items.length - 1];
		if (e.shiftKey && document.activeElement === first) {
			e.preventDefault();
			last.focus();
		} else if (!e.shiftKey && document.activeElement === last) {
			e.preventDefault();
			first.focus();
		}
	};
	node.addEventListener('keydown', onKey);
	return {
		destroy() {
			node.removeEventListener('keydown', onKey);
			previous?.focus?.();
		}
	};
}
