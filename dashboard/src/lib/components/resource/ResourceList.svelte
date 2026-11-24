<script lang="ts">
	import { enhance } from '$app/forms';
	import { invalidateAll } from '$app/navigation';
	import { Plus, SearchX } from '@lucide/svelte';
	import { getI18n } from '$lib/i18n/index.svelte';
	import { can } from '$lib/config/permissions';
	import type { ResourceDef } from '$lib/config/resources';
	import { toastSuccess } from '$lib/stores/toast';
	import type { FormState, Role } from '$lib/types';
	import type { ListData } from '$lib/server/resource';
	import { Button, Card, EmptyState, FormAlert, Modal, PageHeader, Pagination } from '$lib/components/shared';
	import ActionPanel from './ActionPanel.svelte';
	import DataTable from './DataTable.svelte';
	import ExportMenu from './ExportMenu.svelte';
	import FieldInputs from './FieldInputs.svelte';
	import FilterBar from './FilterBar.svelte';
	import UnavailableNotice from './UnavailableNotice.svelte';
	import { resDesc, resTitle } from './labels';

	let { def, data, role, base, form = null, staff = [], embedded = false }: { def: ResourceDef; data: ListData; role: Role; base: string; form?: FormState | null; staff?: { id: string; full_name: string }[]; embedded?: boolean } = $props();
	const { t } = getI18n();
	let open = $state(false);
	let loading = $state(false);
	const mine = $derived(form && form.op === 'create' ? form : null);
	const canCreate = $derived(!!def.create && can(role, def.create.permission));
	const hasFile = $derived(!!def.create?.fields.some((f) => f.type === 'file' || f.type === 'repeater'));
	const href = (row: Record<string, any>) => (def.detail === false ? null : def.detailHref ? def.detailHref.replace('{id}', row.id) : `${base}/${def.key}/${row.id}`);
	const rowActions = $derived(def.detail === false && !!def.actions?.length);
</script>

{#if !embedded}
	<PageHeader title={resTitle(t, def.scope, def.key)} subtitle={resDesc(t, def.key)}>
		{#snippet actions()}
			{#if def.exportable && !data.unavailable}<ExportMenu {def} />{/if}
			{#if canCreate}<Button onclick={() => (open = true)}>{#snippet icon()}<Plus size={18} />{/snippet}{t('rx.ui.create')}</Button>{/if}
		{/snippet}
	</PageHeader>
{/if}

<Card padded={false}>
	{#if def.filters?.length}<FilterBar filters={def.filters} values={data.filters} resetHref="{base}/{def.key}" />{/if}
	{#if data.unavailable}
		<UnavailableNotice endpoint={def.endpoint} />
	{:else if data.items.length === 0}
		<EmptyState icon={SearchX} title={t('rx.ui.noResults')} description={t('rx.ui.noResultsText')} />
	{:else}
		<DataTable cols={def.cols} rows={data.items} {href} />
		{#if rowActions}
			<div class="ra">{#each data.items as r (r.id)}<div class="r"><span class="mono">{r.id}</span><ActionPanel {def} row={r} {role} {staff} compact /></div>{/each}</div>
		{/if}
		<Pagination page={data.page} pageSize={data.pageSize} total={data.total} />
	{/if}
</Card>

{#if canCreate && def.create}
	<Modal bind:open title={t('rx.ui.create')} size="lg">
		<form id="create-{def.key}" method="POST" action="?/create" class="stack" enctype={hasFile ? 'multipart/form-data' : undefined}
			use:enhance={() => { loading = true; return async ({ result, update }) => { if (result.type === 'success') { toastSuccess(t('rx.ui.done')); open = false; await invalidateAll(); } else await update({ reset: false }); loading = false; }; }}>
			<FormAlert form={mine} />
			<FieldInputs fields={def.create.fields} errors={mine?.errors ?? {}} {staff} />
		</form>
		{#snippet footer()}
			<Button variant="ghost" onclick={() => (open = false)}>{t('common.cancel')}</Button>
			<Button type="submit" form="create-{def.key}" variant="brand" {loading}>{t('common.create')}</Button>
		{/snippet}
	</Modal>
{/if}

<style lang="scss">
	.ra { display: grid; gap: 0.4rem; padding: 1rem 1.35rem; border-top: 1px solid var(--border); background: var(--surface-2); .r { display: flex; justify-content: space-between; gap: 1rem; align-items: center; flex-wrap: wrap; } .mono { font-family: var(--font-mono); font-size: var(--fs-xs); color: var(--fg-muted); } }
</style>
