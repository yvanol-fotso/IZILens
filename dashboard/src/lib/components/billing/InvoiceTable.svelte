<script lang="ts">
	import { getI18n } from '$lib/i18n/index.svelte';
	import { formatDate } from '$lib/utils/format';
	import { Download, Eye } from '@lucide/svelte';
	import { Badge, Button } from '$lib/components/shared';
	
	let { invoices = [
		{ id: 'INV-2026-001', amount: 583.00, currency: 'CAD', status: 'paid', date: '2026-10-01' },
		{ id: 'INV-2026-002', amount: 299.00, currency: 'CAD', status: 'open', date: '2026-11-01' }
	] } = $props();
	
	const { t, locale } = getI18n();
	
	const statusTone = (s: string) => s === 'paid' ? 'success' : s === 'open' ? 'warning' : 'neutral';
</script>

<div class="table-wrap">
	<table>
		<thead>
			<tr>
				<th>{t('adm.f.number') || 'N° Facture'}</th>
				<th>{t('adm.f.issued_at') || 'Date'}</th>
				<th class="n">{t('adm.f.amount') || 'Montant'}</th>
				<th>{t('adm.f.status') || 'Statut'}</th>
				<th></th>
			</tr>
		</thead>
		<tbody>
			{#each invoices as inv (inv.id)}
				<tr>
					<td class="mono">{inv.id}</td>
					<td>{formatDate(inv.date, locale)}</td>
					<td class="n">{new Intl.NumberFormat(locale, { style: 'currency', currency: inv.currency }).format(inv.amount)}</td>
					<td><Badge tone={statusTone(inv.status)}>{t(`rx.o.${inv.status}`) || inv.status}</Badge></td>
					<td class="actions">
						<Button variant="outline" size="sm"><Eye size={14} /></Button>
						<Button variant="outline" size="sm"><Download size={14} /></Button>
					</td>
				</tr>
			{:else}
				<tr><td colspan="5" class="empty">{t('common.noData') || 'Aucune facture'}</td></tr>
			{/each}
		</tbody>
	</table>
</div>

<style lang="scss">
	.table-wrap { overflow-x: auto; }
	table { width: 100%; border-collapse: collapse; font-size: var(--fs-sm); }
	th, td { padding: 1rem; text-align: left; border-bottom: 1px solid var(--border); }
	th { background: var(--surface-2); color: var(--fg-muted); font-weight: 600; font-size: var(--fs-xs); text-transform: uppercase; }
	.n { text-align: right; font-variant-numeric: tabular-nums; }
	.mono { font-family: var(--font-mono); }
	.actions { display: flex; gap: 0.5rem; justify-content: flex-end; }
	.empty { text-align: center; color: var(--fg-muted); padding: 2rem; }
</style>