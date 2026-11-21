<script lang="ts">
	import { Fingerprint } from '@lucide/svelte';
	import { getI18n } from '$lib/i18n/index.svelte';
	import { ModuleSoon } from '$lib/components/shared';
	const { t } = getI18n();
</script>

<ModuleSoon icon={Fingerprint} title={t('modules.biometrics_page.title')} subtitle={t('modules.biometrics_page.subtitle')} features={['match', 'score', 'quality', 'link'].map((k) => t(`modules.biometrics_page.features.${k}`))} />
