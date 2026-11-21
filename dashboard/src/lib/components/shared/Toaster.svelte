<script lang="ts">
	import { CircleCheck, CircleAlert, Info, X } from '@lucide/svelte';
	import { toasts, dismiss } from '$lib/stores/toast';
</script>

<div class="toaster" aria-live="polite">
	{#each $toasts as t (t.id)}
		<div class="toast {t.tone}" role="status">
			{#if t.tone === 'success'}<CircleCheck size={18} />{:else if t.tone === 'error'}<CircleAlert size={18} />{:else}<Info size={18} />{/if}
			<span>{t.message}</span>
			<button type="button" onclick={() => dismiss(t.id)} aria-label="Close"><X size={16} /></button>
		</div>
	{/each}
</div>

<style lang="scss">
	.toaster { position: fixed; right: 1rem; bottom: 1rem; z-index: var(--z-toast); display: grid; gap: 0.5rem; width: min(380px, calc(100vw - 2rem)); }
	.toast { display: flex; align-items: center; gap: 0.7rem; padding: 0.85rem 1rem; border-radius: var(--radius); background: var(--brand-navy); color: #fff; box-shadow: var(--shadow-lg); font-size: var(--fs-sm); font-weight: 600; animation: in 0.25s var(--ease); span { flex: 1; } button { border: 0; background: none; color: inherit; opacity: 0.7; display: grid; &:hover { opacity: 1; } } }
	.success :global(svg:first-child) { color: var(--accent-mint); }
	.error :global(svg:first-child) { color: var(--accent-rose); }
	.info :global(svg:first-child) { color: var(--brand-cyan); }
	@keyframes in { from { opacity: 0; transform: translateY(10px); } }
</style>
