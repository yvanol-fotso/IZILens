<script lang="ts">
	import { CONFIG_PAGES } from '$lib/config/admin-config';
	import { ConfigRoute } from '$lib/components/admin';
	let { data, form } = $props();
</script>

<ConfigRoute page={CONFIG_PAGES.settings} data={data.cfg} role={data.user.role} {form} />
