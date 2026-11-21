<script lang="ts">
	import { getI18n } from '$lib/i18n/index.svelte';
	import { AnalyticsCharts } from '$lib/components/analytics';
	import { PageHeader } from '$lib/components/shared';
	let { data } = $props();
	const { t } = getI18n();
</script>

<PageHeader title={t('analytics.title')} subtitle={t('analytics.subtitle')} />
<AnalyticsCharts stats={data.stats} />
