<script lang="ts">
	/** Rend du HTML issu de Markdown de confiance (fichiers /src/content). Ne jamais lui passer de saisie utilisateur. */
	let { html }: { html: string } = $props();
</script>

<div class="prose">{@html html}</div>

<style lang="scss">
	.prose {
		max-width: 72ch;
		line-height: 1.75;
		:global(h2) { font-size: var(--fs-xl); margin: 2.6rem 0 0.9rem; padding-top: 0.4rem; scroll-margin-top: calc(var(--header-h) + 20px); }
		:global(h3) { font-size: var(--fs-lg); margin: 1.8rem 0 0.6rem; }
		:global(p) { margin: 0 0 1rem; color: var(--fg); }
		:global(ul), :global(ol) { margin: 0 0 1.1rem; padding-left: 1.3rem; display: grid; gap: 0.4rem; }
		:global(ul) { list-style: disc; }
		:global(ol) { list-style: decimal; }
		:global(li::marker) { color: var(--primary); }
		:global(a) { font-weight: 600; text-decoration: underline; text-underline-offset: 3px; }
		:global(strong) { font-weight: 800; }
		:global(blockquote) { margin: 1.4rem 0; padding: 0.9rem 1.2rem; border-left: 4px solid var(--brand-cyan); background: var(--surface-2); border-radius: 0 var(--radius) var(--radius) 0; color: var(--fg-muted); }
		:global(code) { background: var(--surface-3); padding: 0.12em 0.4em; border-radius: 6px; }
		:global(hr) { border: 0; border-top: 1px solid var(--border); margin: 2rem 0; }
		:global(table) { margin: 1.2rem 0; font-size: var(--fs-sm); display: block; overflow-x: auto; }
		:global(th), :global(td) { text-align: left; padding: 0.6rem 0.9rem; border: 1px solid var(--border); }
		:global(th) { background: var(--surface-2); }
	}
</style>
