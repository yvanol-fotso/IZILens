<script lang="ts">
	import { ScrollText } from '@lucide/svelte';
	import { getI18n } from '$lib/i18n/index.svelte';
	import { formatDate } from '$lib/utils/format';
	import type { AuditLog } from '$lib/types';
	import { Badge, EmptyState, Table } from '$lib/components/shared';

	let { logs }: { logs: AuditLog[] } = $props();
	const i18n = getI18n();
	const { t } = i18n;
</script>

{#if logs.length === 0}
	<EmptyState icon={ScrollText} title={t('audit.empty.title')} description={t('audit.empty.desc')} />
{:else}
	<Table caption={t('audit.title')}>
		<thead><tr><th>{t('audit.columns.date')}</th><th>{t('audit.columns.actor')}</th><th>{t('audit.columns.action')}</th><th>{t('audit.columns.resource')}</th><th>{t('audit.columns.ip')}</th></tr></thead>
		<tbody>
			{#each logs as l (l.id)}
				<tr>
					<td>{formatDate(l.created_at, i18n.locale, true)}</td>
					<td><Badge tone={l.actor_type === 'system' ? 'neutral' : l.actor_type === 'api_key' ? 'info' : 'brand'}>{t(`audit.actors.${l.actor_type}`)}</Badge></td>
					<td class="mono">{l.action}</td>
					<td class="mono">{l.resource_type ?? '—'}{l.resource_id ? ` · ${l.resource_id.slice(0, 8)}` : ''}</td>
					<td class="mono">{l.ip_address ?? '—'}</td>
				</tr>
			{/each}
		</tbody>
	</Table>
{/if}
