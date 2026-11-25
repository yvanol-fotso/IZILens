<script lang="ts">
	import { getI18n } from '$lib/i18n/index.svelte';
	import { Activity, Fingerprint, FileCheck2 } from '@lucide/svelte';

	let { usage = {
		kyc: { count: 45, quota: 100 },
		kyb: { count: 2, quota: 10 },
		biometrics: { count: 120, quota: 50 }
	} } = $props();
	
	const { t } = getI18n();
	const services = [
		{ key: 'kyc', icon: FileCheck2, label: 'KYC', color: 'var(--brand-cyan)' },
		{ key: 'kyb', icon: Activity, label: 'KYB', color: 'var(--accent-orange)' },
		{ key: 'biometrics', icon: Fingerprint, label: 'Biométrie', color: 'var(--primary)' }
	];
</script>

<div class="usage-grid">
	{#each services as s (s.key)}
		{@const data = usage[s.key] || { count: 0, quota: 0 }}
		{@const percent = data.quota > 0 ? Math.min((data.count / data.quota) * 100, 100) : 0}
		{@const isOver = data.count > data.quota}
		
		<div class="usage-card">
			<div class="head">
				<span class="label">
					<svelte:component this={s.icon} size={16} /> 
					{s.label}
				</span>
				<span class="value" class:over={isOver}>
					{data.count} <small>/ {data.quota}</small>
				</span>
			</div>
			<div class="bar-bg">
				<div class="bar-fill" style:width="{percent}%" style:background={isOver ? 'var(--danger)' : s.color}></div>
			</div>
			{#if isOver}
				<p class="over-text">{t('cli.billing.overage') || 'Dépassement facturé à l\'unité'}</p>
			{/if}
		</div>
	{/each}
</div>

<style lang="scss">
	.usage-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; }
	.usage-card { background: var(--surface-2); padding: 1rem; border-radius: var(--radius); border: 1px solid var(--border); }
	.head { display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem; }
	.label { display: flex; align-items: center; gap: 0.4rem; font-size: var(--fs-sm); font-weight: 700; color: var(--fg-muted); }
	.value { font-weight: 800; font-size: var(--fs-lg); }
	.value small { font-weight: 500; font-size: var(--fs-xs); color: var(--fg-muted); }
	.value.over { color: var(--danger); }
	.bar-bg { height: 8px; background: var(--border); border-radius: 99px; overflow: hidden; }
	.bar-fill { height: 100%; border-radius: 99px; transition: width 0.5s ease; }
	.over-text { color: var(--danger); font-size: var(--fs-xs); font-weight: 700; margin-top: 0.4rem; }
</style>