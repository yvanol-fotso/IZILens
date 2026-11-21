<script lang="ts">
	import type { Snippet } from 'svelte';
	let { title, subtitle, actions }: { title: string; subtitle?: string; actions?: Snippet } = $props();
</script>

<header class="ph">
	<div>
		<h1>{title}</h1>
		{#if subtitle}<p>{subtitle}</p>{/if}
	</div>
	{#if actions}<div class="actions">{@render actions()}</div>{/if}
</header>

<style lang="scss">
	.ph { display: flex; align-items: flex-end; justify-content: space-between; gap: 1rem; flex-wrap: wrap; margin-bottom: 1.5rem; }
	h1 { font-size: var(--fs-2xl); }
	p { color: var(--fg-muted); margin-top: 0.35rem; max-width: 62ch; }
	.actions { display: flex; gap: 0.6rem; flex-wrap: wrap; }
</style>
