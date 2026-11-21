<script lang="ts">
	import { CircleAlert, CircleCheck } from '@lucide/svelte';
	import { getI18n } from '$lib/i18n/index.svelte';

	let { form, successMessage }: { form?: { ok?: boolean; message?: string } | null; successMessage?: string } = $props();
	const { t } = getI18n();
	const text = $derived.by(() => {
		if (!form?.message) return '';
		// Les actions renvoient soit une clé i18n (ex. "auth.errors.invalid"), soit un message backend brut.
		const translated = t(form.message);
		return translated === form.message ? form.message : translated;
	});
</script>

{#if form?.ok && successMessage}
	<div class="alert ok" role="status"><CircleCheck size={18} />{successMessage}</div>
{:else if form && !form.ok && text}
	<div class="alert bad" role="alert"><CircleAlert size={18} />{text}</div>
{/if}

<style lang="scss">
	.alert { display: flex; gap: 0.6rem; align-items: flex-start; padding: 0.8rem 1rem; border-radius: var(--radius); font-size: var(--fs-sm); font-weight: 600; :global(svg) { margin-top: 2px; flex-shrink: 0; } }
	.ok { background: var(--success-bg); color: var(--success); }
	.bad { background: var(--danger-bg); color: var(--danger); }
</style>
