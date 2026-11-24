<script lang="ts">
	import { getI18n } from '$lib/i18n/index.svelte';
	import { can } from '$lib/config/permissions';
	import type { ConfigPage } from '$lib/config/admin-config';
	import type { FormState, Role } from '$lib/types';
	import { PageHeader } from '$lib/components/shared';
	import { resDesc, resTitle } from '$lib/components/resource';
	import ConfigForm from './ConfigForm.svelte';
	import ProviderStatus from './ProviderStatus.svelte';

	let { page, data, role, form = null }: { page: ConfigPage; data: { values: Record<string, any>; status: Record<string, any>; unavailable: boolean }; role: Role; form?: FormState | null } = $props();
	const { t } = getI18n();
</script>

<PageHeader title={resTitle(t, 'admin', page.key)} subtitle={resDesc(t, page.key)} />
{#if page.key === 'providers'}<ProviderStatus status={data.status} />{/if}
<ConfigForm {page} values={data.values} unavailable={data.unavailable} {form} readonly={!can(role, page.write)} />
