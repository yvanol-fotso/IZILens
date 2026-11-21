<script lang="ts">
	import { env } from '$env/dynamic/public';
	import { getI18n } from '$lib/i18n/index.svelte';
	import { Badge, Button, Card, CodeBlock } from '$lib/components/shared';

	let { apiBase, healthy }: { apiBase: string; healthy: boolean } = $props();
	const { t } = getI18n();
	const create = $derived(`curl -X POST ${apiBase}/kyc/cases \\
  -H "X-API-Key: izi_XXXXXXXX..." \\
  -F "document_type=cni_cm" \\
  -F "reference=ORDER-1042" \\
  -F "front=@recto.jpg" \\
  -F "back=@verso.jpg"`);
	const read = $derived(`curl ${apiBase}/kyc/cases/<case_id> \\
  -H "X-API-Key: izi_XXXXXXXX..."`);
</script>

<div class="stack">
	<Card title={t('developers.health')}>
		<div class="row"><Badge tone={healthy ? 'success' : 'danger'} dot>{healthy ? t('app.backend.ok') : t('app.backend.down')}</Badge><span class="muted">{t('developers.baseUrl')} : <code>{apiBase}</code></span></div>
	</Card>
	<Card title="1 · {t('developers.step1')}"><p class="muted">{t('developers.step1Text')}</p><div class="gap"><Button href="/app/api-keys" variant="outline" size="sm">{t('app.nav.apiKeys')}</Button></div></Card>
	<Card title="2 · {t('developers.step2')}"><CodeBlock code={create} /></Card>
	<Card title="3 · {t('developers.step3')}"><CodeBlock code={read} /></Card>
	{#if env.PUBLIC_DOCS_URL}<Button href={env.PUBLIC_DOCS_URL} variant="brand">{t('developers.docs')}</Button>{/if}
</div>

<style>
	.gap { margin-top: 0.8rem; } code { font-size: var(--fs-xs); }
</style>
