<script lang="ts">
	import { quoteHref } from '$lib/config/services';
	import { getI18n } from '$lib/i18n/index.svelte';
	import { Button, SectionHeader, ServicePicker } from '$lib/components/shared';
	const { t } = getI18n();
	let selected = $state<string[]>([]);
</script>

<section class="s">
	<div class="container">
		<SectionHeader title={t('svc.compose.title')}><p>{t('svc.compose.text')}</p></SectionHeader>
		<ServicePicker bind:selected />
		<div class="row btn"><Button href={quoteHref(selected)} variant="brand" size="lg">{t('svc.compose.button')}</Button>{#if selected.length}<span class="muted">{t('common.selected', { count: selected.length })}</span>{/if}</div>
	</div>
</section>

<style lang="scss">
	.s { padding: 5.5rem 0; background: var(--bg-soft); border-block: 1px solid var(--border); } .btn { margin-top: 1.6rem; }
</style>
