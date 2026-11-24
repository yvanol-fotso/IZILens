<script lang="ts">
	import { enhance } from '$app/forms';
	import { invalidateAll } from '$app/navigation';
	import { getI18n } from '$lib/i18n/index.svelte';
	import { toastSuccess } from '$lib/stores/toast';
	import { Badge, Button, Card, FormAlert, Input, PageHeader, Textarea } from '$lib/components/shared';
	let { data, form } = $props();
	const { t } = getI18n();
	let selected = $state('platform_admin');
	const current = $derived(data.roles.find((r: any) => r.role === selected));
	let loading = $state(false);
	const err = (k: string) => { const e = form?.errors as Record<string, string> | undefined; return e?.[k] ? t(e[k]) : undefined; };
	const groups = $derived([...new Set(data.permissions.map((p: string) => p.split(':')[1]))] as string[]);
</script>

<PageHeader title={t('adm.roles.title')} subtitle={t('adm.roles.subtitle')} />
{#if !data.fromBackend}<p class="note">{t('adm.roles.defaults')}</p>{/if}

<div class="layout">
	<Card title={t('adm.roles.staffRoles')} padded={false}>
		<ul class="list">{#each data.roles as r (r.role)}<li><button type="button" class:on={selected === r.role} onclick={() => (selected = r.role)}>{t(`roles.${r.role}`)}<Badge>{r.permissions.length}</Badge></button></li>{/each}</ul>
	</Card>
	{#key selected}
	<form method="POST" action="?/save" class="stack" use:enhance={() => { loading = true; return async ({ result, update }) => { if (result.type === 'success') { toastSuccess(t('rx.ui.done')); await invalidateAll(); } await update({ reset: false }); loading = false; }; }}>
		<input type="hidden" name="role" value={selected} />
		<FormAlert {form} />
		<Card title={t(`roles.${selected}`)} description={selected === 'super_admin' ? t('adm.roles.locked') : t('adm.roles.separation')}>
			<div class="perms">
				{#each groups as g (g)}
					<fieldset><legend>{g}</legend>
						{#each data.permissions.filter((p: string) => p.split(':')[1] === g) as p (p)}
							<label><input type="checkbox" name="permissions" value={p} checked={current?.permissions.includes(p)} disabled={selected === 'super_admin'} />{p.split(':').slice(2).join(':') || 'read'}</label>
						{/each}
					</fieldset>
				{/each}
			</div>
		</Card>
		{#if selected !== 'super_admin'}
			<Card title={t('rx.ui.confirmChange')}><div class="stack">
				<Textarea label="{t('rx.ui.reason')} *" name="reason" error={err('reason')} />
				<Input label="{t('rx.ui.stepUp')} *" name="step_up_code" inputmode="numeric" maxlength={6} autocomplete="one-time-code" error={err('step_up_code')} hint={t('rx.ui.stepUpHint')} />
				<div><Button type="submit" variant="brand" {loading}>{t('common.save')}</Button></div>
			</div></Card>
		{/if}
	</form>
	{/key}
</div>

<style lang="scss">
	.note { margin-bottom: 1rem; padding: 0.8rem 1rem; background: var(--info-bg); color: var(--info); border-radius: var(--radius); font-size: var(--fs-sm); font-weight: 600; }
	.layout { display: grid; grid-template-columns: 280px 1fr; gap: 1.25rem; align-items: start; }
	.list { display: grid; button { width: 100%; display: flex; justify-content: space-between; align-items: center; padding: 0.85rem 1.2rem; border: 0; background: none; border-bottom: 1px solid var(--border); font-weight: 700; text-align: left; color: var(--fg); &.on { background: var(--primary-soft); box-shadow: inset 3px 0 0 var(--primary); } } }
	.perms { display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 1rem; } fieldset { border: 1px solid var(--border); border-radius: var(--radius); padding: 0.8rem 1rem; display: grid; gap: 0.4rem; } legend { font-weight: 800; font-size: var(--fs-sm); padding: 0 0.4rem; text-transform: capitalize; }
	label { display: flex; gap: 0.5rem; align-items: center; font-size: var(--fs-sm); font-family: var(--font-mono); input { accent-color: var(--primary); } }
	@media (max-width: 900px) { .layout { grid-template-columns: 1fr; } }
</style>
