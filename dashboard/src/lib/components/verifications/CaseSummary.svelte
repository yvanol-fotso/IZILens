<script lang="ts">
	import { getI18n } from '$lib/i18n/index.svelte';
	import { formatDate, formatPercent } from '$lib/utils/format';
	import type { KycCase } from '$lib/types';
	import { Card, RiskBadge, StatusBadge } from '$lib/components/shared';

	let { kyc }: { kyc: KycCase } = $props();
	const i18n = getI18n();
	const { t } = i18n;
</script>

<Card>
	<dl>
		<div><dt>{t('verifications.columns.status')}</dt><dd><StatusBadge status={kyc.status} /></dd></div>
		<div><dt>{t('verifications.detail.risk')}</dt><dd><RiskBadge level={kyc.risk_level} /></dd></div>
		<div><dt>{t('verifications.detail.ocr')}</dt><dd class="big">{formatPercent(kyc.ocr_confidence, i18n.locale)}</dd></div>
		<div><dt>{t('verifications.detail.created')}</dt><dd>{formatDate(kyc.created_at, i18n.locale, true)}</dd></div>
		<div><dt>{t('verifications.detail.processed')}</dt><dd>{formatDate(kyc.processed_at, i18n.locale, true)}</dd></div>
		{#if kyc.decided_at}<div><dt>{t('verifications.detail.decided')}</dt><dd>{formatDate(kyc.decided_at, i18n.locale, true)}</dd></div>{/if}
	</dl>
	{#if kyc.decision_reason}<p class="reason">« {kyc.decision_reason} »</p>{/if}
	{#if kyc.failure_reason}<p class="fail"><b>{t('verifications.detail.failure')} :</b> {kyc.failure_reason}</p>{/if}
</Card>

<style lang="scss">
	dl { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 1.2rem; margin: 0; }
	dt { font-size: var(--fs-xs); color: var(--fg-muted); font-weight: 700; margin-bottom: 0.3rem; }
	dd { margin: 0; font-weight: 600; }
	.big { font-size: var(--fs-xl); font-weight: 800; }
	.reason { margin-top: 1rem; padding: 0.8rem 1rem; background: var(--surface-2); border-radius: var(--radius); color: var(--fg-muted); font-style: italic; }
	.fail { margin-top: 1rem; color: var(--danger); font-size: var(--fs-sm); }
</style>
