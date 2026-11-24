<script lang="ts">
	import { clientResource } from '$lib/config/client-resources';
	import { ResourceDetail } from '$lib/components/resource';
	let { data, form } = $props();
	const def = $derived(clientResource(data.key)!);
</script>

<ResourceDetail {def} row={data.row} related={data.related} role={data.user.role} base="/app" {form} />
