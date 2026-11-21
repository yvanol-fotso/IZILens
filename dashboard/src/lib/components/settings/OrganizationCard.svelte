<script lang="ts">
	import { getI18n } from '$lib/i18n/index.svelte';
	import type { SessionUser } from '$lib/types';
	import { Badge, Card } from '$lib/components/shared';

	let { user }: { user: SessionUser } = $props();
	const { t } = getI18n();
	const org = $derived(user.organization);
</script>

<Card title={t('settings.organization.title')} description={t('settings.organization.readonly')}>
	{#if org}
		<dl>
			<div><dt>{t('common.name')}</dt><dd>{org.name}</dd></div>
			<div><dt>{t('settings.organization.slug')}</dt><dd class="mono">{org.slug}</dd></div>
			<div><dt>{t('settings.organization.modules')}</dt><dd class="mods">{#each org.enabled_modules as m (m)}<Badge tone="brand">{m}</Badge>{/each}</dd></div>
		</dl>
	{:else}<p class="muted">—</p>{/if}
</Card>

<style lang="scss">
	dl { display: grid; gap: 1rem; margin: 0; } dt { font-size: var(--fs-xs); color: var(--fg-muted); font-weight: 700; } dd { margin: 0.2rem 0 0; font-weight: 700; } .mods { display: flex; gap: 0.4rem; flex-wrap: wrap; }
</style>
