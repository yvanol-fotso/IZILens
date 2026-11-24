<script lang="ts">
	import { invalidateAll } from '$app/navigation';
	import { getI18n } from '$lib/i18n/index.svelte';
	import type { SessionUser } from '$lib/types';

	/** Bascule Sandbox / Production : cookie `izi_env`, transmis au backend (en-tête X-IZI-Environment). */
	let { user }: { user: SessionUser } = $props();
	const { t } = getI18n();
	let env = $state<'sandbox' | 'production'>('sandbox');
	$effect(() => { env = document.cookie.includes('izi_env=production') ? 'production' : 'sandbox'; });
	const prodOk = $derived(user.organization?.production_enabled !== false);
	async function set(v: 'sandbox' | 'production') {
		if (v === 'production' && !prodOk) return;
		env = v;
		document.cookie = `izi_env=${v}; Path=/; Max-Age=31536000; SameSite=Lax`;
		await invalidateAll();
	}
</script>

<div class="env" role="group" aria-label={t('cli.env.label')}>
	<button type="button" class:on={env === 'sandbox'} aria-pressed={env === 'sandbox'} onclick={() => set('sandbox')}>{t('cli.env.sandbox')}</button>
	<button type="button" class:on={env === 'production'} class:prod={env === 'production'} disabled={!prodOk} title={prodOk ? '' : t('cli.env.locked')} aria-pressed={env === 'production'} onclick={() => set('production')}>{t('cli.env.production')}</button>
</div>

<style lang="scss">
	.env { display: inline-flex; padding: 3px; gap: 3px; background: var(--surface-2); border-radius: var(--radius-pill); border: 1px solid var(--border); button { border: 0; background: none; padding: 0.3rem 0.8rem; border-radius: var(--radius-pill); font-weight: 800; font-size: var(--fs-xs); color: var(--fg-muted); &.on { background: var(--accent-orange); color: #2a1700; } &.on.prod { background: var(--accent-mint); color: #032a1d; } &:disabled { opacity: 0.5; cursor: not-allowed; } } }
</style>
