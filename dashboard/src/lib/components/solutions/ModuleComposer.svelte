<script lang="ts">
	import { quoteHref } from '$lib/config/services';
	import { getI18n } from '$lib/i18n/index.svelte';
	import { Button, SectionHeader, ServicePicker } from '$lib/components/shared';
	const { t } = getI18n();
	let selected = $state<string[]>([]);
</script>

<section id="compose" class="s">
	<div class="container">
		<SectionHeader title={t('sol.modular.title')}><p>{t('sol.modular.text')}</p></SectionHeader>
		<ServicePicker bind:selected />
		<p class="hint">{t('sol.modular.hint')}</p>
		<div class="row"><Button href={quoteHref(selected)} variant="brand" size="lg">{t('sol.modular.button')}</Button>{#if selected.length}<span class="muted">{t('common.selected', { count: selected.length })}</span>{/if}</div>
	</div>
</section>

<style lang="scss">
	.s { padding: 5.5rem 0; background: var(--bg-soft); border-block: 1px solid var(--border); } .hint { margin: 1.2rem 0; color: var(--fg-muted); font-size: var(--fs-sm); }
</style>
