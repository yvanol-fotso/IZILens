<script lang="ts">
	import { enhance } from '$app/forms';
	import { invalidateAll } from '$app/navigation';
	import { getI18n } from '$lib/i18n/index.svelte';
	import { formatDate } from '$lib/utils/format';
	import { Badge, Button, Card } from '$lib/components/shared';

	let { sessions = [] }: { sessions?: { id: string; device?: string; ip_address?: string; last_seen_at?: string; current?: boolean }[] } = $props();
	const i18n = getI18n();
	const { t } = i18n;
</script>

<Card title={t('cli.sessions.title')} description={t('cli.sessions.subtitle')}>
	{#if sessions.length === 0}<p class="muted">{t('rx.ui.noResults')}</p>{:else}
		<ul>{#each sessions as s (s.id)}
			<li><div><b>{s.device ?? '—'}</b> {#if s.current}<Badge tone="success">{t('cli.sessions.current')}</Badge>{/if}<small>{s.ip_address ?? ''} · {formatDate(s.last_seen_at, i18n.locale, true)}</small></div>
				{#if !s.current}<form method="POST" action="?/sessionRevoke" use:enhance={() => async ({ update }) => { await update({ reset: false }); await invalidateAll(); }}><input type="hidden" name="id" value={s.id} /><Button type="submit" size="sm" variant="danger">{t('rx.a.revoke')}</Button></form>{/if}</li>
		{/each}</ul>
	{/if}
</Card>

<style lang="scss">
	ul { display: grid; gap: 0.6rem; } li { display: flex; justify-content: space-between; align-items: center; gap: 1rem; padding: 0.7rem 0.9rem; background: var(--surface-2); border-radius: var(--radius-sm); div { display: grid; } small { color: var(--fg-muted); } }
</style>
