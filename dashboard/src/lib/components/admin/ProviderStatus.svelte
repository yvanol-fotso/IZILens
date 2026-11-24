<script lang="ts">
	import { getI18n } from '$lib/i18n/index.svelte';
	import { Badge, Card } from '$lib/components/shared';
	import { sectionLabel, toneFor } from '$lib/components/resource';
	let { status }: { status: Record<string, { available?: boolean; errors_24h?: number; latency_ms?: number; cost_30d?: number; currency?: string }> } = $props();
	const { t } = getI18n();
</script>

{#if Object.keys(status).length}
	<div class="grid">
		{#each Object.entries(status) as [k, s] (k)}
			<Card title={sectionLabel(t, k)}>
				<Badge tone={toneFor(s.available ? 'active' : 'failed')} dot>{s.available ? t('adm.up') : t('adm.down')}</Badge>
				<dl><div><dt>{t('adm.errors24')}</dt><dd>{s.errors_24h ?? '—'}</dd></div><div><dt>{t('adm.latency')}</dt><dd>{s.latency_ms ?? '—'} ms</dd></div><div><dt>{t('adm.cost30')}</dt><dd>{s.cost_30d !== undefined ? `${s.cost_30d} ${s.currency ?? ''}` : '—'}</dd></div></dl>
			</Card>
		{/each}
	</div>
{/if}

<style lang="scss">
	.grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(230px, 1fr)); gap: 1rem; margin-bottom: 1.25rem; } dl { display: grid; gap: 0.5rem; margin: 0.8rem 0 0; } dt { font-size: var(--fs-xs); color: var(--fg-muted); } dd { margin: 0; font-weight: 700; }
</style>
