<script lang="ts">
	import { getI18n } from '$lib/i18n/index.svelte';
	import { EcosystemGrid, LeadershipAmbition, StorySection } from '$lib/components/about';
	import { PageHero } from '$lib/components/shared';
	const { t, list } = getI18n();
</script>

<svelte:head><title>{t('nav.about')} · IZI LENS</title><meta name="description" content={list('about.story')[0]} /></svelte:head>

<PageHero kicker={t('about.hero.kicker')} title={t('about.hero.title')} />
<StorySection />
<EcosystemGrid />
<LeadershipAmbition />
