<script lang="ts">
	import { ShieldAlert } from '@lucide/svelte';
	import { getI18n } from '$lib/i18n/index.svelte';
	import { ModuleSoon } from '$lib/components/shared';
	const { t } = getI18n();
</script>

<ModuleSoon icon={ShieldAlert} title={t('modules.aml_page.title')} subtitle={t('modules.aml_page.subtitle')} features={['sanctions', 'pep', 'media', 'rules'].map((k) => t(`modules.aml_page.features.${k}`))} />
