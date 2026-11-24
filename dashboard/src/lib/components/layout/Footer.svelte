<script lang="ts">
	import { SITE } from '$lib/config/site';
	import { demoHref } from '$lib/config/services';
	import { getI18n } from '$lib/i18n/index.svelte';
	import { Logo, LanguageSwitcher } from '$lib/components/shared';
	import { openConsentCentre } from '$lib/stores/consent';
	import SocialIcon from './SocialIcon.svelte';

	const { t } = getI18n();
	const year = new Date().getFullYear(); // généré dynamiquement
	/** Seuls les profils dont l'URL officielle est confirmée sont rendus. */
	const socials = SITE.social.filter((s) => !!s.url);
</script>

<footer>
	<div class="container top">
		<div class="brand">
			<Logo tone="light" size={42} />
			<p class="slogan">{t('site.slogan')}</p>
			<p>{t('footer.about')}</p>
			{#if socials.length}
				<ul class="social" aria-label="Social">
					{#each socials as s (s.id)}<li><a href={s.url} rel="noopener noreferrer" aria-label={s.label}><SocialIcon name={s.id} /></a></li>{/each}
				</ul>
			{/if}
		</div>

		<nav class="cols" aria-label="Footer">
			<div>
				<h3>{t('footer.columns.platform')}</h3>
				<a href="/">{t('footer.links.home')}</a>
				<a href="/services">{t('footer.links.services')}</a>
				<a href="/solutions">{t('footer.links.solutions')}</a>
				<a href="/#pricing">{t('footer.links.pricing')}</a>
			</div>
			<div>
				<h3>{t('footer.columns.developers')}</h3>
				<a href="/developers">{t('footer.links.developers')}</a>
				<a href="/resources">{t('footer.links.resources')}</a>
				<a href="/login">{t('footer.links.signIn')}</a>
			</div>
			<div>
				<h3>{t('footer.columns.company')}</h3>
				<a href="/about">{t('footer.links.about')}</a>
				<a href="/contact">{t('footer.links.contact')}</a>
				<a href={demoHref}>{t('footer.links.demo')}</a>
			</div>
			<div>
				<h3>{t('footer.columns.legal')}</h3>
				<a href="/privacy">{t('footer.privacy')}</a>
				<a href="/cookies">{t('footer.cookies')}</a>
				<a href="/terms">{t('footer.terms')}</a>
				<button type="button" onclick={openConsentCentre}>{t('footer.cookiePrefs')}</button>
			</div>
		</nav>
	</div>

	<div class="container bottom">
		<span>{t('footer.copyright', { year })}</span>
		<LanguageSwitcher variant="light" placement="up" />
	</div>
</footer>

<style lang="scss">
	footer { background: var(--brand-navy); color: #aebfd6; padding-top: 4rem; margin-top: auto; }
	.top { display: grid; grid-template-columns: minmax(240px, 1.2fr) 3fr; gap: 3rem; padding-bottom: 3rem; }
	.brand { display: grid; gap: 1rem; align-content: start; p { font-size: var(--fs-sm); max-width: 38ch; line-height: 1.7; } .slogan { color: var(--brand-cyan); font-style: italic; font-weight: 600; } }
	.social { display: flex; gap: 0.5rem; a { width: 38px; height: 38px; display: grid; place-items: center; border-radius: 10px; background: rgb(255 255 255 / 0.08); color: #fff; &:hover { background: var(--primary); } } }
	.cols { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 2rem; }
	h3 { color: #fff; font-size: var(--fs-sm); margin-bottom: 0.9rem; }
	.cols > div { display: grid; align-content: start; gap: 0.55rem; }
	a, button { color: #c0cfe3; background: none; border: 0; padding: 0; text-align: left; font-size: var(--fs-sm); &:hover { color: var(--brand-cyan); text-decoration: none; } }
	.bottom { display: flex; justify-content: space-between; align-items: center; gap: 1rem; flex-wrap: wrap; padding: 1.2rem 0 1.8rem; border-top: 1px solid rgb(255 255 255 / 0.1); font-size: var(--fs-xs); }
	@media (max-width: 900px) { .top { grid-template-columns: 1fr; } }
</style>
