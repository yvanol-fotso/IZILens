<script lang="ts">
	import { PrivacyDocument } from '$lib/components/privacy';
	let { data } = $props();
</script>

<PrivacyDocument doc={data.doc} />
