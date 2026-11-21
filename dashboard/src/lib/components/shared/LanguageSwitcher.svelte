<script lang="ts">
	import { Check, ChevronDown, Languages } from '@lucide/svelte';
	import { invalidateAll } from '$app/navigation';
	import { clickOutside } from '$lib/actions/clickOutside';
	import { getI18n } from '$lib/i18n/index.svelte';
	import { LOCALES, LOCALE_COOKIE, LOCALE_LABELS, type Locale } from '$lib/i18n/locales';

	let { variant = 'default', placement = 'down' }: { variant?: 'default' | 'light'; placement?: 'down' | 'up' } = $props();
	const i18n = getI18n();
	let open = $state(false);

	async function choose(locale: Locale) {
		open = false;
		if (locale === i18n.locale) return;
		document.cookie = `${LOCALE_COOKIE}=${locale}; Path=/; Max-Age=${60 * 60 * 24 * 365}; SameSite=Lax`;
		i18n.locale = locale; // bascule immédiate de l'UI…
		await invalidateAll(); // …puis rechargement des données serveur (contenus légaux, etc.)
	}
</script>

<div class="lang" use:clickOutside={() => (open = false)}>
	<button type="button" class="trigger {variant}" onclick={() => (open = !open)} aria-expanded={open} aria-haspopup="listbox" aria-label={i18n.t('nav.language')}>
		<Languages size={17} />
		<span class="lbl">{LOCALE_LABELS[i18n.locale].name}</span>
		<ChevronDown size={15} />
	</button>
	{#if open}
		<ul class:up={placement === 'up'} role="listbox" aria-label={i18n.t('nav.language')}>
			{#each LOCALES as l (l)}
				<li role="option" aria-selected={l === i18n.locale}>
					<button type="button" onclick={() => choose(l)}>
						<span class="flag">{LOCALE_LABELS[l].flag}</span>
						{LOCALE_LABELS[l].name}
						{#if l === i18n.locale}<Check size={16} />{/if}
					</button>
				</li>
			{/each}
		</ul>
	{/if}
</div>

<style lang="scss">
	.lang { position: relative; }
	.trigger { display: inline-flex; align-items: center; gap: 0.4rem; padding: 0.55rem 0.8rem; border: 1.5px solid var(--border-strong); border-radius: var(--radius); background: transparent; color: var(--fg); font-weight: 700; font-size: var(--fs-sm); &:hover { border-color: var(--primary); } &.light { color: #fff; border-color: rgb(255 255 255 / 0.28); &:hover { border-color: var(--brand-cyan); } } }
	ul { position: absolute; right: 0; top: calc(100% + 8px); min-width: 180px; background: var(--surface); color: var(--fg); border: 1px solid var(--border); border-radius: var(--radius); box-shadow: var(--shadow-lg); padding: 0.35rem; z-index: 10; animation: drop 0.15s var(--ease); }
	li button { width: 100%; display: flex; align-items: center; gap: 0.6rem; padding: 0.6rem 0.7rem; border: 0; background: none; border-radius: var(--radius-sm); font-weight: 600; text-align: left; &:hover { background: var(--surface-2); } :global(svg:last-child) { margin-left: auto; color: var(--primary); } }
	ul.up { top: auto; bottom: calc(100% + 8px); }
	@keyframes drop { from { opacity: 0; transform: translateY(-4px); } }
</style>
