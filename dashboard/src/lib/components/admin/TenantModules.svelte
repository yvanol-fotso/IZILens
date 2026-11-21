<script lang="ts">
	import { enhance } from '$app/forms';
	import { getI18n } from '$lib/i18n/index.svelte';
	import { MODULES } from '$lib/config/modules';
	import { toastSuccess } from '$lib/stores/toast';
	import type { Organization } from '$lib/types';
	import { Button, Card, Switch } from '$lib/components/shared';

	let { tenant }: { tenant: Organization } = $props();
	const { t } = getI18n();
	let checked = $state<Record<string, boolean>>(Object.fromEntries(MODULES.map((m) => [m.id, tenant.enabled_modules.includes(m.id)])));
	let loading = $state(false);
</script>

<Card title={t('admin.tenants.modules')}>
	<form method="POST" action="?/modules" class="stack" use:enhance={() => { loading = true; return async ({ result, update }) => { if (result.type === 'success') toastSuccess(t('admin.tenants.updated')); await update({ reset: false }); loading = false; }; }}>
		{#each MODULES as m (m.id)}
			<Switch bind:checked={checked[m.id]} label={t(`modules.${m.id}.title`)} description={t(`modules.${m.id}.desc`)} />
			{#if checked[m.id]}<input type="hidden" name="modules" value={m.id} />{/if}
		{/each}
		<div><Button type="submit" variant="brand" {loading}>{t('common.save')}</Button></div>
	</form>
</Card>
