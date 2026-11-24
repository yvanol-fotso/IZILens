<script lang="ts">
	import { getI18n } from '$lib/i18n/index.svelte';
	import { Button, Input, Select } from '$lib/components/shared';
	let { query }: { query: Record<string, string | undefined> } = $props();
	const { t } = getI18n();
	let range = $state(query.range ?? '30d');
</script>

<form method="GET" class="bar">
	<Select label={t('adm.dash.period')} name="range" bind:value={range} options={['today', '7d', '30d', '90d', 'custom'].map((r) => ({ value: r, label: t(`adm.range.${r}`) }))} />
	{#if range === 'custom'}<Input label={t('rx.ui.from')} name="from" type="date" value={query.from ?? ''} /><Input label={t('rx.ui.to')} name="to" type="date" value={query.to ?? ''} />{/if}
	<Input label={t('rx.f.country')} name="country" value={query.country ?? ''} />
	<Select label={t('rx.f.service')} name="service" value={query.service ?? ''} options={[{ value: '', label: t('common.all') }, ...['kyc', 'kyb', 'biometrics', 'monitoring'].map((s) => ({ value: s, label: t(`rx.o.${s}`) }))]} />
	<Input label={t('rx.f.client_id')} name="client_id" value={query.client_id ?? ''} />
	<Button type="submit" variant="brand">{t('common.filter')}</Button>
</form>

<style lang="scss">
	.bar { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 0.8rem; align-items: end; margin-bottom: 1.5rem; padding: 1rem 1.2rem; background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius-lg); }
</style>
