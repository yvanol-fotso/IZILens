<script lang="ts">
	import { getI18n } from '$lib/i18n/index.svelte';
	import { UploadForm } from '$lib/components/verifications';
	import { PageHeader } from '$lib/components/shared';

	let { form } = $props();
	const { t } = getI18n();
</script>

<PageHeader title={t('verifications.new')} subtitle={t('verifications.upload.subtitle')} />
<div class="wrap"><UploadForm {form} /></div>

<style>
	.wrap { max-width: 860px; }
</style>
