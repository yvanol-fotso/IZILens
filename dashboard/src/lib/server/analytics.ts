import type { CaseStatus, KycCase, RiskLevel } from '$lib/types';

export interface CaseStats {
	total: number;
	byStatus: Record<CaseStatus, number>;
	byRisk: Record<RiskLevel | 'none', number>;
	avgConfidence: number | null;
	approvalRate: number | null;
	daily: { date: string; value: number }[];
	confidenceBands: { low: number; mid: number; high: number };
}

const STATUSES: CaseStatus[] = [
	'created',
	'in_progress',
	'action_required',
	'processing',
	'manual_review',
	'verified',
	'not_verified',
	'failed',
	'expired'
];

export function buildStats(cases: KycCase[], days = 14): CaseStats {
	const byStatus = Object.fromEntries(STATUSES.map((s) => [s, 0])) as Record<CaseStatus, number>;
	const byRisk: CaseStats['byRisk'] = { low: 0, medium: 0, high: 0, none: 0 };
	const bands = { low: 0, mid: 0, high: 0 };
	let confSum = 0;
	let confCount = 0;

	const perDay = new Map<string, number>();
	const today = new Date();
	for (let i = days - 1; i >= 0; i--) {
		const d = new Date(today);
		d.setDate(today.getDate() - i);
		perDay.set(d.toISOString().slice(0, 10), 0);
	}

	for (const c of cases) {
		if (c.status in byStatus) byStatus[c.status]++;
		byRisk[c.risk_level ?? 'none']++;
		if (typeof c.ocr_confidence === 'number') {
			const v = c.ocr_confidence <= 1 ? c.ocr_confidence : c.ocr_confidence / 100;
			confSum += v;
			confCount++;
			if (v < 0.7) bands.low++;
			else if (v < 0.9) bands.mid++;
			else bands.high++;
		}
		const key = c.created_at?.slice(0, 10);
		if (key && perDay.has(key)) perDay.set(key, (perDay.get(key) ?? 0) + 1);
	}

	const decided = byStatus.verified + byStatus.not_verified;
	return {
		total: cases.length,
		byStatus,
		byRisk,
		avgConfidence: confCount ? confSum / confCount : null,
		approvalRate: decided ? byStatus.verified / decided : null,
		daily: [...perDay.entries()].map(([date, value]) => ({ date, value })),
		confidenceBands: bands
	};
}
