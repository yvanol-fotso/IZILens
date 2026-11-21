<script lang="ts">
	import { getI18n } from '$lib/i18n/index.svelte';
	import { Badge, Card, PageHeader } from '$lib/components/shared';
	let { data } = $props();
	const { t } = getI18n();
</script>

<PageHeader title={t('admin.system.title')} subtitle={t('admin.system.subtitle')} />
<div class="stack wrap">
	<Card>
		<dl>
			<div><dt>{t('admin.system.backend')}</dt><dd><Badge tone={data.healthy ? 'success' : 'danger'} dot>{data.healthy ? t('app.backend.ok') : t('app.backend.down')}</Badge></dd></div>
			<div><dt>{t('admin.system.baseUrl')}</dt><dd class="mono">{data.baseUrl}</dd></div>
			<div><dt>{t('admin.system.oidc')}</dt><dd><Badge tone={data.oidc ? 'success' : 'warning'}>{data.oidc ? t('admin.system.configured') : t('admin.system.missing')}</Badge></dd></div>
			<div><dt>{t('admin.system.loginFormat')}</dt><dd class="mono">{data.loginFormat}</dd></div>
		</dl>
	</Card>
</div>

<style lang="scss">
	.wrap { max-width: 720px; } dl { display: grid; gap: 1.2rem; margin: 0; } dt { font-size: var(--fs-xs); font-weight: 700; color: var(--fg-muted); margin-bottom: 0.3rem; } dd { margin: 0; font-weight: 600; }
</style>
