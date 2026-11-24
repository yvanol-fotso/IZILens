<script lang="ts">
	import { Check } from '@lucide/svelte';
	import { SERVICES, type ServiceId } from '$lib/config/services';
	import { getI18n } from '$lib/i18n/index.svelte';

	/** Sélection libre d'un ou plusieurs services ; renvoie les identifiants (kyc, kyb, liveness, monitoring). */
	let { selected = $bindable<string[]>([]) }: { selected?: string[] } = $props();
	const { t } = getI18n();
	const toggle = (id: ServiceId) => (selected = selected.includes(id) ? selected.filter((s) => s !== id) : [...selected, id]);
</script>

<div class="picker" role="group" aria-label={t('svc.overview.mainTitle')}>
	{#each SERVICES as s (s.id)}
		{@const Icon = s.icon}
		{@const on = selected.includes(s.id)}
		<button type="button" class:on style:--c={s.color} aria-pressed={on} onclick={() => toggle(s.id)}>
			<span class="ico"><Icon size={22} /></span>
			<span class="txt"><b>{t(`svc.items.${s.id}.code`)}</b><small>{t(`svc.items.${s.id}.name`)}</small></span>
			<span class="tick">{#if on}<Check size={16} />{/if}</span>
		</button>
	{/each}
</div>

<style lang="scss">
	.picker { display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 0.8rem; }
	button { display: flex; align-items: center; gap: 0.9rem; text-align: left; padding: 1rem 1.1rem; background: var(--surface); border: 2px solid var(--border-strong); border-radius: var(--radius); color: var(--fg); transition: border-color 0.15s, background 0.15s, transform 0.15s; &:hover { border-color: var(--c); } &.on { border-color: var(--c); background: color-mix(in srgb, var(--c) 9%, var(--surface)); } }
	.ico { width: 44px; height: 44px; border-radius: 13px; display: grid; place-items: center; background: color-mix(in srgb, var(--c) 15%, var(--surface)); color: var(--c); flex-shrink: 0; }
	.txt { display: grid; flex: 1; line-height: 1.3; small { color: var(--fg-muted); font-size: var(--fs-xs); } }
	.tick { width: 24px; height: 24px; border-radius: 50%; border: 2px solid var(--border-strong); display: grid; place-items: center; color: #fff; flex-shrink: 0; }
	.on .tick { background: var(--c); border-color: var(--c); }
</style>
