<script lang="ts">
	import { getI18n } from '$lib/i18n/index.svelte';
	import { OrganizationCard, PreferencesForm, ProfileForm, SecurityCard } from '$lib/components/settings';
	import { PageHeader } from '$lib/components/shared';
	let { data, form } = $props();
	const { t } = getI18n();
</script>

<PageHeader title={t('settings.title')} subtitle={t('settings.subtitle')} />
<div class="grid">
	<ProfileForm user={data.user} {form} />
	<PreferencesForm />
	<SecurityCard {form} />
	<OrganizationCard user={data.user} />
</div>

<style>
	.grid { display: grid; grid-template-columns: 1fr 1fr; gap: 1.25rem; align-items: start; }
	@media (max-width: 960px) { .grid { grid-template-columns: 1fr; } }
</style>
