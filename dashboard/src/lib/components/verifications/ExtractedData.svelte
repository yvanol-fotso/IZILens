<script lang="ts">
	import { Flag } from '@lucide/svelte';
	import { getI18n } from '$lib/i18n/index.svelte';
	import { safeJson } from '$lib/utils/format';
	import type { KycCase } from '$lib/types';
	import { Badge, Card } from '$lib/components/shared';

	let { kyc }: { kyc: KycCase } = $props();
	const { t } = getI18n();
	const data = $derived(safeJson(kyc.extracted_data));
	const entries = $derived(data ? Object.entries(data).filter(([, v]) => v !== null && v !== '' && typeof v !== 'object') : []);
	const flags = $derived.by<string[]>(() => {
		const f = kyc.flags;
		if (Array.isArray(f)) return f.map(String);
		if (f && typeof f === 'object') return Object.entries(f).filter(([, v]) => !!v).map(([k]) => k);
		return [];
	});
	const label = (k: string) => {
		const key = `verifications.detail.fields.${k}`;
		return t(key) === key ? k.replace(/_/g, ' ') : t(key);
	};
</script>

<Card title={t('verifications.detail.extracted')}>
	{#if entries.length}
		<dl>{#each entries as [k, v] (k)}<div><dt>{label(k)}</dt><dd>{String(v)}</dd></div>{/each}</dl>
	{:else}
		<p class="muted">{t('verifications.detail.noExtracted')}</p>
	{/if}
</Card>

<Card title={t('verifications.detail.flags')}>
	{#if flags.length}
		<ul>{#each flags as f (f)}<li><Badge tone="warning"><Flag size={12} />{f.replace(/_/g, ' ')}</Badge></li>{/each}</ul>
	{:else}
		<p class="muted">{t('verifications.detail.noFlags')}</p>
	{/if}
</Card>

<style lang="scss">
	dl { display: grid; grid-template-columns: repeat(auto-fit, minmax(190px, 1fr)); gap: 1rem 1.5rem; margin: 0; }
	dt { font-size: var(--fs-xs); color: var(--fg-muted); font-weight: 700; text-transform: capitalize; }
	dd { margin: 0.15rem 0 0; font-weight: 700; word-break: break-word; }
	ul { display: flex; flex-wrap: wrap; gap: 0.5rem; }
</style>
