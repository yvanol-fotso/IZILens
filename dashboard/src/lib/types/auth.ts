export type Role = 'super_admin' | 'admin' | 'reviewer' | 'viewer' | 'integration';

export interface Organization {
	id: string;
	name: string;
	slug: string;
	is_active: boolean;
	enabled_modules: string[];
	created_at?: string;
	updated_at?: string;
}

export interface UserRecord {
	id: string;
	organization_id: string | null;
	email: string;
	full_name: string;
	role: Role;
	is_active: boolean;
	last_login_at?: string | null;
	created_at?: string;
}

export interface SessionUser extends UserRecord {
	organization: Organization | null;
}

export interface TokenPair {
	access_token: string;
	refresh_token?: string;
	token_type?: string;
	expires_in?: number;
}

export type AuthProvider = 'google';
