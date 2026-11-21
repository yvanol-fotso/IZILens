<script lang="ts">
	import { UserPlus } from '@lucide/svelte';
	import { getI18n } from '$lib/i18n/index.svelte';
	import { InviteModal, MembersTable } from '$lib/components/team';
	import { Button, Card, PageHeader } from '$lib/components/shared';

	let { data, form } = $props();
	const { t } = getI18n();
	let open = $state(false);
</script>

<PageHeader title={t('team.title')} subtitle={t('team.subtitle')}>
	{#snippet actions()}<Button onclick={() => (open = true)}>{#snippet icon()}<UserPlus size={18} />{/snippet}{t('team.invite')}</Button>{/snippet}
</PageHeader>
<Card padded={false}><MembersTable members={data.members} currentUserId={data.user.id} /></Card>
<InviteModal bind:open {form} />
