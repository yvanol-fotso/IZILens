<script lang="ts">
	import { reveal } from '$lib/actions/reveal';
	import { getI18n } from '$lib/i18n/index.svelte';
	import { Button, SectionHeader } from '$lib/components/shared';
	const { t } = getI18n();
</script>

<section id="api" class="s">
	<div class="container wrap">
		<div use:reveal>
			<SectionHeader title={t('home.api.title')} tone="light"><p>{t('home.api.p1')}</p><p>{t('home.api.p2')}</p><p>{t('home.api.p3')}</p></SectionHeader>
			<div class="row">
				<Button href="/developers" size="lg">{t('home.api.primary')}</Button>
				<Button href="/developers#docs" size="lg" variant="outline" class="ghost-light">{t('home.api.secondary')}</Button>
			</div>
		</div>
		<pre class="code" aria-hidden="true" use:reveal={{ delay: 100 }}><code><span class="c"># illustration</span>
POST /v1/kyc/verifications
&#123; "reference": "ORDER-1042",
  "document_type": "national_id" &#125;

<span class="c">→ 201 Created</span>
&#123; "id": "ver_8f2c…", "status": "processing" &#125;</code></pre>
	</div>
</section>

<style lang="scss">
	.s { padding: 6rem 0; background: var(--brand-navy); color: #fff; }
	.wrap { display: grid; grid-template-columns: 1.1fr 1fr; gap: 4rem; align-items: center; }
	.row { display: flex; gap: 0.8rem; flex-wrap: wrap; :global(.ghost-light) { color: #fff; border-color: rgb(255 255 255 / 0.3); &:hover { border-color: var(--brand-cyan) !important; color: var(--brand-cyan) !important; } } }
	.code { margin: 0; padding: 1.6rem; border-radius: var(--radius-lg); background: #04142a; border: 1px solid #16406b; color: #cfe3fb; font-size: 0.86rem; line-height: 1.7; overflow-x: auto; box-shadow: var(--shadow-lg); .c { color: #6f8fb5; } }
	@media (max-width: 900px) { .wrap { grid-template-columns: 1fr; gap: 2.5rem; } }
</style>
