<script lang="ts">
	import type { Snippet } from 'svelte';
	let { tone = 'neutral', dot = false, children }: { tone?: 'neutral' | 'success' | 'warning' | 'danger' | 'info' | 'brand'; dot?: boolean; children?: Snippet } = $props();
</script>

<span class="badge {tone}">{#if dot}<i></i>{/if}{@render children?.()}</span>

<style lang="scss">
	.badge { display: inline-flex; align-items: center; gap: 0.4rem; padding: 0.22rem 0.65rem; border-radius: var(--radius-pill); font-size: var(--fs-xs); font-weight: 700; white-space: nowrap; }
	i { width: 6px; height: 6px; border-radius: 50%; background: currentColor; }
	.neutral { background: var(--surface-3); color: var(--fg-muted); }
	.success { background: var(--success-bg); color: var(--success); }
	.warning { background: var(--warning-bg); color: var(--warning); }
	.danger { background: var(--danger-bg); color: var(--danger); }
	.info { background: var(--info-bg); color: var(--info); }
	.brand { background: var(--brand-navy); color: var(--brand-cyan); }
</style>
