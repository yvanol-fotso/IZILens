<script lang="ts">
	import { enhance } from '$app/forms';
	import { getI18n } from '$lib/i18n/index.svelte';
	import type { FormState } from '$lib/types';
	import { Button, Card, Checkbox, FormAlert, Input, Select, Textarea } from '$lib/components/shared';

	/** Formulaire unique pour « contact général / devis » (kind=contact) et « démonstration » (kind=demo). */
	let { kind, form, presetType = 'sales', presetServices = [] }: { kind: 'contact' | 'demo'; form?: FormState | null; presetType?: string; presetServices?: string[] } = $props();
	const { t } = getI18n();
	const mine = $derived(form && form.kind === kind ? form : null);
	const err = (k: string) => (mine?.errors?.[k] ? t(mine.errors[k]) : undefined);
	const v = (k: string, d = '') => mine?.values?.[k] ?? d;
	let loading = $state(false);
	let type = $state(v('type', presetType));
	let services = $state<string[]>(presetServices);
	let sector = $state(v('sector', ''));
	let volume = $state(v('volume', ''));
	const types = ['sales', 'demo', 'partnership', 'integration', 'institutional', 'quote', 'developer', 'other'];
	const svc = ['kyc', 'kyb', 'liveness', 'monitoring', 'api', 'other'];
	const sectors = ['banks', 'fintech', 'micro', 'insurance', 'telecom', 'ecommerce', 'platforms'];
	const volumes = ['< 1 000', '1 000 – 10 000', '10 000 – 100 000', '> 100 000'];
	$effect(() => { if (presetServices.length) services = presetServices; });
</script>

<Card title={kind === 'demo' ? t('contact.demoForm.title') : t('contact.form.title')} description={kind === 'demo' ? t('contact.demoForm.text') : t('contact.form.text')}>
	<form method="POST" action="?/{kind}" class="stack" novalidate use:enhance={() => { loading = true; return async ({ update }) => { await update({ reset: false }); loading = false; }; }}>
		<FormAlert form={mine} />
		<!-- Leurre anti-spam : invisible pour les humains -->
		<div class="hp" aria-hidden="true"><label>Website<input type="text" name="website" tabindex="-1" autocomplete="off" /></label></div>

		<div class="two">
			<Input label={t('contact.form.fullName')} name="full_name" autocomplete="name" value={v('full_name')} error={err('full_name')} required />
			<Input label={t('contact.form.company')} name="company" autocomplete="organization" value={v('company')} error={err('company')} required />
		</div>
		<div class="two">
			<Input label={t('contact.form.email')} name="email" type="email" autocomplete="email" value={v('email')} error={err('email')} required />
			<Input label={t('contact.form.country')} name="country" autocomplete="country-name" value={v('country')} error={err('country')} required />
		</div>

		{#if kind === 'contact'}
			<div class="two">
				<Input label={t('contact.form.role')} name="role" value={v('role')} error={err('role')} required />
				<Input label="{t('contact.form.phone')} ({t('common.optional')})" name="phone" type="tel" autocomplete="tel" value={v('phone')} />
			</div>
			<div class="two">
				<Select label={t('contact.form.type')} name="type" bind:value={type} options={types.map((k) => ({ value: k, label: t(`contact.types.${k}`) }))} />
				<Input label={t('contact.form.subject')} name="subject" value={v('subject')} error={err('subject')} required />
			</div>
		{:else}
			<div class="two">
				<Select label={t('contact.form.sector')} name="sector" bind:value={sector} options={[{ value: '', label: t('contact.form.choose') }, ...sectors.map((k) => ({ value: k, label: t(`sol.sectors.${k}.name`) }))]} error={err('sector')} />
				<Select label={t('contact.form.volume')} name="volume" bind:value={volume} options={[{ value: '', label: t('contact.form.choose') }, ...volumes.map((x) => ({ value: x, label: x }))]} />
			</div>
		{/if}

		<fieldset>
			<legend>{t('contact.form.services')}</legend>
			<div class="svc">{#each svc as s (s)}<label><input type="checkbox" name="services" value={s} bind:group={services} />{t(`contact.services.${s}`)}</label>{/each}</div>
		</fieldset>

		<Textarea label={kind === 'demo' ? t('contact.form.project') : t('contact.form.message')} name={kind === 'demo' ? 'project' : 'message'} value={v(kind === 'demo' ? 'project' : 'message')} error={err(kind === 'demo' ? 'project' : 'message')} maxlength={4000} required />
		<p class="sens">{t('contact.form.sensitive')}</p>

		<Checkbox name="consent" error={err('consent')}>{t('contact.form.consent')} <a href="/privacy">{t('footer.privacy')}</a></Checkbox>
		{#if kind === 'contact'}<Checkbox name="marketing">{t('contact.form.marketing')}</Checkbox>{/if}

		<div><Button type="submit" variant="brand" size="lg" {loading}>{kind === 'demo' ? t('contact.demoForm.submit') : t('contact.form.submit')}</Button></div>
	</form>
</Card>

<style lang="scss">
	.two { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; } @media (max-width: 640px) { .two { grid-template-columns: 1fr; } }
	.hp { position: absolute; left: -9999px; width: 1px; height: 1px; overflow: hidden; }
	fieldset { border: 0; padding: 0; margin: 0; } legend { font-size: var(--fs-sm); font-weight: 700; margin-bottom: 0.6rem; }
	.svc { display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 0.5rem; label { display: flex; gap: 0.6rem; align-items: center; padding: 0.65rem 0.9rem; border: 1.5px solid var(--border-strong); border-radius: var(--radius-sm); font-size: var(--fs-sm); font-weight: 600; cursor: pointer; &:has(input:checked) { border-color: var(--primary); background: var(--primary-soft); } input { accent-color: var(--primary); } } }
	.sens { font-size: var(--fs-xs); color: var(--fg-muted); }
</style>
