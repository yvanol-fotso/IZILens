export * from './auth';

export type CaseStatus = 'processing' | 'pending_review' | 'approved' | 'rejected' | 'failed';
export type RiskLevel = 'low' | 'medium' | 'high';
export type ModuleId = 'kyc' | 'liveness' | 'biometrics' | 'aml' | 'api';




export interface KycDocument {
	id: string;
	case_id: string;
	side: 'front' | 'back';
	mime_type?: string;
	size_bytes?: number;
	width?: number;
	height?: number;
	sharpness?: number;
	created_at?: string;
}

export interface KycCase {
	id: string;
	reference: string;
	document_type: string;
	status: CaseStatus;
	risk_level: RiskLevel | null;
	ocr_confidence: number | null;
	extracted_data: string | Record<string, unknown> | null;
	flags: unknown;
	failure_reason?: string | null;
	created_by?: string | null;
	decided_by_user_id?: string | null;
	decided_at?: string | null;
	decision_reason?: string | null;
	processed_at?: string | null;
	created_at: string;
	updated_at?: string;
	documents?: KycDocument[];
}

export interface ApiKey {
	id: string;
	name: string;
	prefix: string;
	is_active: boolean;
	expires_at?: string | null;
	last_used_at?: string | null;
	revoked_at?: string | null;
	created_at: string;
}

export interface AuditLog {
	id: string;
	organization_id?: string | null;
	actor_type: 'user' | 'api_key' | 'system';
	actor_id?: string | null;
	action: string;
	resource_type?: string | null;
	resource_id?: string | null;
	ip_address?: string | null;
	request_id?: string | null;
	details?: unknown;
	created_at: string;
}

export interface Paged<T> {
	items: T[];
	total: number;
	page: number;
	pageSize: number;
}


export interface FormState {
	ok?: boolean;
	message?: string;
	errors?: Record<string, string>;
	values?: Record<string, string>;
	[key: string]: unknown;
}
