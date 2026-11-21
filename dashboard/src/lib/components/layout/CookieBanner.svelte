<script lang="ts">
	import { Cookie, ShieldCheck } from '@lucide/svelte';
	import { getI18n } from '$lib/i18n/index.svelte';
	import { CONSENT_EFFECTIVE_DATE, CONSENT_VERSION, OPTIONAL_CATEGORIES, consent, consentPanelOpen, type OptionalCategory } from '$lib/stores/consent';
	import { formatDate } from '$lib/utils/format';
	import { Button, Modal, Switch } from '$lib/components/shared';

	const i18n = getI18n();
	const { t } = i18n;
	let mounted = $state(false);
	$effect(() => {
		mounted = true;
	});

	let panel = $state(false);
	let draft = $state<Record<OptionalCategory, boolean>>({ functional: false, analytics: false, performance: false, advertising: false, unclassified: false });

	$effect(() => {
		if ($consentPanelOpen) {
			draft = { ...$consent.choices };
			panel = true;
			consentPanelOpen.set(false);
		}
	});

	const open = () => {
		draft = { ...$consent.choices };
		panel = true;
	};
	function saveChoices() {
		consent.save(draft);
		panel = false;
	}
</script>

{#if mounted && !$consent.decided && !panel}
	<div class="banner" role="region" aria-label={t('cookieBanner.title')}>
		<span class="ico"><Cookie size={22} /></span>
		<div class="txt">
			<strong>{t('cookieBanner.title')}</strong>
			<p>{t('cookieBanner.text')} <a href="/cookies">{t('footer.cookies')}</a></p>
		</div>
		<!-- Accepter et refuser ont strictement le même poids visuel -->
		<div class="btns">
			<Button size="sm" variant="outline" onclick={() => consent.acceptAll()}>{t('cookieBanner.acceptAll')}</Button>
			<Button size="sm" variant="outline" onclick={() => consent.rejectOptional()}>{t('cookieBanner.rejectAll')}</Button>
			<Button size="sm" variant="ghost" onclick={open}>{t('cookieBanner.customize')}</Button>
		</div>
	</div>
{/if}

<Modal bind:open={panel} size="lg" title={t('cookieBanner.preferences')} description={t('cookieBanner.preferencesText')}>
	<div class="prefs">
		<div class="necessary">
			<ShieldCheck size={20} />
			<div><b>{t('cookieBanner.necessary.title')}</b><span>{t('cookieBanner.necessary.desc')}</span></div>
			<em>{t('cookieBanner.alwaysActive')}</em>
		</div>
		{#each OPTIONAL_CATEGORIES as cat (cat)}
			<Switch bind:checked={draft[cat]} label={t(`cookieBanner.${cat}.title`)} description={t(`cookieBanner.${cat}.desc`)} />
		{/each}
		<p class="ver">{t('cookieBanner.version', { version: CONSENT_VERSION, date: formatDate(CONSENT_EFFECTIVE_DATE, i18n.locale) })}</p>
	</div>
	{#snippet footer()}
		<Button variant="outline" onclick={() => { consent.rejectOptional(); panel = false; }}>{t('cookieBanner.rejectAll')}</Button>
		<Button variant="outline" onclick={() => { consent.acceptAll(); panel = false; }}>{t('cookieBanner.acceptAll')}</Button>
		<Button variant="brand" onclick={saveChoices}>{t('cookieBanner.save')}</Button>
	{/snippet}
</Modal>

<style lang="scss">
	.banner { position: fixed; left: 1rem; right: 1rem; bottom: 1rem; z-index: var(--z-toast); max-width: 1020px; margin-inline: auto; display: flex; align-items: center; gap: 1.1rem; padding: 1rem 1.2rem; background: var(--surface); border: 1px solid var(--border-strong); border-radius: var(--radius-lg); box-shadow: var(--shadow-lg); animation: up 0.4s var(--ease); }
	.ico { width: 44px; height: 44px; border-radius: 14px; display: grid; place-items: center; background: var(--primary-soft); color: var(--primary); flex-shrink: 0; }
	.txt { flex: 1; font-size: var(--fs-sm); p { color: var(--fg-muted); margin-top: 0.15rem; line-height: 1.55; } strong { font-size: var(--fs-md); } }
	.btns { display: flex; gap: 0.5rem; flex-wrap: wrap; justify-content: flex-end; }
	.prefs { display: grid; gap: 1.1rem; max-height: 58vh; overflow-y: auto; padding-right: 0.3rem; }
	.necessary { display: flex; gap: 0.8rem; align-items: center; padding: 0.85rem 1rem; background: var(--success-bg); color: var(--success); border-radius: var(--radius); div { display: grid; flex: 1; font-size: var(--fs-sm); span { font-size: var(--fs-xs); opacity: 0.9; } } em { font-style: normal; font-size: var(--fs-xs); font-weight: 800; white-space: nowrap; } }
	.ver { font-size: var(--fs-xs); color: var(--fg-subtle); }
	@keyframes up { from { opacity: 0; transform: translateY(20px); } }
	@media (max-width: 800px) { .banner { flex-direction: column; align-items: stretch; } .btns { :global(.btn) { flex: 1; } } }
</style>
