<script lang="ts">
	import { getI18n } from '$lib/i18n/index.svelte';
	import { formatBytes, formatNumber } from '$lib/utils/format';
	import type { KycDocument } from '$lib/types';
	import { Card, EmptyState } from '$lib/components/shared';
	import { ImageOff } from '@lucide/svelte';

	let { caseId, documents = [] }: { caseId: string; documents?: KycDocument[] } = $props();
	const i18n = getI18n();
	const { t } = i18n;
	let failed = $state<Record<string, boolean>>({});
</script>

<Card title={t('verifications.detail.documents')}>
	{#if documents.length === 0}
		<p class="muted">{t('common.noData')}</p>
	{:else}
		<div class="docs">
			{#each documents as d (d.id)}
				<figure>
					{#if failed[d.id]}
						<EmptyState icon={ImageOff} title={t('errors.generic')} />
					{:else}
						<!-- Servi via le proxy /api/v1 : le jeton reste côté serveur -->
						<img src="/api/v1/kyc/cases/{caseId}/documents/{d.id}/content" alt={t(`verifications.detail.${d.side}`)} loading="lazy" onerror={() => (failed[d.id] = true)} />
					{/if}
					<figcaption>
						<b>{t(`verifications.detail.${d.side}`)}</b>
						<span>{d.width}×{d.height} · {formatBytes(d.size_bytes)} · {t('verifications.detail.sharpness')} {formatNumber(d.sharpness, i18n.locale)}</span>
					</figcaption>
				</figure>
			{/each}
		</div>
	{/if}
</Card>

<style lang="scss">
	.docs { display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 1rem; }
	figure { margin: 0; border: 1px solid var(--border); border-radius: var(--radius); overflow: hidden; background: var(--surface-2); }
	img { width: 100%; aspect-ratio: 1.58; object-fit: contain; background: repeating-conic-gradient(var(--surface-3) 0 25%, var(--surface-2) 0 50%) 0 0 / 20px 20px; }
	figcaption { display: grid; padding: 0.7rem 0.9rem; font-size: var(--fs-xs); color: var(--fg-muted); b { color: var(--fg); font-size: var(--fs-sm); } }
</style>
