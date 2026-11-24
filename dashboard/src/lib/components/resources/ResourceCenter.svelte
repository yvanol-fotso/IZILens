<script lang="ts">
	import { Search, BookOpen, FileText, Code2, Lightbulb, ShieldCheck, Newspaper } from '@lucide/svelte';
	import { getI18n } from '$lib/i18n/index.svelte';
	import { translate } from '$lib/i18n/translate';
	import { Badge, Input } from '$lib/components/shared';

	const i18n = getI18n();
	const { t, list } = i18n;
	let query = $state('');
	let category = $state('all');
	const rubriques = [
		{ k: 'blog', icon: Newspaper }, { k: 'guides', icon: BookOpen }, { k: 'api', icon: Code2 }, { k: 'cases', icon: Lightbulb }, { k: 'security', icon: ShieldCheck }
	];
	const norm = (s: string) => s.toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g, '');
	const q = $derived(norm(query.trim()));
	const matches = (s: string) => !q || norm(s).includes(q);
	const faq = $derived(
		Array.from({ length: 6 }, (_, i) => ({
			c: translate(i18n.locale, `res.faq.items.${i}.c`),
			q: translate(i18n.locale, `res.faq.items.${i}.q`),
			a: translate(i18n.locale, `res.faq.items.${i}.a`)
		})).filter((f) => (category === 'all' || f.c === category) && (matches(f.q) || matches(f.a)))
	);
	const cats = ['general', 'kyc', 'kyb', 'bio', 'api'];
</script>

<section class="s">
	<div class="container">
		<div class="search"><Input label={t('res.searchLabel')} name="q" type="search" icon={Search} placeholder={t('res.searchPlaceholder')} bind:value={query} /></div>

		<div class="grid">
			{#each rubriques as r (r.k)}
				{@const Icon = r.icon}
				{@const items = list(`res.rubriques.${r.k}.items`).filter(matches)}
				{#if items.length || matches(t(`res.rubriques.${r.k}.title`))}
					<article>
						<span class="ico"><Icon size={24} /></span>
						<h3>{t(`res.rubriques.${r.k}.title`)}</h3>
						<p>{t(`res.rubriques.${r.k}.desc`)}</p>
						<ul>{#each (items.length ? items : list(`res.rubriques.${r.k}.items`)) as it (it)}<li>{it}</li>{/each}</ul>
						<Badge tone="neutral">{t('res.soon')}</Badge>
					</article>
				{/if}
			{/each}
		</div>

		<section id="faq" class="faq">
			<h2>{t('res.faq.title')}</h2>
			<div class="cats" role="group">
				<button type="button" class:on={category === 'all'} onclick={() => (category = 'all')}>{t('common.all')}</button>
				{#each cats as c (c)}<button type="button" class:on={category === c} onclick={() => (category = c)}>{t(`res.faq.categories.${c}`)}</button>{/each}
			</div>
			{#if faq.length}
				<div class="list">{#each faq as f (f.q)}<details><summary>{f.q}</summary><p>{f.a}</p></details>{/each}</div>
			{:else}<p class="muted">{t('res.faq.empty')}</p>{/if}
		</section>
	</div>
</section>

<style lang="scss">
	.s { padding: 3.5rem 0 5.5rem; background: var(--bg); } .search { max-width: 620px; margin-bottom: 2.4rem; }
	.grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap: 1rem; }
	article { display: grid; gap: 0.7rem; align-content: start; padding: 1.8rem; background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius-lg); justify-items: start; }
	.ico { width: 52px; height: 52px; border-radius: 16px; display: grid; place-items: center; background: var(--primary-soft); color: var(--primary); } h3 { font-size: var(--fs-xl); } article > p { color: var(--fg-muted); font-size: var(--fs-sm); }
	ul { display: grid; gap: 0.4rem; font-size: var(--fs-sm); width: 100%; li { padding: 0.5rem 0.8rem; background: var(--surface-2); border-radius: var(--radius-sm); font-weight: 600; } }
	.faq { margin-top: 4rem; } h2 { font-size: var(--fs-2xl); margin-bottom: 1.2rem; }
	.cats { display: flex; flex-wrap: wrap; gap: 0.5rem; margin-bottom: 1.4rem; button { padding: 0.5rem 1rem; border-radius: var(--radius-pill); border: 1.5px solid var(--border-strong); background: var(--surface); font-weight: 700; font-size: var(--fs-sm); &.on { background: var(--brand-navy); color: #fff; border-color: var(--brand-navy); } } }
	.list { display: grid; gap: 0.6rem; max-width: 820px; } details { background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius); padding: 1rem 1.2rem; } summary { font-weight: 700; cursor: pointer; } details p { margin-top: 0.7rem; color: var(--fg-muted); }
</style>
