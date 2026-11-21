<script lang="ts">
	let { segments, total, centerLabel }: { segments: { label: string; value: number; color: string }[]; total?: number; centerLabel?: string } = $props();
	const sum = $derived(total ?? segments.reduce((a, s) => a + s.value, 0));
	const R = 52;
	const C = 2 * Math.PI * R;
	const arcs = $derived.by(() => {
		let offset = 0;
		return segments.map((s) => {
			const len = sum ? (s.value / sum) * C : 0;
			const arc = { ...s, len, offset };
			offset += len;
			return arc;
		});
	});
</script>

<div class="donut">
	<svg viewBox="0 0 140 140" role="img" aria-label={centerLabel}>
		<circle cx="70" cy="70" r={R} class="track" />
		{#each arcs as a (a.label)}
			{#if a.len > 0}
				<circle cx="70" cy="70" r={R} fill="none" stroke={a.color} stroke-width="16" stroke-dasharray="{a.len} {C - a.len}" stroke-dashoffset={-a.offset} transform="rotate(-90 70 70)" />
			{/if}
		{/each}
		<text x="70" y="68" text-anchor="middle" class="n">{sum}</text>
		{#if centerLabel}<text x="70" y="86" text-anchor="middle" class="l">{centerLabel}</text>{/if}
	</svg>
	<ul>
		{#each segments as s (s.label)}
			<li><i style:background={s.color}></i><span>{s.label}</span><b>{s.value}</b></li>
		{/each}
	</ul>
</div>

<style lang="scss">
	.donut { display: flex; align-items: center; gap: 1.5rem; flex-wrap: wrap; }
	svg { width: 150px; height: 150px; flex-shrink: 0; }
	.track { fill: none; stroke: var(--surface-3); stroke-width: 16; }
	.n { font-size: 26px; font-weight: 800; fill: var(--fg); }
	.l { font-size: 9px; font-weight: 600; fill: var(--fg-muted); }
	ul { display: grid; gap: 0.5rem; flex: 1; min-width: 150px; }
	li { display: flex; align-items: center; gap: 0.55rem; font-size: var(--fs-sm); i { width: 10px; height: 10px; border-radius: 3px; } span { flex: 1; color: var(--fg-muted); } b { font-variant-numeric: tabular-nums; } }
</style>
