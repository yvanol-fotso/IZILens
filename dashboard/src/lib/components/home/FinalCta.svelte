<script lang="ts">
	import { demoHref, quoteHref } from '$lib/config/services';
	import { getI18n } from '$lib/i18n/index.svelte';
	import { Button, CtaBand } from '$lib/components/shared';
	const { t } = getI18n();
</script>

<CtaBand title={t('home.cta.title')}>
	<p>{t('home.cta.p1')}</p>
	<p>{t('home.cta.p2')}</p>
	{#snippet actions()}
		<Button href={demoHref} size="lg">{t('home.cta.primary')}</Button>
		<Button href={quoteHref()} size="lg" variant="outline" class="ghost-light">{t('home.cta.secondary')}</Button>
	{/snippet}
</CtaBand>
