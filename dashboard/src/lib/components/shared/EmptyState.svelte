<script lang="ts">
	import type { Component, Snippet } from 'svelte';
	let { icon: Icon, title, description, children }: { icon?: Component<any>; title: string; description?: string; children?: Snippet } = $props();
</script>

<div class="empty">
	{#if Icon}<span class="ico"><Icon size={26} /></span>{/if}
	<h3>{title}</h3>
	{#if description}<p>{description}</p>{/if}
	{#if children}<div class="cta">{@render children()}</div>{/if}
</div>

<style lang="scss">
	.empty { display: grid; justify-items: center; text-align: center; gap: 0.5rem; padding: 3rem 1.5rem; }
	.ico { width: 56px; height: 56px; border-radius: var(--radius); display: grid; place-items: center; background: var(--primary-soft); color: var(--primary); margin-bottom: 0.5rem; }
	h3 { font-size: var(--fs-lg); }
	p { color: var(--fg-muted); max-width: 42ch; font-size: var(--fs-sm); }
	.cta { margin-top: 0.75rem; }
</style>
