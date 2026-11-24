<script lang="ts">
	import { BulletList, Button } from '$lib/components/shared';
	import { reveal } from '$lib/actions/reveal';
	let { title, text, intro, items, primary, secondary, note }: { title: string; text: string; intro: string; items: string[]; primary: string; secondary: string; note?: string } = $props();
</script>

<section class="s">
	<div class="container wrap">
		<div use:reveal><h2>{title}</h2><p>{text}</p>{#if note}<p>{note}</p>{/if}
			<div class="row"><Button href="/developers" variant="brand">{primary}</Button><Button href="/contact?type=integration#form" variant="outline">{secondary}</Button></div>
		</div>
		<div class="box" use:reveal={{ delay: 100 }}><p class="intro">{intro}</p><BulletList {items} /></div>
	</div>
</section>

<style lang="scss">
	.s { padding: 5.5rem 0; background: var(--bg-soft); border-block: 1px solid var(--border); }
	.wrap { display: grid; grid-template-columns: 1fr 1fr; gap: 3.5rem; align-items: center; } h2 { font-size: var(--fs-3xl); margin-bottom: 1rem; } p { color: var(--fg-muted); margin-bottom: 0.8rem; } .row { margin-top: 1.4rem; }
	.box { padding: 1.8rem; background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius-lg); display: grid; gap: 1rem; } .intro { font-weight: 800; color: var(--fg) !important; }
	@media (max-width: 900px) { .wrap { grid-template-columns: 1fr; } }
</style>
