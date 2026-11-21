<script lang="ts">
	import { FileText, ScanFace, ShieldCheck, Settings2, Blocks } from '@lucide/svelte';
	import { reveal } from '$lib/actions/reveal';
	import { getI18n } from '$lib/i18n/index.svelte';

	const { t } = getI18n();
	const steps = [
		{ key: 'collect', icon: FileText, color: 'var(--primary)' },
		{ key: 'verify', icon: ScanFace, color: 'var(--accent-purple)' },
		{ key: 'assess', icon: ShieldCheck, color: 'var(--accent-mint)' },
		{ key: 'act', icon: Settings2, color: 'var(--accent-orange)' },
		{ key: 'integrate', icon: Blocks, color: 'var(--accent-rose)' }
	];
</script>

<section id="platform" class="section">
	<div class="container">
		<header use:reveal>
			<h2>{t('home.platform.title')}</h2>
			<p>{t('home.platform.subtitle')}</p>
		</header>
		<ol>
			{#each steps as s, i (s.key)}
				{@const Icon = s.icon}
				<li style:--c={s.color} use:reveal={{ delay: i * 70 }}>
					<span class="ico"><Icon size={24} /></span>
					<span class="n">{i + 1}</span>
					<h3>{t(`home.platform.steps.${s.key}.title`)}</h3>
					<p>{t(`home.platform.steps.${s.key}.desc`)}</p>
				</li>
			{/each}
		</ol>
	</div>
</section>

<style lang="scss">
	.section { padding: 6rem 0; background: var(--bg); }
	header { max-width: 640px; margin-bottom: 3.2rem; h2 { font-size: var(--fs-3xl); } p { margin-top: 1rem; color: var(--fg-muted); font-size: var(--fs-lg); } }
	ol { display: grid; grid-template-columns: repeat(5, 1fr); gap: 0; position: relative; }
	ol::before { content: ''; position: absolute; top: 28px; left: 28px; right: 28px; height: 2px; background: repeating-linear-gradient(90deg, var(--border-strong) 0 8px, transparent 8px 16px); }
	li { position: relative; padding-right: 1.5rem; display: grid; gap: 0.5rem; align-content: start; }
	.ico { width: 56px; height: 56px; border-radius: 18px; display: grid; place-items: center; background: color-mix(in srgb, var(--c) 14%, var(--surface)); color: var(--c); border: 2px solid var(--bg); position: relative; z-index: 1; margin-bottom: 0.6rem; }
	.n { position: absolute; top: -6px; left: 40px; z-index: 2; width: 22px; height: 22px; border-radius: 50%; background: var(--brand-navy); color: #fff; font-size: 0.7rem; font-weight: 800; display: grid; place-items: center; }
	h3 { font-size: var(--fs-lg); }
	li p { color: var(--fg-muted); font-size: var(--fs-sm); }
	@media (max-width: 980px) { ol { grid-template-columns: 1fr; gap: 2rem; } ol::before { top: 28px; bottom: 28px; left: 28px; right: auto; width: 2px; height: auto; background: repeating-linear-gradient(180deg, var(--border-strong) 0 8px, transparent 8px 16px); } li { padding-left: 4.5rem; padding-right: 0; } .ico { position: absolute; left: 0; top: 0; } .n { left: 40px; top: -6px; } }
</style>
