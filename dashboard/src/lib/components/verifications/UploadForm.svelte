<script lang="ts">
	import { enhance } from '$app/forms';
	import { ImagePlus, X } from '@lucide/svelte';
	import { getI18n } from '$lib/i18n/index.svelte';
	import { formatBytes } from '$lib/utils/format';
	import type { FormState } from '$lib/types';
	import { Button, Card, FormAlert, Input, Select } from '$lib/components/shared';

	let { form }: { form?: FormState | null } = $props();
	const { t } = getI18n();
	let loading = $state(false);
	let reference = $state('');
	let docType = $state('cni_cm');
	let files = $state<{ front: File | null; back: File | null }>({ front: null, back: null });
	let previews = $state<{ front: string; back: string }>({ front: '', back: '' });
	let over = $state<'front' | 'back' | null>(null);

	function pick(side: 'front' | 'back', list: FileList | null | undefined, input: HTMLInputElement) {
		const f = list?.[0] ?? null;
		files[side] = f;
		if (previews[side]) URL.revokeObjectURL(previews[side]);
		previews[side] = f ? URL.createObjectURL(f) : '';
		if (!f) input.value = '';
	}
</script>

<Card title={t('verifications.upload.title')} description={t('verifications.upload.subtitle')}>
	<form method="POST" enctype="multipart/form-data" class="stack" use:enhance={() => { loading = true; return async ({ update }) => { await update({ reset: false }); loading = false; }; }}>
		<FormAlert {form} />
		<div class="two">
			<Select label={t('verifications.upload.docType')} name="document_type" bind:value={docType} options={[{ value: 'cni_cm', label: t('docTypes.cni_cm') }]} />
			<Input label="{t('verifications.upload.reference')} ({t('common.optional')})" name="reference" bind:value={reference} hint={t('verifications.upload.referenceHint')} maxlength={64} />
		</div>

		<fieldset class="declared">
			<legend>{t('verifications.upload.declaredTitle')}</legend>
			<p class="hint">{t('verifications.upload.declaredHint')}</p>
			<div class="two">
				<Input label={t('verifications.upload.surname')} name="declared_surname" required maxlength={80} />
				<Input label={t('verifications.upload.givenNames')} name="declared_given_names" required maxlength={80} />
			</div>
			<div class="two">
				<Input label={t('verifications.upload.birthDate')} name="declared_date_of_birth" type="date" required />
				<Input label="{t('verifications.upload.nationality')} ({t('common.optional')})" name="declared_nationality" maxlength={60} />
			</div>
		</fieldset>

		<div class="two">
			{#each ['front', 'back'] as const as side (side)}
				<div class="drop-wrap">
					<span class="lbl">{t(side === 'front' ? 'verifications.upload.front' : 'verifications.upload.back')}{side === 'back' ? ` (${t('common.optional')})` : ''}</span>
					<label class="drop" class:over={over === side} class:filled={!!files[side]} ondragover={(e) => { e.preventDefault(); over = side; }} ondragleave={() => (over = null)} ondrop={(e) => { e.preventDefault(); over = null; const inp = e.currentTarget.querySelector('input')!; inp.files = e.dataTransfer!.files; pick(side, inp.files, inp); }}>
						<input type="file" name={side} accept="image/jpeg,image/png" required={side === 'front'} onchange={(e) => pick(side, e.currentTarget.files, e.currentTarget)} />
						{#if previews[side]}
							<img src={previews[side]} alt="" />
							<span class="meta">{files[side]?.name} · {formatBytes(files[side]?.size)}</span>
						{:else}
							<ImagePlus size={30} />
							<span>{t('verifications.upload.dropHint')}</span>
							<small>{side === 'back' ? t('verifications.upload.backHint') : t('verifications.upload.sizeHint')}</small>
						{/if}
					</label>
				</div>
			{/each}
		</div>

		<div class="row"><Button type="submit" size="lg" {loading}>{t('verifications.upload.submit')}</Button><Button href="/app/verifications" variant="ghost">{t('common.cancel')}</Button></div>
	</form>
</Card>

<style lang="scss">
	.declared { border: 1px solid var(--border); border-radius: var(--radius-lg); padding: 1rem; display: grid; gap: 0.75rem; legend { font-weight: 700; font-size: var(--fs-sm); padding: 0 0.4rem; } .hint { margin: 0; font-size: var(--fs-xs); color: var(--fg-subtle); } }
	.two { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; }
	.lbl { font-size: var(--fs-sm); font-weight: 700; display: block; margin-bottom: 0.4rem; }
	.drop { position: relative; display: grid; place-items: center; align-content: center; gap: 0.4rem; text-align: center; min-height: 220px; padding: 1rem; border: 2px dashed var(--border-strong); border-radius: var(--radius-lg); background: var(--surface-2); color: var(--fg-muted); cursor: pointer; overflow: hidden; transition: border-color 0.15s, background 0.15s; font-size: var(--fs-sm); small { font-size: var(--fs-xs); color: var(--fg-subtle); }
		&:hover, &.over { border-color: var(--primary); background: var(--primary-soft); color: var(--primary); }
		&.filled { border-style: solid; padding: 0; align-content: stretch; }
		input { position: absolute; inset: 0; opacity: 0; cursor: pointer; }
		img { width: 100%; height: 220px; object-fit: contain; background: #0003; }
		.meta { position: absolute; left: 0; right: 0; bottom: 0; padding: 0.4rem; background: rgb(0 0 0 / 0.55); color: #fff; font-size: var(--fs-xs); } }
	@media (max-width: 700px) { .two { grid-template-columns: 1fr; } }
</style>
