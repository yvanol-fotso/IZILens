<script lang="ts">
	import { Search } from '@lucide/svelte';
	import { getI18n } from '$lib/i18n/index.svelte';
	import { Button, Input, Select } from '$lib/components/shared';

	let { filters }: { filters: { status: string; risk_level: string; search: string } } = $props();
	const { t } = getI18n();
	let search = $state(filters.search);
	let status = $state(filters.status);
	let risk = $state(filters.risk_level);
	const statuses = ['processing', 'pending_review', 'approved', 'rejected', 'failed'];
	const risks = ['low', 'medium', 'high'];
</script>

<form method="GET" class="filters" role="search">
	<Input label={t('common.search')} name="search" icon={Search} placeholder={t('verifications.searchPlaceholder')} bind:value={search} />
	<Select label={t('verifications.columns.status')} name="status" bind:value={status} options={[{ value: '', label: t('verifications.allStatuses') }, ...statuses.map((s) => ({ value: s, label: t(`status.${s}`) }))]} />
	<Select label={t('verifications.columns.risk')} name="risk_level" bind:value={risk} options={[{ value: '', label: t('verifications.allRisks') }, ...risks.map((r) => ({ value: r, label: t(`risk.${r}`) }))]} />
	<div class="btns"><Button type="submit" variant="brand">{t('common.filter')}</Button><Button href="/app/verifications" variant="ghost">{t('common.reset')}</Button></div>
</form>

<style lang="scss">
	.filters { display: grid; grid-template-columns: 2fr 1fr 1fr auto; gap: 0.8rem; align-items: end; padding: 1.1rem 1.35rem; border-bottom: 1px solid var(--border); }
	.btns { display: flex; gap: 0.4rem; }
	@media (max-width: 900px) { .filters { grid-template-columns: 1fr 1fr; } }
	@media (max-width: 560px) { .filters { grid-template-columns: 1fr; } }
</style>
