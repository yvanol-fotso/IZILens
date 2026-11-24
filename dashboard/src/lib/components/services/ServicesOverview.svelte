<script lang="ts">
	import { ArrowRight } from '@lucide/svelte';
	import { reveal } from '$lib/actions/reveal';
	import { SERVICES } from '$lib/config/services';
	import { getI18n } from '$lib/i18n/index.svelte';
	import { SectionHeader } from '$lib/components/shared';
	const { t } = getI18n();
</script>

<section id="solutions" class="s">
	<div class="container">
		<SectionHeader title={t('svc.overview.title')}><p>{t('svc.overview.text')}</p></SectionHeader>
		<h3 class="sub">{t('svc.overview.mainTitle')}</h3>
		<div class="grid">
			{#each SERVICES as s, i (s.id)}
				{@const Icon = s.icon}
				<a href="/services/{s.slug}" class="card" style:--c={s.color} use:reveal={{ delay: i * 70 }}>
					<span class="num">0{i + 1}</span>
					<span class="ico"><Icon size={26} /></span>
					<h3>{t(`svc.items.${s.id}.code`)} <small>| {t(`svc.items.${s.id}.name`)}</small></h3>
					<p>{t(`svc.items.${s.id}.short`)}</p>
					<span class="more">{t(`svc.items.${s.id}.cta`)}<ArrowRight size={16} /></span>
				</a>
			{/each}
		</div>
		<p class="note">{t('svc.overview.note')}</p>
	</div>
</section>

<style lang="scss">
	.s { padding: 5.5rem 0; background: var(--bg); } .sub { font-size: var(--fs-xl); margin-bottom: 1.2rem; }
	.grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 1rem; }
	.card { position: relative; display: grid; gap: 0.7rem; align-content: start; padding: 1.8rem; background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius-lg); color: var(--fg); text-decoration: none !important; transition: transform 0.2s var(--ease), border-color 0.2s; &:hover { transform: translateY(-4px); border-color: var(--c); } }
	.num { position: absolute; top: 1.2rem; right: 1.4rem; font-weight: 800; color: var(--surface-3); font-size: 2.4rem; line-height: 1; }
	.ico { width: 56px; height: 56px; border-radius: 17px; display: grid; place-items: center; background: color-mix(in srgb, var(--c) 14%, var(--surface)); color: var(--c); }
	h3 { font-size: var(--fs-xl); small { font-size: var(--fs-sm); font-weight: 600; color: var(--fg-muted); } } p { color: var(--fg-muted); font-size: var(--fs-sm); }
	.more { display: inline-flex; align-items: center; gap: 0.4rem; font-weight: 700; color: var(--primary); font-size: var(--fs-sm); }
	.note { margin-top: 1.6rem; color: var(--fg-muted); font-size: var(--fs-sm); }
</style>
