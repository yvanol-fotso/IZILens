<script lang="ts">
	import { getI18n } from '$lib/i18n/index.svelte';
	import { ApiSection, FinalCta, Hero, HowItWorks, Presentation, PricingSection, SectorsSection, SecuritySection, ServicesSection, WhyUs } from '$lib/components/home';
	const { t } = getI18n();
</script>

<svelte:head>
	<title>IZI LENS — {t('site.slogan')}</title>
	<meta name="description" content={t('home.hero.text1')} />
</svelte:head>

<Hero />
<Presentation />
<ServicesSection />
<WhyUs />
<HowItWorks />
<SectorsSection />
<ApiSection />
<SecuritySection />
<PricingSection />
<FinalCta />
