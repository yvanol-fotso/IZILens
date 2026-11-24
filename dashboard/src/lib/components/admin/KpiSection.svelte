<script lang="ts">
	import { getI18n } from '$lib/i18n/index.svelte';
	import { StatCard } from '$lib/components/shared';
	import { formatNumber } from '$lib/utils/format';

	/** Affiche les paires clé/valeur numériques d'un bloc du tableau de bord (libellés rx.f.<clé>). */
	let { title, data, money = false, currency = 'CAD' }: { title: string; data?: Record<string, any>; money?: boolean; currency?: string } = $props();
	const i18n = getI18n();
	const { t } = i18n;
	const entries = $derived(Object.entries(data ?? {}).filter(([, v]) => typeof v === 'number' || typeof v === 'string'));
	const fmt = (k: string, v: any) => {
		if (typeof v !== 'number') return String(v);
		if (money && /revenue|consumption|amount|unpaid|received|payments/.test(k)) return new Intl.NumberFormat(i18n.locale === 'fr' ? 'fr-CA' : 'en-CA', { style: 'currency', currency, maximumFractionDigits: 0 }).format(v);
		if (/percent|availability/.test(k)) return `${formatNumber(v, i18n.locale, 2)} %`;
		return formatNumber(v, i18n.locale, 2);
	};
	const label = (k: string) => (t(`rx.f.${k}`) === `rx.f.${k}` ? k.replace(/_/g, ' ') : t(`rx.f.${k}`));
</script>

<section>
	<h2>{title}</h2>
	{#if entries.length}
		<div class="g">{#each entries as [k, v] (k)}<StatCard label={label(k)} value={fmt(k, v)} />{/each}</div>
	{:else}<p class="muted">{t('rx.ui.noResults')}</p>{/if}
</section>

<style lang="scss">
	section { margin-bottom: 2rem; } h2 { font-size: var(--fs-xl); margin-bottom: 0.9rem; } .g { display: grid; gap: 1rem; grid-template-columns: repeat(auto-fit, minmax(190px, 1fr)); }
</style>
