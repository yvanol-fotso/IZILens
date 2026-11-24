<script lang="ts">
	import { Landmark, CreditCard, HandCoins, ShieldPlus, RadioTower, ShoppingCart, AppWindow } from '@lucide/svelte';
	import { reveal } from '$lib/actions/reveal';
	import { getI18n } from '$lib/i18n/index.svelte';
	import { Button, SectionHeader } from '$lib/components/shared';

	const { t } = getI18n();
	const sectors = [
		{ k: 'banks', icon: Landmark }, { k: 'fintech', icon: CreditCard }, { k: 'micro', icon: HandCoins }, { k: 'insurance', icon: ShieldPlus },
		{ k: 'telecom', icon: RadioTower }, { k: 'ecommerce', icon: ShoppingCart }, { k: 'platforms', icon: AppWindow }
	];
</script>

<section id="sectors" class="s">
	<div class="container">
		<SectionHeader title={t('home.sectors.title')}><p>{t('home.sectors.text')}</p></SectionHeader>
		<ul>
			{#each sectors as s, i (s.k)}
				{@const Icon = s.icon}
				<li use:reveal={{ delay: i * 50 }}><span class="ico"><Icon size={22} /></span><div><h3>{t(`home.sectors.items.${s.k}.title`)}</h3><p>{t(`home.sectors.items.${s.k}.desc`)}</p></div></li>
			{/each}
		</ul>
		<div class="btn"><Button href="/solutions" variant="brand" size="lg">{t('home.sectors.button')}</Button></div>
	</div>
</section>

<style lang="scss">
	.s { padding: 6rem 0; background: var(--bg); }
	ul { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 0.9rem; }
	li { display: flex; gap: 1rem; align-items: flex-start; padding: 1.2rem 1.3rem; background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius); }
	.ico { width: 46px; height: 46px; border-radius: 14px; display: grid; place-items: center; background: var(--primary-soft); color: var(--primary); flex-shrink: 0; }
	h3 { font-size: var(--fs-md); } p { color: var(--fg-muted); font-size: var(--fs-sm); margin-top: 0.15rem; }
	.btn { margin-top: 2.2rem; }
</style>
