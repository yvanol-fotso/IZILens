<script lang="ts">
	import { ChevronLeft, ChevronRight } from '@lucide/svelte';
	import { page as pageState } from '$app/state';
	import { getI18n } from '$lib/i18n/index.svelte';

	let { page, pageSize, total }: { page: number; pageSize: number; total: number } = $props();
	const { t } = getI18n();
	const pages = $derived(Math.max(1, Math.ceil(total / pageSize)));

	function hrefFor(p: number) {
		const q = new URLSearchParams(pageState.url.searchParams);
		q.set('page', String(p));
		return `?${q.toString()}`;
	}
</script>

{#if pages > 1}
	<nav class="pg" aria-label="Pagination">
		<span class="info">{t('common.page', { page, pages })}</span>
		<div class="btns">
			<a class="b" class:off={page <= 1} href={page > 1 ? hrefFor(page - 1) : undefined} aria-label={t('common.previous')} aria-disabled={page <= 1}><ChevronLeft size={18} /></a>
			<a class="b" class:off={page >= pages} href={page < pages ? hrefFor(page + 1) : undefined} aria-label={t('common.next')} aria-disabled={page >= pages}><ChevronRight size={18} /></a>
		</div>
	</nav>
{/if}

<style lang="scss">
	.pg { display: flex; justify-content: space-between; align-items: center; padding: 0.9rem 1.1rem; border-top: 1px solid var(--border); }
	.info { font-size: var(--fs-sm); color: var(--fg-muted); }
	.btns { display: flex; gap: 0.4rem; }
	.b { width: 36px; height: 36px; display: grid; place-items: center; border: 1.5px solid var(--border-strong); border-radius: var(--radius-sm); color: var(--fg); &:hover { border-color: var(--primary); text-decoration: none; } &.off { opacity: 0.4; pointer-events: none; } }
</style>
