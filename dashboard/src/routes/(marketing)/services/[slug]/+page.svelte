<script lang="ts">
	import { serviceBySlug } from '$lib/config/services';
	import { ServiceDetail } from '$lib/components/services';
	let { data } = $props();
	const service = $derived(serviceBySlug(data.slug)!);
</script>

<ServiceDetail {service} />
