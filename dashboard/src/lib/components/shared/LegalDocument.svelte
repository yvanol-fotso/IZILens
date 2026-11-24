<script lang="ts">
	import type { Snippet } from 'svelte';
	import { getI18n } from '$lib/i18n/index.svelte';
	import { formatDate } from '$lib/utils/format';
	import Markdown from './Markdown.svelte';

	/** Gabarit commun des pages légales (confidentialité, conditions, cookies). */
	let { doc, extra }: { doc: { title: string; updated: string; html: string; toc: { id: string; text: string }[] }; extra?: Snippet } = $props();
	const i18n = getI18n();
</script>

<svelte:head><title>{doc.title} · IZI LENS</title></svelte:head>

<section class="hero">
	<div class="container">
		<h1>{doc.title}</h1>
		{#if doc.updated}<p>{i18n.t('legal.updated', { date: formatDate(doc.updated, i18n.locale) })}</p>{/if}
	</div>
</section>

<div class="container layout">
	<aside aria-label={i18n.t('legal.toc')}>
		<strong>{i18n.t('legal.toc')}</strong>
		<ol>
			{#each doc.toc as item (item.id)}
				<li><a href="#{item.id}">{item.text}</a></li>
			{/each}
		</ol>
	</aside>
	<article>
		<p class="notice">{i18n.t('legal.draftNotice')}</p>
		<Markdown html={doc.html} />
		{#if extra}<div class="extra">{@render extra()}</div>{/if}
	</article>
</div>

<style lang="scss">
	.hero { background: var(--brand-navy); color: #fff; padding: calc(var(--header-h) + 3.5rem) 0 3.5rem; background-image: radial-gradient(60% 120% at 85% 0%, rgb(34 199 242 / 0.18), transparent 60%); }
	h1 { font-size: var(--fs-3xl); max-width: 22ch; }
	.hero p { margin-top: 0.8rem; color: #9db4d1; }
	.layout { display: grid; grid-template-columns: 240px minmax(0, 1fr); gap: 3.5rem; padding: 3rem 0 5rem; align-items: start; }
	aside { position: sticky; top: calc(var(--header-h) + 24px); display: grid; gap: 0.8rem; font-size: var(--fs-sm); strong { font-size: var(--fs-sm); } ol { display: grid; gap: 0.15rem; border-left: 2px solid var(--border); } a { display: block; padding: 0.35rem 0.9rem; color: var(--fg-muted); margin-left: -2px; border-left: 2px solid transparent; &:hover { color: var(--primary); border-left-color: var(--primary); text-decoration: none; } } }
	.notice { font-size: var(--fs-xs); background: var(--warning-bg); color: var(--warning); padding: 0.6rem 0.9rem; border-radius: var(--radius-sm); margin-bottom: 1.5rem; max-width: 72ch; }
	.extra { margin-top: 2rem; }
	@media (max-width: 860px) { .layout { grid-template-columns: 1fr; gap: 1.5rem; } aside { position: static; } }
</style>
