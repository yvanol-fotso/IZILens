/** Fait apparaître un élément à l'entrée dans le viewport (un seul moment d'animation, respecte reduced-motion). */
export function reveal(node: HTMLElement, options: { delay?: number } = {}) {
	if (typeof IntersectionObserver === 'undefined' || matchMedia('(prefers-reduced-motion: reduce)').matches) return;
	node.classList.add('reveal');
	node.style.setProperty('--reveal-delay', `${options.delay ?? 0}ms`);
	const io = new IntersectionObserver(
		(entries) => {
			for (const e of entries) {
				if (e.isIntersecting) {
					node.classList.add('reveal-in');
					io.disconnect();
				}
			}
		},
		{ threshold: 0.12 }
	);
	io.observe(node);
	return { destroy: () => io.disconnect() };
}
