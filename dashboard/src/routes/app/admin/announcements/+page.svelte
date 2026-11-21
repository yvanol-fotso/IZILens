<script lang="ts">
	import { Megaphone } from '@lucide/svelte';
	import { getI18n } from '$lib/i18n/index.svelte';
	import { ModuleSoon } from '$lib/components/shared';
	const { t } = getI18n();
</script>

<ModuleSoon icon={Megaphone} title={t('modules.announcements_page.title')} subtitle={t('modules.announcements_page.subtitle')} features={['banner', 'target', 'schedule'].map((k) => t(`modules.announcements_page.features.${k}`))} />
