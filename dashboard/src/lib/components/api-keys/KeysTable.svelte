<script lang="ts">
	import { enhance } from '$app/forms';
	import { KeyRound } from '@lucide/svelte';
	import { getI18n } from '$lib/i18n/index.svelte';
	import { formatDate } from '$lib/utils/format';
	import type { ApiKey } from '$lib/types';
	import { Badge, Button, EmptyState, Table } from '$lib/components/shared';

	let { keys }: { keys: ApiKey[] } = $props();
	const i18n = getI18n();
	const { t } = i18n;
	const state = (k: ApiKey) => (k.revoked_at || !k.is_active ? 'revoked' : k.expires_at && new Date(k.expires_at) < new Date() ? 'expired' : 'active');
</script>

{#if keys.length === 0}
	<EmptyState icon={KeyRound} title={t('apiKeys.empty.title')} description={t('apiKeys.empty.desc')} />
{:else}
	<Table caption={t('apiKeys.title')}>
		<thead><tr><th>{t('apiKeys.columns.name')}</th><th>{t('apiKeys.columns.prefix')}</th><th>{t('apiKeys.columns.created')}</th><th>{t('apiKeys.columns.lastUsed')}</th><th>{t('apiKeys.columns.expires')}</th><th>{t('apiKeys.columns.status')}</th><th></th></tr></thead>
		<tbody>
			{#each keys as k (k.id)}
				{@const s = state(k)}
				<tr>
					<td><b>{k.name}</b></td>
					<td class="mono">{k.prefix}…</td>
					<td>{formatDate(k.created_at, i18n.locale)}</td>
					<td>{k.last_used_at ? formatDate(k.last_used_at, i18n.locale, true) : t('common.never')}</td>
					<td>{k.expires_at ? formatDate(k.expires_at, i18n.locale) : '—'}</td>
					<td><Badge tone={s === 'active' ? 'success' : 'neutral'} dot>{s === 'active' ? t('common.active') : s === 'revoked' ? t('apiKeys.revoked') : t('apiKeys.expired')}</Badge></td>
					<td class="num">
						{#if s === 'active'}
							<form method="POST" action="?/revoke" use:enhance={({ cancel }) => { if (!confirm(t('apiKeys.revokeConfirm', { name: k.name }))) cancel(); }}>
								<input type="hidden" name="id" value={k.id} />
								<Button type="submit" size="sm" variant="danger">{t('apiKeys.revoke')}</Button>
							</form>
						{/if}
					</td>
				</tr>
			{/each}
		</tbody>
	</Table>
{/if}
