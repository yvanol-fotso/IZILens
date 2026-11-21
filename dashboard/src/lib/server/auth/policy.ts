import { can } from '$lib/config/permissions';
import type { SessionUser } from '$lib/types/auth';
import { authConfig } from './config';

/** Empêche les redirections ouvertes : uniquement des chemins internes. */
export function safeNext(next: string | null | undefined, fallback: string = authConfig.paths.afterLogin): string {
	return next && next.startsWith('/') && !next.startsWith('//') && !next.includes('\\') ? next : fallback;
}

export const isAppPath = (p: string) => p === '/app' || p.startsWith('/app/');
export const isAdminPath = (p: string) => p === '/app/admin' || p.startsWith('/app/admin/');
export const isAuthPage = (p: string) => p === '/login' || p === '/register';
export const isProxyPath = (p: string) => p.startsWith('/api/v1');

/** Destination après connexion : `next` s'il est sûr, sinon l'espace adapté au rôle. */
export function postLoginPath(user: Pick<SessionUser, 'role'> | null, next?: string | null): string {
	const fallback = user?.role === 'super_admin' ? authConfig.paths.afterLoginAdmin : authConfig.paths.afterLogin;
	return safeNext(next, fallback);
}

export type GuardDecision = { type: 'allow' } | { type: 'redirect'; to: string };

/** Politique d'accès unique, utilisée par hooks.server.ts. */
export function decideAccess(path: string, search: string, user: SessionUser | null, hasToken: boolean): GuardDecision {
	if (isAppPath(path) && !hasToken) return { type: 'redirect', to: `${authConfig.paths.login}?next=${encodeURIComponent(path + search)}` };
	if (isAdminPath(path) && !can(user?.role, 'admin:access')) return { type: 'redirect', to: authConfig.paths.afterLogin };
	if (isAuthPage(path) && hasToken) return { type: 'redirect', to: authConfig.paths.afterLogin };
	return { type: 'allow' };
}
