<script lang="ts">
	import { Mail, MapPin, Phone } from '@lucide/svelte';
	import SocialIcon from './SocialIcon.svelte';
	import { env } from '$env/dynamic/public';
	import { footerIndustries, footerSolutions } from '$lib/config/navigation';
	import { SITE } from '$lib/config/site';
	import { getI18n } from '$lib/i18n/index.svelte';
	import { Logo, LanguageSwitcher } from '$lib/components/shared';
	import { openConsentCentre } from '$lib/stores/consent';

	const { t } = getI18n();
	const year = new Date().getFullYear(); // généré dynamiquement
	const docsUrl = $derived(env.PUBLIC_DOCS_URL || '');
	/** Seuls les profils dont l'URL officielle est confirmée sont rendus. */
	const socials = SITE.social.filter((s) => !!s.url);
</script>

<footer>
	<div class="container top">
		<div class="brand">
			<Logo tone="light" size={42} />
			<p>{t('footer.tagline')}</p>
			{#if socials.length}
				<ul class="social" aria-label={t('footer.columns.social')}>
					{#each socials as s (s.id)}
						<li><a href={s.url} rel="noopener noreferrer" aria-label={s.label}><SocialIcon name={s.id} /></a></li>
					{/each}
				</ul>
			{/if}
		</div>

		<nav class="cols" aria-label="Footer">
			<div>
				<h3>{t('footer.columns.solutions')}</h3>
				{#each footerSolutions as it (it.key)}
					{#if it.href}<a href={it.href}>{t(`footer.solutions.${it.key}`)}</a>{:else}<span>{t(`footer.solutions.${it.key}`)}</span>{/if}
				{/each}
			</div>
			<div>
				<h3>{t('footer.columns.industries')}</h3>
				{#each footerIndustries as it (it.key)}
					{#if it.href}<a href={it.href}>{t(`footer.industries.${it.key}`)}</a>{:else}<span>{t(`footer.industries.${it.key}`)}</span>{/if}
				{/each}
			</div>
			<div>
				<h3>{t('footer.columns.developers')}</h3>
				{#if docsUrl}<a href={docsUrl}>{t('footer.links.docs')}</a>{/if}
				<a href="/login">{t('footer.links.signIn')}</a>
			</div>
			<div>
				<h3>{t('footer.columns.company')}</h3>
				<a href="mailto:{SITE.email}">{t('footer.links.contact')}</a>
			</div>
			<div>
				<h3>{t('footer.columns.legal')}</h3>
				<a href="/privacy">{t('footer.privacy')}</a>
				<a href="/cookies">{t('footer.cookies')}</a>
				<a href="/terms">{t('footer.terms')}</a>
				<button type="button" onclick={openConsentCentre}>{t('footer.cookiePrefs')}</button>
			</div>
		</nav>

		<address class="contact">
			<h3>{t('footer.columns.contact')}</h3>
			<p><Mail size={16} /><a href="mailto:{SITE.email}">{SITE.email}</a></p>
			<p><Phone size={16} /><a href="tel:{SITE.phone.replace(/\s/g, '')}">{SITE.phone}</a></p>
			<p><MapPin size={16} /><span>{SITE.address.join(', ')}</span></p>
		</address>
	</div>

	<div class="container bottom">
		<span>© {year} {SITE.company}. {t('footer.rights')}</span>
		<LanguageSwitcher variant="light" placement="up" />
	</div>
</footer>

<style lang="scss">
	footer { background: var(--brand-navy); color: #aebfd6; padding-top: 4rem; margin-top: auto; }
	.top { display: grid; grid-template-columns: minmax(220px, 1.1fr) 4fr minmax(220px, 1.2fr); gap: 3rem; padding-bottom: 3rem; }
	.brand { display: grid; gap: 1.2rem; align-content: start; p { font-size: var(--fs-sm); max-width: 34ch; line-height: 1.7; } }
	.social { display: flex; gap: 0.5rem; a { width: 38px; height: 38px; display: grid; place-items: center; border-radius: 10px; background: rgb(255 255 255 / 0.08); color: #fff; &:hover { background: var(--primary); } } }
	.cols { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 2rem; }
	h3 { color: #fff; font-size: var(--fs-sm); margin-bottom: 0.9rem; }
	.cols > div { display: grid; align-content: start; gap: 0.55rem; font-size: var(--fs-sm); }
	.cols span { color: #8ea3bf; }
	a, button { color: #c0cfe3; background: none; border: 0; padding: 0; text-align: left; font-size: var(--fs-sm); &:hover { color: var(--brand-cyan); text-decoration: none; } }
	.contact { font-style: normal; p { display: flex; gap: 0.6rem; align-items: flex-start; margin-bottom: 0.6rem; font-size: var(--fs-sm); :global(svg) { flex-shrink: 0; margin-top: 3px; color: var(--brand-cyan); } } }
	.bottom { display: flex; justify-content: space-between; align-items: center; gap: 1rem; flex-wrap: wrap; padding: 1.2rem 0 1.8rem; border-top: 1px solid rgb(255 255 255 / 0.1); font-size: var(--fs-xs); }
	@media (max-width: 1100px) { .top { grid-template-columns: 1fr; } }
</style>
