<script lang="ts">
	import { getI18n } from '$lib/i18n/index.svelte';
	import { Coverage, FinalCta, Hero, PlatformSteps, WhyUs } from '$lib/components/home';
	const { t } = getI18n();
</script>

<svelte:head>
	<title>{t('meta.siteTitle')}</title>
	<meta name="description" content={t('meta.siteDescription')} />
</svelte:head>

<Hero />
<PlatformSteps />
<Coverage />
<WhyUs />
<FinalCta />
