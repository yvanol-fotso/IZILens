<script lang="ts">
	import { getI18n } from '$lib/i18n/index.svelte';
	import { formatDate } from '$lib/utils/format';

	let { data, height = 180, labelMode = 'date' }: { data: { label?: string; date?: string; value: number }[]; height?: number; labelMode?: 'date' | 'label' } = $props();
	const i18n = getI18n();
	const max = $derived(Math.max(1, ...data.map((d) => d.value)));
	const label = (d: { label?: string; date?: string }) => (labelMode === 'date' && d.date ? formatDate(d.date, i18n.locale).replace(/\s?\d{4}/, '') : (d.label ?? ''));
</script>

<figure>
	<div class="bars" style:height="{height}px" role="img" aria-label="chart">
		{#each data as d, i (i)}
			<div class="col" title="{label(d)} : {d.value}">
				<span class="val">{d.value || ''}</span>
				<span class="bar" style:height="{(d.value / max) * 100}%" class:zero={d.value === 0}></span>
			</div>
		{/each}
	</div>
	<div class="axis">
		{#each data as d, i (i)}<span class:hide={data.length > 8 && i % 2 === 1}>{label(d)}</span>{/each}
	</div>
</figure>

<style lang="scss">
	figure { margin: 0; }
	.bars { display: flex; align-items: flex-end; gap: 6px; border-bottom: 1px solid var(--border); }
	.col { flex: 1; height: 100%; display: flex; flex-direction: column; justify-content: flex-end; align-items: center; gap: 4px; min-width: 0; }
	.val { font-size: 0.68rem; font-weight: 700; color: var(--fg-muted); min-height: 1em; }
	.bar { width: 100%; max-width: 34px; border-radius: 6px 6px 0 0; background: linear-gradient(180deg, var(--brand-cyan), var(--primary)); transition: height 0.5s var(--ease); min-height: 3px; &.zero { background: var(--surface-3); } }
	.axis { display: flex; gap: 6px; margin-top: 0.45rem; span { flex: 1; text-align: center; font-size: 0.66rem; color: var(--fg-subtle); white-space: nowrap; overflow: hidden; text-overflow: clip; &.hide { visibility: hidden; } } }
</style>
