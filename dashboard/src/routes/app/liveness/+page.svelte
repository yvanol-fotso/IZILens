<script lang="ts">
	import { getI18n } from '$lib/i18n/index.svelte';
	import { HowItWorks, LinkGenerator, ThresholdCard } from '$lib/components/liveness';
	import { PageHeader } from '$lib/components/shared';
	let { data, form } = $props();
	const { t } = getI18n();
</script>

<PageHeader title={t('liveness.title')} subtitle={t('liveness.subtitle')} />
<div class="stack">
	<LinkGenerator />
	<div class="two"><ThresholdCard level={data.triggerLevel} {form} /><HowItWorks /></div>
</div>

<style>
	.two { display: grid; grid-template-columns: 1fr 1fr; gap: 1.25rem; }
	@media (max-width: 860px) { .two { grid-template-columns: 1fr; } }
</style>
