<script lang="ts">
	import { getI18n } from '$lib/i18n/index.svelte';
	import { PricingTables } from '$lib/components/billing';
	import { PageHeader, Card, Button } from '$lib/components/shared';
	import { DEFAULT_PRICING_GRID } from '$lib/config/pricing';
	import { demoHref } from '$lib/config/services';
	
	const { t } = getI18n();
</script>

<svelte:head>
	<title>{t('marketing.pricing.title')} | IZI LENS</title>
	<meta name="description" content={t('marketing.pricing.subtitle')} />
</svelte:head>

<div class="container marketing-pricing">
	<PageHeader 
		title={t('marketing.pricing.title')} 
		subtitle={t('marketing.pricing.subtitle')} 
	/>
	
	<PricingTables data={DEFAULT_PRICING_GRID} showSimulator={true} />
	
	<div class="faq-section">
		<Card title={t('marketing.pricing.faq')}>
			<p class="muted">{t('marketing.pricing.faqBilling')}</p>
			<p class="muted">{t('marketing.pricing.faqTaxes')}</p>
		</Card>
	</div>

	<div class="cta-section">
		<Card>
			<div class="cta-content">
				<div>
					<h3>{t('marketing.pricing.ctaTitle')}</h3>
					<p class="muted">{t('marketing.pricing.ctaText')}</p>
				</div>
				<div class="cta-actions">
					<Button href="/register" variant="brand">{t('marketing.pricing.start')}</Button>
					<Button href={demoHref} variant="outline">{t('marketing.pricing.contact')}</Button>
				</div>
			</div>
		</Card>
	</div>
</div>

<style lang="scss">
	.marketing-pricing { padding: 4rem 1rem; max-width: 1200px; margin: 0 auto; }
	.faq-section { margin-top: 3rem; max-width: 800px; margin-left: auto; margin-right: auto; }
	.cta-section { margin-top: 2rem; max-width: 800px; margin-left: auto; margin-right: auto; }
	.cta-content { display: flex; justify-content: space-between; align-items: center; gap: 2rem; flex-wrap: wrap; }
	.cta-content h3 { margin: 0 0 0.5rem 0; font-size: var(--fs-xl); }
	.cta-actions { display: flex; gap: 1rem; flex-wrap: wrap; }
	.muted { color: var(--fg-muted); font-size: var(--fs-sm); line-height: 1.6; margin-bottom: 1rem; }
	@media (max-width: 768px) {
		.cta-content { flex-direction: column; text-align: center; }
		.cta-actions { justify-content: center; }
	}
</style>