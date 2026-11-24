<script lang="ts">
	import { adminResource } from '$lib/config/admin-resources';
	import { ResourceList } from '$lib/components/resource';
	let { data, form } = $props();
	const def = $derived(adminResource(data.key)!);
</script>

<ResourceList {def} data={data.list} role={data.user.role} base="/admin" {form} staff={data.staff} />
