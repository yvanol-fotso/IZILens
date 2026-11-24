<script lang="ts">
	import { Ban, KeyRound, MonitorSmartphone, ShieldAlert, ShieldCheck, UserX } from '@lucide/svelte';
	import { getI18n } from '$lib/i18n/index.svelte';
	import { ADMIN_RESOURCES } from '$lib/config/admin-resources';
	import { ResourceList } from '$lib/components/resource';
	import { PageHeader, StatCard } from '$lib/components/shared';
	let { data, form } = $props();
	const { t } = getI18n();
	const o = $derived(data.overview ?? {});
	const v = (k: string) => (o[k] ?? '—');
	const sDef = ADMIN_RESOURCES.find((r) => r.key === 'sessions')!;
	const eDef = ADMIN_RESOURCES.find((r) => r.key === 'security-events')!;
</script>

<PageHeader title={t('adm.sec.title')} subtitle={t('adm.sec.subtitle')} />
<div class="kpis">
	<StatCard label={t('adm.sec.failedLogins')} value={v('failed_logins_24h')} icon={Ban} tone="danger" />
	<StatCard label={t('adm.sec.suspicious')} value={v('suspicious_logins_24h')} icon={ShieldAlert} tone="warning" />
	<StatCard label={t('adm.sec.activeSessions')} value={v('active_sessions')} icon={MonitorSmartphone} tone="info" />
	<StatCard label={t('adm.sec.openAlerts')} value={v('open_alerts')} icon={UserX} tone="danger" />
	<StatCard label={t('adm.sec.sensitiveAccess')} value={v('sensitive_access_24h')} icon={KeyRound} />
	<StatCard label={t('adm.sec.mfaCoverage')} value={o.mfa_coverage_percent !== undefined ? `${o.mfa_coverage_percent}%` : '—'} icon={ShieldCheck} tone="success" />
</div>
<h2>{t('rx.r.sessions.title')}</h2>
<ResourceList def={sDef} data={data.sessions} role={data.user.role} base="/admin" {form} embedded />
<h2>{t('rx.r.security-events.title')}</h2>
<ResourceList def={eDef} data={data.events} role={data.user.role} base="/admin" embedded />

<style lang="scss">
	.kpis { display: grid; gap: 1rem; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); margin-bottom: 2rem; } h2 { font-size: var(--fs-xl); margin: 1.8rem 0 0.8rem; }
</style>
