<script lang="ts">
	import type { Component } from 'svelte';
	let { label, value, icon: Icon, tone = 'brand', hint }: { label: string; value: string | number; icon?: Component<any>; tone?: 'brand' | 'success' | 'warning' | 'danger' | 'info'; hint?: string } = $props();
</script>

<div class="stat">
	<div class="top">
		<span class="label">{label}</span>
		{#if Icon}<span class="ico {tone}"><Icon size={18} /></span>{/if}
	</div>
	<strong>{value}</strong>
	{#if hint}<span class="hint">{hint}</span>{/if}
</div>

<style lang="scss">
	.stat { background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius-lg); padding: 1.1rem 1.25rem; display: grid; gap: 0.35rem; }
	.top { display: flex; justify-content: space-between; align-items: center; gap: 0.5rem; }
	.label { font-size: var(--fs-sm); color: var(--fg-muted); font-weight: 600; }
	strong { font-size: 2rem; letter-spacing: -0.03em; line-height: 1.1; font-variant-numeric: tabular-nums; }
	.hint { font-size: var(--fs-xs); color: var(--fg-subtle); }
	.ico { width: 34px; height: 34px; border-radius: 10px; display: grid; place-items: center; }
	.brand { background: var(--primary-soft); color: var(--primary); }
	.success { background: var(--success-bg); color: var(--success); }
	.warning { background: var(--warning-bg); color: var(--warning); }
	.danger { background: var(--danger-bg); color: var(--danger); }
	.info { background: var(--info-bg); color: var(--info); }
</style>
