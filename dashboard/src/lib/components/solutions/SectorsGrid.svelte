<script lang="ts">
	import { Landmark, CreditCard, HandCoins, ShieldPlus, RadioTower, ShoppingCart, AppWindow } from '@lucide/svelte';
	import { reveal } from '$lib/actions/reveal';
	import { SERVICES } from '$lib/config/services';
	import { getI18n } from '$lib/i18n/index.svelte';
	import { BulletList, SectionHeader } from '$lib/components/shared';

	/** compact = liste courte (page Services) · sinon sept cartes détaillées (page Solutions). */
	let { compact = false, title, text, note }: { compact?: boolean; title?: string; text?: string; note?: string } = $props();
	const { t, list } = getI18n();
	const sectors = [
		{ k: 'banks', icon: Landmark }, { k: 'fintech', icon: CreditCard }, { k: 'micro', icon: HandCoins }, { k: 'insurance', icon: ShieldPlus },
		{ k: 'telecom', icon: RadioTower }, { k: 'ecommerce', icon: ShoppingCart }, { k: 'platforms', icon: AppWindow }
	];
</script>

<section id="sectors" class="s">
	<div class="container">
		<SectionHeader title={title ?? t('sol.sectorsTitle')}>{#if text}<p>{text}</p>{/if}</SectionHeader>
		{#if compact}
			<ul class="chips">{#each sectors as s (s.k)}{@const Icon = s.icon}<li><Icon size={18} />{t(`sol.sectors.${s.k}.name`)}</li>{/each}</ul>
			{#if note}<p class="note">{note}</p>{/if}
		{:else}
			<div class="grid">
				{#each sectors as s, i (s.k)}
					{@const Icon = s.icon}
					<article use:reveal={{ delay: (i % 3) * 70 }}>
						<span class="ico"><Icon size={26} /></span>
						<h3>{t(`sol.sectors.${s.k}.name`)}</h3>
						<p class="tag">{t(`sol.sectors.${s.k}.tagline`)}</p>
						<p>{t(`sol.sectors.${s.k}.desc`)}</p>
						<h4>{t('sol.needs')}</h4>
						<BulletList items={list(`sol.sectors.${s.k}.needs`)} />
						<div class="mods"><span>{t('common.servicesFor')} :</span>{#each SERVICES as sv (sv.id)}<a href="/services/{sv.slug}">{t(`svc.items.${sv.id}.code`)}</a>{/each}</div>
					</article>
				{/each}
			</div>
		{/if}
	</div>
</section>

<style lang="scss">
	.s { padding: 5.5rem 0; background: var(--bg); }
	.chips { display: flex; flex-wrap: wrap; gap: 0.7rem; li { display: inline-flex; align-items: center; gap: 0.55rem; padding: 0.7rem 1.1rem; background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius-pill); font-weight: 600; font-size: var(--fs-sm); :global(svg) { color: var(--primary); } } }
	.note { margin-top: 1.4rem; color: var(--fg-muted); font-size: var(--fs-sm); }
	.grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(340px, 1fr)); gap: 1.2rem; }
	article { display: grid; gap: 0.7rem; align-content: start; padding: 1.9rem; background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius-lg); }
	.ico { width: 56px; height: 56px; border-radius: 17px; display: grid; place-items: center; background: var(--primary-soft); color: var(--primary); }
	h3 { font-size: var(--fs-xl); } .tag { font-weight: 700; color: var(--primary); } article p { color: var(--fg-muted); font-size: var(--fs-sm); }
	h4 { font-size: var(--fs-sm); margin-top: 0.5rem; } :global(article li) { font-size: var(--fs-sm); }
	.mods { display: flex; flex-wrap: wrap; gap: 0.4rem; align-items: center; margin-top: 0.6rem; padding-top: 0.9rem; border-top: 1px solid var(--border); font-size: var(--fs-xs); span { color: var(--fg-muted); font-weight: 700; } a { padding: 0.2rem 0.6rem; border-radius: var(--radius-pill); background: var(--primary-soft); font-weight: 700; } }
</style>
