<script lang="ts">
	import type { Snippet } from 'svelte';
	let { title, kicker, children, align = 'left', tone = 'default' }: { title: string; kicker?: string; children?: Snippet; align?: 'left' | 'center'; tone?: 'default' | 'light' } = $props();
</script>

<header class="sh {align} {tone}">
	{#if kicker}<p class="kicker">{kicker}</p>{/if}
	<h2>{title}</h2>
	{#if children}<div class="body">{@render children()}</div>{/if}
</header>

<style lang="scss">
	.sh { max-width: 720px; margin-bottom: 2.6rem; &.center { margin-inline: auto; text-align: center; } }
	.kicker { font-size: var(--fs-sm); font-weight: 700; color: var(--primary); margin-bottom: 0.7rem; font-style: italic; }
	h2 { font-size: var(--fs-3xl); }
	.body { margin-top: 1rem; color: var(--fg-muted); font-size: var(--fs-lg); display: grid; gap: 0.8rem; }
	.light { .kicker { color: var(--brand-cyan); } .body { color: #a9bfdc; } h2 { color: #fff; } }
</style>
