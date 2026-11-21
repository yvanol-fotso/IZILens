<script lang="ts">
	import { enhance } from '$app/forms';
	import { getI18n } from '$lib/i18n/index.svelte';
	import { ASSIGNABLE_ROLES } from '$lib/config/permissions';
	import { formatDate } from '$lib/utils/format';
	import type { UserRecord } from '$lib/types';
	import { Avatar, Badge, Button, Table } from '$lib/components/shared';

	let { members, currentUserId }: { members: UserRecord[]; currentUserId: string } = $props();
	const i18n = getI18n();
	const { t } = i18n;
</script>

<Table caption={t('team.title')}>
	<thead><tr><th>{t('team.columns.member')}</th><th>{t('team.columns.role')}</th><th>{t('team.columns.status')}</th><th>{t('team.columns.lastLogin')}</th><th></th></tr></thead>
	<tbody>
		{#each members as m (m.id)}
			<tr>
				<td><div class="who"><Avatar name={m.full_name} /><div><b>{m.full_name}</b><small>{m.email}</small></div></div></td>
				<td>
					{#if m.id === currentUserId || m.role === 'super_admin'}
						<Badge tone="brand">{t(`roles.${m.role}`)}</Badge>
					{:else}
						<form method="POST" action="?/update" use:enhance={() => async ({ update }) => update({ reset: false })}>
							<input type="hidden" name="id" value={m.id} />
							<select name="role" value={m.role} aria-label={t('team.columns.role')} onchange={(e) => e.currentTarget.form?.requestSubmit()}>
								{#each ASSIGNABLE_ROLES as r (r)}<option value={r}>{t(`roles.${r}`)}</option>{/each}
							</select>
						</form>
					{/if}
				</td>
				<td><Badge tone={m.is_active ? 'success' : 'neutral'} dot>{m.is_active ? t('common.active') : t('common.inactive')}</Badge></td>
				<td>{m.last_login_at ? formatDate(m.last_login_at, i18n.locale, true) : t('common.never')}</td>
				<td class="num">
					{#if m.id !== currentUserId && m.role !== 'super_admin'}
						<form method="POST" action="?/update" use:enhance={() => async ({ update }) => update({ reset: false })}>
							<input type="hidden" name="id" value={m.id} /><input type="hidden" name="is_active" value={String(!m.is_active)} />
							<Button type="submit" size="sm" variant={m.is_active ? 'ghost' : 'outline'}>{m.is_active ? t('team.deactivate') : t('team.activate')}</Button>
						</form>
					{/if}
				</td>
			</tr>
		{/each}
	</tbody>
</Table>

<style lang="scss">
	.who { display: flex; gap: 0.75rem; align-items: center; div { display: grid; line-height: 1.25; } small { color: var(--fg-muted); } }
	select { padding: 0.4rem 0.6rem; border: 1.5px solid var(--border-strong); border-radius: var(--radius-sm); background: var(--surface); font-size: var(--fs-sm); font-weight: 600; }
</style>
