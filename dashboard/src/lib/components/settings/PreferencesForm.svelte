<script lang="ts">
	import { invalidateAll } from '$app/navigation';
	import { Monitor, Moon, Sun } from '@lucide/svelte';
	import { getI18n } from '$lib/i18n/index.svelte';
	import { LOCALES, LOCALE_COOKIE, LOCALE_LABELS, type Locale } from '$lib/i18n/locales';
	import { applyTheme, type ThemeMode } from '$lib/utils/theme';
	import { Card } from '$lib/components/shared';

	const i18n = getI18n();
	const { t } = i18n;
	let theme = $state<ThemeMode>('light');
	$effect(() => {
		const m = document.cookie.match(/izi_theme=(\w+)/)?.[1] as ThemeMode | undefined;
		if (m) theme = m;
	});
	async function setLocale(l: Locale) {
		document.cookie = `${LOCALE_COOKIE}=${l}; Path=/; Max-Age=31536000; SameSite=Lax`;
		i18n.locale = l;
		await invalidateAll();
	}
	function setTheme(m: ThemeMode) {
		theme = m;
		applyTheme(m);
	}
	const themes = [{ id: 'light', icon: Sun, k: 'themeLight' }, { id: 'dark', icon: Moon, k: 'themeDark' }, { id: 'system', icon: Monitor, k: 'themeSystem' }] as const;
</script>

<Card title={t('settings.preferences.title')}>
	<div class="stack">
		<fieldset><legend>{t('settings.preferences.language')}</legend>
			<div class="seg">{#each LOCALES as l (l)}<button type="button" class:on={i18n.locale === l} aria-pressed={i18n.locale === l} onclick={() => setLocale(l)}>{LOCALE_LABELS[l].flag} {LOCALE_LABELS[l].name}</button>{/each}</div>
		</fieldset>
		<fieldset><legend>{t('settings.preferences.theme')}</legend>
			<div class="seg">{#each themes as th (th.id)}{@const Icon = th.icon}<button type="button" class:on={theme === th.id} aria-pressed={theme === th.id} onclick={() => setTheme(th.id)}><Icon size={16} />{t(`nav.${th.k}`)}</button>{/each}</div>
		</fieldset>
	</div>
</Card>

<style lang="scss">
	fieldset { border: 0; padding: 0; margin: 0; } legend { font-size: var(--fs-sm); font-weight: 700; margin-bottom: 0.5rem; }
	.seg { display: inline-flex; padding: 4px; gap: 4px; background: var(--surface-2); border-radius: var(--radius); flex-wrap: wrap; button { display: inline-flex; align-items: center; gap: 0.45rem; border: 0; background: none; padding: 0.55rem 0.95rem; border-radius: var(--radius-sm); font-weight: 700; font-size: var(--fs-sm); color: var(--fg-muted); &.on { background: var(--surface); color: var(--fg); box-shadow: var(--shadow-sm); } } }
</style>
