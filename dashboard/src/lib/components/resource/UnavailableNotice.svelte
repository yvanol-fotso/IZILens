<script lang="ts">
	import { PlugZap } from '@lucide/svelte';
	import { getI18n } from '$lib/i18n/index.svelte';
	let { endpoint }: { endpoint: string } = $props();
	const { t } = getI18n();
</script>

<div class="na" role="status">
	<span class="ico"><PlugZap size={26} /></span>
	<h3>{t('rx.ui.unavailable')}</h3>
	<p>{t('rx.ui.unavailableText')}</p>
	<code>GET {endpoint}</code>
</div>

<style lang="scss">
	.na { display: grid; justify-items: center; gap: 0.6rem; text-align: center; padding: 3rem 1.5rem; }
	.ico { width: 56px; height: 56px; border-radius: 16px; display: grid; place-items: center; background: var(--warning-bg); color: var(--warning); } h3 { font-size: var(--fs-lg); } p { color: var(--fg-muted); font-size: var(--fs-sm); max-width: 52ch; }
	code { padding: 0.3rem 0.7rem; background: var(--surface-2); border-radius: var(--radius-sm); font-size: var(--fs-xs); }
</style>
