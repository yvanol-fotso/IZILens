<script lang="ts">
	import { Building2, CircleCheck, Users } from '@lucide/svelte';
	import { getI18n } from '$lib/i18n/index.svelte';
	import { StatCard } from '$lib/components/shared';
	let { orgs, active, members }: { orgs: number; active: number; members: number } = $props();
	const { t } = getI18n();
</script>

<div class="g">
	<StatCard label={t('admin.stats.tenants')} value={orgs} icon={Building2} />
	<StatCard label={t('admin.stats.activeTenants')} value={active} icon={CircleCheck} tone="success" />
	<StatCard label={t('admin.stats.members')} value={members} icon={Users} tone="info" />
</div>

<style>
	.g { display: grid; gap: 1rem; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); }
</style>
