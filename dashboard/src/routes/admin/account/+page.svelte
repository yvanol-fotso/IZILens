<script lang="ts">
	import { getI18n } from '$lib/i18n/index.svelte';
	import { MfaCard, PreferencesForm, ProfileForm, SecurityCard, SessionsCard } from '$lib/components/settings';
	import { PageHeader } from '$lib/components/shared';
	let { data, form } = $props();
	const { t } = getI18n();
</script>

<PageHeader title={t('adm.account.title')} subtitle={t('adm.account.subtitle')} />
{#if data.setup && data.user.mfa_enabled === false}<p class="warn" role="alert">{t('adm.account.mfaRequired')}</p>{/if}
<div class="grid">
	<MfaCard user={data.user} {form} passkeys={data.account.passkeys} />
	<SecurityCard {form} />
	<ProfileForm user={data.user} {form} />
	<PreferencesForm />
	<SessionsCard sessions={data.account.sessions} />
</div>

<style>
	.warn { margin-bottom: 1rem; padding: 0.9rem 1.1rem; background: var(--warning-bg); color: var(--warning); border-radius: var(--radius); font-weight: 700; }
	.grid { display: grid; grid-template-columns: 1fr 1fr; gap: 1.25rem; align-items: start; } @media (max-width: 960px) { .grid { grid-template-columns: 1fr; } }
</style>
