<script lang="ts">
	import { Search } from '@lucide/svelte';
	import { getI18n } from '$lib/i18n/index.svelte';
	import type { Filter } from '$lib/config/resources';
	import { Button, Input, Select } from '$lib/components/shared';
	import { fieldLabel, optLabel } from './labels';

	let { filters, values, resetHref }: { filters: Filter[]; values: Record<string, string>; resetHref: string } = $props();
	const { t } = getI18n();
</script>

<form method="GET" class="bar" role="search">
	{#each filters as f (f.key)}
		{#if f.type === 'search'}
			<Input label={f.key === 'search' ? t('common.search') : fieldLabel(t, f.key)} name={f.key} value={values[f.key] ?? ''} icon={f.key === 'search' ? Search : undefined} />
		{:else if f.type === 'select'}
			<Select label={fieldLabel(t, f.key)} name={f.key} value={values[f.key] ?? ''} options={[{ value: '', label: t('common.all') }, ...(f.options ?? []).map((o) => ({ value: o, label: optLabel(t, o) }))]} />
		{:else}
			<Input label="{fieldLabel(t, f.key)} · {t('rx.ui.from')}" name="{f.key}_from" type="date" value={values[`${f.key}_from`] ?? ''} />
			<Input label={t('rx.ui.to')} name="{f.key}_to" type="date" value={values[`${f.key}_to`] ?? ''} />
		{/if}
	{/each}
	<div class="btns"><Button type="submit" variant="brand">{t('common.filter')}</Button><Button href={resetHref} variant="ghost">{t('common.reset')}</Button></div>
</form>

<style lang="scss">
	.bar { display: grid; grid-template-columns: repeat(auto-fit, minmax(170px, 1fr)); gap: 0.8rem; align-items: end; padding: 1.1rem 1.35rem; border-bottom: 1px solid var(--border); }
	.btns { display: flex; gap: 0.4rem; }
</style>
