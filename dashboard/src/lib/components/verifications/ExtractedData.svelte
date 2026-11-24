<script lang="ts">
	import { Flag } from '@lucide/svelte';
	import { getI18n } from '$lib/i18n/index.svelte';
	import { safeJson } from '$lib/utils/format';
	import type { KycCase } from '$lib/types';
	import { Badge, Card } from '$lib/components/shared';

	let { kyc }: { kyc: KycCase } = $props();
	const { t } = getI18n();
	const legacy = $derived(safeJson(kyc.extracted_data));
	const entries = $derived.by<[string, string][]>(() => {
		if (kyc.extracted) {
			return Object.entries(kyc.extracted)
				.filter(([, f]) => f && (f.normalized || f.value))
				.map(([k, f]) => [k, String(f.normalized ?? f.value)] as [string, string]);
		}
		return legacy ? Object.entries(legacy).filter(([, v]) => v !== null && v !== '' && typeof v !== 'object').map(([k, v]) => [k, String(v)] as [string, string]) : [];
	});
	const declared = $derived(
		kyc.declared_identity ? Object.entries(kyc.declared_identity).filter(([, v]) => v !== null && v !== '').map(([k, v]) => [k, String(v)] as [string, string]) : []
	);
	type FlagView = { key: string; text: string; tone: 'warning' | 'danger' | 'info' };
	const flags = $derived.by<FlagView[]>(() => {
		const f = kyc.flags;
		if (Array.isArray(f)) {
			return f.map((x, i) => {
				if (x && typeof x === 'object' && 'code' in x) {
					const flag = x as { code: string; message?: string; severity?: string };
					return { key: `${flag.code}-${i}`, text: flag.message ?? flag.code.replace(/_/g, ' '), tone: flag.severity === 'high' ? 'danger' : flag.severity === 'low' ? 'info' : 'warning' } as FlagView;
				}
				return { key: `${String(x)}-${i}`, text: String(x).replace(/_/g, ' '), tone: 'warning' } as FlagView;
			});
		}
		if (f && typeof f === 'object') return Object.entries(f).filter(([, v]) => !!v).map(([k]) => ({ key: k, text: k.replace(/_/g, ' '), tone: 'warning' }) as FlagView);
		return [];
	});
	const label = (k: string) => {
		const key = `verifications.detail.fields.${k}`;
		return t(key) === key ? k.replace(/_/g, ' ') : t(key);
	};
</script>

<Card title={t('verifications.detail.extracted')}>
	{#if entries.length}
		<dl>{#each entries as [k, v] (k)}<div><dt>{label(k)}</dt><dd>{v}</dd></div>{/each}</dl>
	{:else}
		<p class="muted">{t('verifications.detail.noExtracted')}</p>
	{/if}
</Card>

{#if declared.length}
	<Card title={t('verifications.detail.declared')}>
		<dl>{#each declared as [k, v] (k)}<div><dt>{label(k)}</dt><dd>{v}</dd></div>{/each}</dl>
	</Card>
{/if}

<Card title={t('verifications.detail.flags')}>
	{#if flags.length}
		<ul>{#each flags as f (f.key)}<li><Badge tone={f.tone}><Flag size={12} />{f.text}</Badge></li>{/each}</ul>
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
