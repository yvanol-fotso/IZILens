<script lang="ts">
	import type { Snippet } from 'svelte';
	let { children, caption }: { children?: Snippet; caption?: string } = $props();
</script>

<div class="wrap" tabindex="-1">
	<table>
		{#if caption}<caption class="sr-only">{caption}</caption>{/if}
		{@render children?.()}
	</table>
</div>

<style lang="scss">
	.wrap { overflow-x: auto; }
	table { min-width: 640px; font-size: var(--fs-sm); }
	.wrap :global(th) { text-align: left; padding: 0.75rem 1.1rem; font-size: var(--fs-xs); font-weight: 700; color: var(--fg-muted); background: var(--surface-2); border-bottom: 1px solid var(--border); white-space: nowrap; }
	.wrap :global(td) { padding: 0.85rem 1.1rem; border-bottom: 1px solid var(--border); vertical-align: middle; }
	.wrap :global(tbody tr:last-child td) { border-bottom: 0; }
	.wrap :global(tbody tr:hover) { background: var(--surface-2); }
	.wrap :global(td.num), .wrap :global(th.num) { text-align: right; font-variant-numeric: tabular-nums; }
	.wrap :global(td a.cell-link) { font-weight: 700; color: var(--fg); }
</style>
