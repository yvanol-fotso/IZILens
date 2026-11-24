<script lang="ts">
	import { enhance } from '$app/forms';
	import { invalidateAll } from '$app/navigation';
	import { ArrowLeft, Pencil } from '@lucide/svelte';
	import { getI18n } from '$lib/i18n/index.svelte';
	import { can } from '$lib/config/permissions';
	import type { ResourceDef } from '$lib/config/resources';
	import { toastSuccess } from '$lib/stores/toast';
	import type { FormState, Role } from '$lib/types';
	import { Badge, Button, Card, FormAlert, Modal, PageHeader } from '$lib/components/shared';
	import ActionPanel from './ActionPanel.svelte';
	import DataTable from './DataTable.svelte';
	import FieldInputs from './FieldInputs.svelte';
	import { fieldLabel, optLabel, resTitle, sectionLabel, toneFor } from './labels';
	import { formatDate, formatNumber, formatPercent } from '$lib/utils/format';

	type Row = Record<string, any>;
	let { def, row, related, role, base, form = null, staff = [] }: { def: ResourceDef; row: Row; related: Record<string, Row[]>; role: Role; base: string; form?: FormState | null; staff?: { id: string; full_name: string }[] } = $props();
	const i18n = getI18n();
	const { t } = i18n;
	let editOpen = $state(false);
	let loading = $state(false);
	const mine = $derived(form && form.op === 'update' ? form : null);
	const canEdit = $derived(!!def.edit && !!def.create && can(role, def.create.permission));
	const title = $derived(row.name ?? row.legal_name ?? row.reference ?? row.number ?? row.title_fr ?? row.full_name ?? row.subject ?? row.prefix ?? row.id);
	const detail = $derived(def.detail || { sections: [], related: [] });
	const money = (v: any, c: string) => new Intl.NumberFormat(i18n.locale === 'fr' ? 'fr-CA' : 'en-CA', { style: 'currency', currency: row.currency || 'CAD' }).format(Number(v));
	void money;
	const show = (v: any, type?: string) => {
		if (v === null || v === undefined || v === '') return '—';
		if (type === 'date') return formatDate(v, i18n.locale);
		if (type === 'datetime') return formatDate(v, i18n.locale, true);
		if (type === 'percent') return formatPercent(Number(v), i18n.locale);
		if (type === 'number') return formatNumber(Number(v), i18n.locale, 2);
		if (type === 'money') return new Intl.NumberFormat(i18n.locale === 'fr' ? 'fr-CA' : 'en-CA', { style: 'currency', currency: row.currency || 'CAD' }).format(Number(v));
		return typeof v === 'object' ? JSON.stringify(v) : String(v);
	};
</script>

<PageHeader title={String(title)} subtitle={resTitle(t, def.scope, def.key)}>
	{#snippet actions()}
		<Button href="{base}/{def.key}" variant="ghost">{#snippet icon()}<ArrowLeft size={18} />{/snippet}{t('common.back')}</Button>
		{#if canEdit}<Button variant="outline" onclick={() => (editOpen = true)}>{#snippet icon()}<Pencil size={16} />{/snippet}{t('common.edit')}</Button>{/if}
	{/snippet}
</PageHeader>

<div class="layout">
	<div class="main stack">
		{#each detail.sections as s (s.key)}
			<Card title={sectionLabel(t, s.key)}>
				<dl>
					{#each s.fields as f (f.key)}
						<div>
							<dt>{fieldLabel(t, f.key)}</dt>
							<dd class:mono={f.type === 'mono'}>
								{#if (f.type === 'status' || f.type === 'badge') && row[f.key]}<Badge tone={f.type === 'badge' ? 'neutral' : toneFor(row[f.key])} dot={f.type === 'status'}>{optLabel(t, row[f.key])}</Badge>
								{:else if f.type === 'risk' && row[f.key]}<Badge tone={toneFor(row[f.key])}>{optLabel(t, row[f.key])}</Badge>
								{:else if f.type === 'bool'}{row[f.key] ? t('common.yes') : t('common.no')}
								{:else if f.type === 'list' && Array.isArray(row[f.key])}<span class="chips">{#each row[f.key] as x (x)}<Badge tone="brand">{optLabel(t, x)}</Badge>{/each}</span>
								{:else}{show(row[f.key], f.type)}{/if}
							</dd>
						</div>
					{/each}
				</dl>
			</Card>
		{/each}
		{#each detail.related ?? [] as r (r.key)}
			<Card title={sectionLabel(t, r.key)} padded={false}>
				{#if (related[r.key] ?? []).length}<DataTable cols={r.cols} rows={related[r.key]} />{:else}<p class="empty">{t('rx.ui.noResults')}</p>{/if}
			</Card>
		{/each}
	</div>
	{#if def.actions?.length}
		<aside><Card title={t('rx.ui.actions')}><ActionPanel {def} {row} {role} {staff} /></Card></aside>
	{/if}
</div>

{#if canEdit && def.create}
	<Modal bind:open={editOpen} title={t('common.edit')} size="lg">
		<form id="edit-form" method="POST" action="?/update" class="stack" enctype="multipart/form-data"
			use:enhance={() => { loading = true; return async ({ result, update }) => { if (result.type === 'success') { toastSuccess(t('rx.ui.done')); editOpen = false; await invalidateAll(); } else await update({ reset: false }); loading = false; }; }}>
			<FormAlert form={mine} />
			<FieldInputs fields={def.create.fields} init={row} {staff} />
		</form>
		{#snippet footer()}<Button variant="ghost" onclick={() => (editOpen = false)}>{t('common.cancel')}</Button><Button type="submit" form="edit-form" variant="brand" {loading}>{t('common.save')}</Button>{/snippet}
	</Modal>
{/if}

<style lang="scss">
	.layout { display: grid; grid-template-columns: minmax(0, 1fr) 320px; gap: 1.25rem; align-items: start; } aside { position: sticky; top: 84px; }
	dl { display: grid; grid-template-columns: repeat(auto-fit, minmax(210px, 1fr)); gap: 1.1rem 1.5rem; margin: 0; } dt { font-size: var(--fs-xs); color: var(--fg-muted); font-weight: 700; margin-bottom: 0.25rem; } dd { margin: 0; font-weight: 600; word-break: break-word; &.mono { font-family: var(--font-mono); font-size: var(--fs-sm); } }
	.chips { display: flex; gap: 0.3rem; flex-wrap: wrap; } .empty { padding: 1.5rem; color: var(--fg-muted); font-size: var(--fs-sm); }
	@media (max-width: 1000px) { .layout { grid-template-columns: 1fr; } aside { position: static; } }
</style>
