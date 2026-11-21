<script lang="ts">
	import type { Snippet } from 'svelte';
	let { title, description, actions, children, padded = true, class: className = '' }: { title?: string; description?: string; actions?: Snippet; children?: Snippet; padded?: boolean; class?: string } = $props();
</script>

<section class="card {className}">
	{#if title || actions}
		<header>
			<div>
				{#if title}<h2>{title}</h2>{/if}
				{#if description}<p>{description}</p>{/if}
			</div>
			{#if actions}<div class="actions">{@render actions()}</div>{/if}
		</header>
	{/if}
	<div class="body" class:padded>{@render children?.()}</div>
</section>

<style lang="scss">
	.card { background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius-lg); box-shadow: var(--shadow-sm); overflow: hidden; }
	header { display: flex; align-items: flex-start; justify-content: space-between; gap: 1rem; padding: 1.15rem 1.35rem 0; flex-wrap: wrap; }
	h2 { font-size: var(--fs-lg); letter-spacing: -0.015em; }
	p { color: var(--fg-muted); font-size: var(--fs-sm); margin-top: 0.2rem; }
	.actions { display: flex; gap: 0.5rem; align-items: center; }
	.body.padded { padding: 1.15rem 1.35rem 1.35rem; }
</style>
