<script lang="ts">
	import { adminResource } from '$lib/config/admin-resources';
	import { ResourceDetail } from '$lib/components/resource';
	let { data, form } = $props();
	const def = $derived(adminResource(data.key)!);
</script>

<ResourceDetail {def} row={data.row} related={data.related} role={data.user.role} base="/admin" {form} staff={data.staff} />
