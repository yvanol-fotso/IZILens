<script lang="ts">
	import { reveal } from '$lib/actions/reveal';
	import { getI18n } from '$lib/i18n/index.svelte';
	import { SectionHeader } from '$lib/components/shared';
	import Img from '$lib/components/shared/Img.svelte';
	const { t } = getI18n();
	const steps = ['s1', 's2', 's3', 's4'];
</script>

<section id="how" class="s">
	<div class="container">
		<SectionHeader title={t('home.how.title')} />
		<ol>
			{#each steps as s, i (s)}
				<li use:reveal={{ delay: i * 80 }}>
					<span class="n">{i + 1}</span>
					<h3>{t(`home.how.steps.${s}.title`)}</h3>
					<p>{t(`home.how.steps.${s}.desc`)}</p>
				</li>
			{/each}
		</ol>
		<figure class="dash" use:reveal={{ delay: 120 }}>
			<Img src="/marketing/home/how-dashboard" alt={t('home.images.how')} ratio="1200/460" />
		</figure>
	</div>
</section>

<style lang="scss">
	.s { padding: 6rem 0; background: var(--bg-soft); border-block: 1px solid var(--border); }
	ol { display: grid; grid-template-columns: repeat(4, 1fr); gap: 1.5rem; position: relative; &::before { content: ''; position: absolute; top: 24px; left: 24px; right: 24px; height: 2px; background: repeating-linear-gradient(90deg, var(--border-strong) 0 8px, transparent 8px 16px); } }
	li { position: relative; display: grid; gap: 0.5rem; align-content: start; }
	.n { width: 48px; height: 48px; border-radius: 50%; background: var(--brand-navy); color: var(--brand-cyan); font-weight: 800; display: grid; place-items: center; border: 4px solid var(--bg-soft); position: relative; z-index: 1; margin-bottom: 0.5rem; }
	h3 { font-size: var(--fs-lg); } p { color: var(--fg-muted); font-size: var(--fs-sm); }
	.dash { margin: 3.5rem 0 0; --img-radius: var(--radius-lg); border-radius: var(--radius-lg); box-shadow: var(--shadow-md); }
	@media (max-width: 900px) { ol { grid-template-columns: 1fr; &::before { display: none; } } .dash { margin-top: 2.5rem; } }
</style>
