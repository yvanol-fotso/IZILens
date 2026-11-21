<script lang="ts">
	import { Building2 } from '@lucide/svelte';
	import { getI18n } from '$lib/i18n/index.svelte';
	import { formatDate } from '$lib/utils/format';
	import type { Organization } from '$lib/types';
	import { Badge, EmptyState, Table } from '$lib/components/shared';

	let { tenants }: { tenants: Organization[] } = $props();
	const i18n = getI18n();
	const { t } = i18n;
</script>

{#if tenants.length === 0}
	<EmptyState icon={Building2} title={t('common.noData')} />
{:else}
	<Table caption={t('admin.tenants.title')}>
		<thead><tr><th>{t('admin.tenants.columns.name')}</th><th>{t('admin.tenants.columns.slug')}</th><th>{t('admin.tenants.columns.modules')}</th><th>{t('admin.tenants.columns.status')}</th><th>{t('admin.tenants.columns.created')}</th></tr></thead>
		<tbody>
			{#each tenants as o (o.id)}
				<tr>
					<td><a class="cell-link" href="/app/admin/tenants/{o.id}">{o.name}</a></td>
					<td class="mono">{o.slug}</td>
					<td><div class="mods">{#each o.enabled_modules as m (m)}<Badge tone="brand">{m}</Badge>{/each}</div></td>
					<td><Badge tone={o.is_active ? 'success' : 'neutral'} dot>{o.is_active ? t('common.active') : t('common.inactive')}</Badge></td>
					<td>{formatDate(o.created_at, i18n.locale)}</td>
				</tr>
			{/each}
		</tbody>
	</Table>
{/if}

<style>
	.mods { display: flex; gap: 0.3rem; flex-wrap: wrap; }
</style>
