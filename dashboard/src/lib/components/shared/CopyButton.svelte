<script lang="ts">
	import { Copy, Check } from '@lucide/svelte';
	import { copy } from '$lib/actions/copy';
	import { getI18n } from '$lib/i18n/index.svelte';

	let { text, label, size = 'sm' }: { text: string; label?: string; size?: 'sm' | 'md' } = $props();
	const { t } = getI18n();
	let done = $state(false);
</script>

<button type="button" class="cp {size}" use:copy={{ text, message: t('toast.copied') }} onclick={() => { done = true; setTimeout(() => (done = false), 1600); }}>
	{#if done}<Check size={15} />{:else}<Copy size={15} />{/if}
	{label ?? (done ? t('common.copied') : t('common.copy'))}
</button>

<style lang="scss">
	.cp { display: inline-flex; align-items: center; gap: 0.4rem; border: 1.5px solid var(--border-strong); background: var(--surface); color: var(--fg); border-radius: var(--radius-sm); font-weight: 700; &:hover { border-color: var(--primary); color: var(--primary); } }
	.sm { padding: 0.4rem 0.7rem; font-size: var(--fs-xs); }
	.md { padding: 0.65rem 1rem; font-size: var(--fs-sm); }
</style>
