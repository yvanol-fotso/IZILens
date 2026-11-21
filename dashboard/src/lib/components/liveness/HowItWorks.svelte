<script lang="ts">
	import { getI18n } from '$lib/i18n/index.svelte';
	import { Card } from '$lib/components/shared';
	const { t } = getI18n();
</script>

<Card title={t('liveness.howTitle')}>
	<ol>{#each ['one', 'two', 'three', 'four'] as k, i (k)}<li><b>{i + 1}</b><span>{t(`liveness.steps.${k}`)}</span></li>{/each}</ol>
</Card>

<style lang="scss">
	ol { display: grid; gap: 1rem; }
	li { display: flex; gap: 0.9rem; align-items: flex-start; font-size: var(--fs-sm); color: var(--fg-muted); }
	b { width: 26px; height: 26px; border-radius: 50%; background: var(--brand-navy); color: var(--brand-cyan); display: grid; place-items: center; font-size: var(--fs-xs); flex-shrink: 0; }
</style>
