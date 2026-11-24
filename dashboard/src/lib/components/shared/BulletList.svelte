<script lang="ts">
	import { Check } from '@lucide/svelte';
	let { items, columns = 1 }: { items: string[]; columns?: 1 | 2 } = $props();
</script>

<ul class:two={columns === 2}>
	{#each items as it (it)}<li><Check size={17} /><span>{it}</span></li>{/each}
</ul>

<style lang="scss">
	ul { display: grid; gap: 0.6rem; &.two { grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 0.6rem 2rem; } }
	li { display: flex; gap: 0.7rem; align-items: flex-start; :global(svg) { color: var(--success); flex-shrink: 0; margin-top: 4px; } }
</style>
