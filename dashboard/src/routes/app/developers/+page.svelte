<script lang="ts">
	import { getI18n } from '$lib/i18n/index.svelte';
	import { QuickStart } from '$lib/components/developers';
	import { PageHeader } from '$lib/components/shared';
	let { data } = $props();
	const { t } = getI18n();
</script>

<PageHeader title={t('developers.title')} subtitle={t('developers.subtitle')} />
<div class="wrap"><QuickStart apiBase={data.apiBase} healthy={data.healthy} /></div>

<style>
	.wrap { max-width: 860px; }
</style>
