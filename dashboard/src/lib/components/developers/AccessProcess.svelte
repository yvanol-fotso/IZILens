<script lang="ts">
	import { reveal } from '$lib/actions/reveal';
	import { getI18n } from '$lib/i18n/index.svelte';
	import { SectionHeader } from '$lib/components/shared';
	const { t } = getI18n();
	const steps = ['s1', 's2', 's3', 's4'];
</script>

<section id="access" class="s">
	<div class="container">
		<SectionHeader title={t('dev.access.title')} />
		<ol>{#each steps as s, i (s)}<li use:reveal={{ delay: i * 80 }}><span class="n">{i + 1}</span><h3>{t(`dev.access.steps.${s}.title`)}</h3><p>{t(`dev.access.steps.${s}.desc`)}</p></li>{/each}</ol>
		<p class="note">{t('dev.access.note')}</p>
	</div>
</section>

<style lang="scss">
	.s { padding: 5.5rem 0; background: var(--bg-soft); border-block: 1px solid var(--border); }
	ol { display: grid; grid-template-columns: repeat(auto-fit, minmax(230px, 1fr)); gap: 1.4rem; counter-reset: s; } li { display: grid; gap: 0.5rem; align-content: start; }
	.n { width: 46px; height: 46px; border-radius: 50%; background: var(--brand-navy); color: var(--brand-cyan); font-weight: 800; display: grid; place-items: center; } h3 { font-size: var(--fs-lg); } p { color: var(--fg-muted); font-size: var(--fs-sm); }
	.note { margin-top: 2rem; padding: 1rem 1.2rem; background: var(--info-bg); color: var(--info); border-radius: var(--radius); font-weight: 600; font-size: var(--fs-sm) !important; }
</style>
