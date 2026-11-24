<script lang="ts">
	import { Check, X, ExternalLink } from '@lucide/svelte';
	import { getI18n } from '$lib/i18n/index.svelte';
	import { formatDate, formatNumber, formatPercent } from '$lib/utils/format';
	import type { Col } from '$lib/config/resources';
	import { Badge, Table } from '$lib/components/shared';
	import { fieldLabel, optLabel, toneFor } from './labels';

	type Row = Record<string, any>;
	let { cols, rows, href }: { cols: Col[]; rows: Row[]; /** (row) => lien de la fiche */ href?: (row: Row) => string | null } = $props();
	const i18n = getI18n();
	const { t } = i18n;

	const money = (v: unknown, cur?: string) =>
		typeof v === 'number' || (typeof v === 'string' && v !== '' && !Number.isNaN(Number(v)))
			? new Intl.NumberFormat(i18n.locale === 'fr' ? 'fr-CA' : 'en-CA', { style: 'currency', currency: cur || 'CAD', maximumFractionDigits: ['XOF', 'XAF'].includes(cur ?? '') ? 0 : 2 }).format(Number(v))
			: '—';
</script>

<Table>
	<thead><tr>{#each cols as c (c.key)}<th class:num={c.type === 'money' || c.type === 'number' || c.type === 'percent'}>{fieldLabel(t, c.key)}</th>{/each}</tr></thead>
	<tbody>
		{#each rows as row, i (row.id ?? i)}
			<tr>
				{#each cols as c (c.key)}
					{@const v = row[c.key]}
					{@const link = c.link ? href?.(row) : null}
					<td class:num={c.type === 'money' || c.type === 'number' || c.type === 'percent'} class:mono={c.type === 'mono'}>
						{#if v === null || v === undefined || v === ''}<span class="muted">—</span>
						{:else if c.type === 'status' || c.type === 'badge' || c.type === 'risk'}<Badge tone={c.type === 'badge' ? 'neutral' : toneFor(v)} dot={c.type !== 'badge'}>{optLabel(t, v)}</Badge>
						{:else if c.type === 'bool'}{#if v === true || v === 'true'}<Check size={16} color="var(--success)" />{:else}<X size={16} color="var(--fg-subtle)" />{/if}
						{:else if c.type === 'list'}<span class="chips">{#each Array.isArray(v) ? v : [v] as x (x)}<Badge tone="brand">{optLabel(t, x)}</Badge>{/each}</span>
						{:else if c.type === 'date'}{formatDate(v, i18n.locale)}
						{:else if c.type === 'datetime'}{formatDate(v, i18n.locale, true)}
						{:else if c.type === 'money'}{money(v, c.currencyKey ? row[c.currencyKey] : row.currency)}
						{:else if c.type === 'number'}{formatNumber(Number(v), i18n.locale, 2)}
						{:else if c.type === 'percent'}{formatPercent(Number(v), i18n.locale)}
						{:else if c.type === 'file'}<a href={String(v)} rel="noopener"><ExternalLink size={15} /> PDF</a>
						{:else if link}<a class="cell-link" href={link}>{v}</a>
						{:else}{typeof v === 'object' ? JSON.stringify(v) : v}{/if}
					</td>
				{/each}
			</tr>
		{/each}
	</tbody>
</Table>

<style lang="scss">
	.chips { display: flex; gap: 0.25rem; flex-wrap: wrap; }
	td.mono { font-family: var(--font-mono); font-size: var(--fs-xs); }
</style>
