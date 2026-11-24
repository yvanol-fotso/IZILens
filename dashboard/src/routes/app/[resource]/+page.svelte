<script lang="ts">
	import { clientResource } from '$lib/config/client-resources';
	import { ResourceList } from '$lib/components/resource';
	let { data, form } = $props();
	const def = $derived(clientResource(data.key)!);
</script>

<ResourceList {def} data={data.list} role={data.user.role} base="/app" {form} />
