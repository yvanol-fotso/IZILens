<script lang="ts">
	import type { Snippet } from 'svelte';
	let { checked = $bindable(false), name, error, children, required = false }: { checked?: boolean; name: string; error?: string; children: Snippet; required?: boolean } = $props();
</script>

<div class="cb">
	<label><input type="checkbox" {name} bind:checked {required} aria-invalid={!!error} /><span>{@render children()}</span></label>
	{#if error}<p class="err">{error}</p>{/if}
</div>

<style lang="scss">
	label { display: flex; gap: 0.7rem; align-items: flex-start; cursor: pointer; font-size: var(--fs-sm); } input { margin-top: 3px; width: 18px; height: 18px; accent-color: var(--primary); flex-shrink: 0; }
	.err { color: var(--danger); font-size: var(--fs-xs); font-weight: 600; margin: 0.3rem 0 0 1.75rem; } :global(.cb a) { text-decoration: underline; }
</style>
