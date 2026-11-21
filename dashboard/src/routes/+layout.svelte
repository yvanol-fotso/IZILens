<script lang="ts">
	import '@fontsource-variable/manrope';
	import '../app.css';
	import type { Snippet } from 'svelte';
	import { setI18n } from '$lib/i18n/index.svelte';
	import { Toaster } from '$lib/components/shared';
	import { CookieBanner } from '$lib/components/layout';

	let { data, children }: { data: { locale: 'fr' | 'en' }; children: Snippet } = $props();

	// Contexte i18n propre à la requête ; se resynchronise quand la langue change.
	const i18n = setI18n(data.locale);
	$effect.pre(() => {
		i18n.locale = data.locale;
	});
	$effect(() => {
		document.documentElement.lang = data.locale;
	});
</script>

<a class="skip-link" href="#main">{i18n.t('common.skipToContent')}</a>
{@render children()}
<CookieBanner />
<Toaster />
