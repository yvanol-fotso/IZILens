<script lang="ts">
	import { enhance } from '$app/forms';
	import { getI18n } from '$lib/i18n/index.svelte';
	import { toastSuccess } from '$lib/stores/toast';
	import type { FormState } from '$lib/types';
	import { Button, Card, FormAlert } from '$lib/components/shared';

	let { level, form }: { level: string; form?: FormState | null } = $props();
	const { t } = getI18n();
	let value = $state(level);
	let loading = $state(false);
	const opts = ['off', 'medium', 'high'];
</script>

<Card title={t('liveness.threshold.title')} description={t('liveness.threshold.desc')}>
	<form method="POST" action="?/threshold" class="stack" use:enhance={() => { loading = true; return async ({ result, update }) => { if (result.type === 'success') toastSuccess(t('liveness.threshold.saved')); await update({ reset: false }); loading = false; }; }}>
		<FormAlert {form} />
		<fieldset>
			{#each opts as o (o)}
				<label class:on={value === o}><input type="radio" name="trigger_level" value={o} bind:group={value} />{t(`liveness.threshold.${o}`)}</label>
			{/each}
		</fieldset>
		<div><Button type="submit" variant="brand" {loading}>{t('common.save')}</Button></div>
	</form>
</Card>

<style lang="scss">
	fieldset { border: 0; padding: 0; margin: 0; display: grid; gap: 0.5rem; }
	label { display: flex; align-items: center; gap: 0.7rem; padding: 0.8rem 1rem; border: 1.5px solid var(--border-strong); border-radius: var(--radius); cursor: pointer; font-weight: 600; font-size: var(--fs-sm); &.on { border-color: var(--primary); background: var(--primary-soft); } input { accent-color: var(--primary); } }
</style>
