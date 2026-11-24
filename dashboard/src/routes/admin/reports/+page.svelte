<script lang="ts">
	import { FileSpreadsheet, FileText, Table2 } from '@lucide/svelte';
	import { getI18n } from '$lib/i18n/index.svelte';
	import { REPORTS } from '$lib/config/admin-config';
	import { Card, Input, PageHeader } from '$lib/components/shared';
	const { t } = getI18n();
	let from = $state('');
	let to = $state('');
	let country = $state('');
	const href = (id: string, f: string) => `/api/admin/admin/reports/${id}/export?format=${f}${from ? `&from=${from}` : ''}${to ? `&to=${to}` : ''}${country ? `&country=${country}` : ''}`;
</script>

<PageHeader title={t('adm.rep.title')} subtitle={t('adm.rep.subtitle')} />
<Card title={t('adm.rep.parameters')}>
	<div class="params"><Input label={t('rx.ui.from')} type="date" name="from" bind:value={from} /><Input label={t('rx.ui.to')} type="date" name="to" bind:value={to} /><Input label={t('rx.f.country')} name="country" bind:value={country} hint="ISO 3166-1 alpha-2" /></div>
</Card>
<div class="grid">
	{#each REPORTS as r (r)}
		<article>
			<h3>{t(`adm.rep.items.${r}.title`)}</h3><p>{t(`adm.rep.items.${r}.desc`)}</p>
			<div class="fmt">
				<a href={href(r, 'pdf')} download data-sveltekit-reload><FileText size={16} />PDF</a>
				<a href={href(r, 'csv')} download data-sveltekit-reload><Table2 size={16} />CSV</a>
				<a href={href(r, 'xlsx')} download data-sveltekit-reload><FileSpreadsheet size={16} />Excel</a>
			</div>
		</article>
	{/each}
</div>

<style lang="scss">
	.params { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; } .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 1rem; margin-top: 1.25rem; }
	article { padding: 1.5rem; background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius-lg); display: grid; gap: 0.6rem; align-content: start; } h3 { font-size: var(--fs-lg); } p { color: var(--fg-muted); font-size: var(--fs-sm); }
	.fmt { display: flex; gap: 0.5rem; margin-top: 0.5rem; a { display: inline-flex; align-items: center; gap: 0.4rem; padding: 0.45rem 0.9rem; border: 1.5px solid var(--border-strong); border-radius: var(--radius-sm); font-weight: 700; font-size: var(--fs-sm); color: var(--fg); &:hover { border-color: var(--primary); color: var(--primary); text-decoration: none; } } }
</style>
