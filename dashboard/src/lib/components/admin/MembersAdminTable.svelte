<script lang="ts">
	import { getI18n } from '$lib/i18n/index.svelte';
	import { formatDate } from '$lib/utils/format';
	import type { UserRecord } from '$lib/types';
	import { Avatar, Badge, EmptyState, Table } from '$lib/components/shared';

	let { members, orgNames = {} }: { members: UserRecord[]; orgNames?: Record<string, string> } = $props();
	const i18n = getI18n();
	const { t } = i18n;
</script>

{#if members.length === 0}
	<EmptyState title={t('admin.tenants.noMembers')} />
{:else}
	<Table caption={t('admin.members.title')}>
		<thead><tr><th>{t('team.columns.member')}</th><th>{t('admin.members.org')}</th><th>{t('team.columns.role')}</th><th>{t('team.columns.status')}</th><th>{t('team.columns.lastLogin')}</th></tr></thead>
		<tbody>
			{#each members as m (m.id)}
				<tr>
					<td><div class="who"><Avatar name={m.full_name} size={32} /><div><b>{m.full_name}</b><small>{m.email}</small></div></div></td>
					<td>{m.organization_id ? (orgNames[m.organization_id] ?? m.organization_id.slice(0, 8)) : 'Kafintech'}</td>
					<td><Badge tone="brand">{t(`roles.${m.role}`)}</Badge></td>
					<td><Badge tone={m.is_active ? 'success' : 'neutral'} dot>{m.is_active ? t('common.active') : t('common.inactive')}</Badge></td>
					<td>{m.last_login_at ? formatDate(m.last_login_at, i18n.locale, true) : t('common.never')}</td>
				</tr>
			{/each}
		</tbody>
	</Table>
{/if}

<style lang="scss">
	.who { display: flex; gap: 0.7rem; align-items: center; div { display: grid; line-height: 1.25; } small { color: var(--fg-muted); } }
</style>
