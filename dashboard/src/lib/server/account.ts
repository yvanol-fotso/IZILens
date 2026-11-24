import { fail, type RequestEvent } from '@sveltejs/kit';
import { actionError, createApi } from './api';
import { invalidateUserCache } from './auth/service';
import { backendJson } from './backend';
import { EPX, EP } from './endpoints';

type Ev = RequestEvent<any, any>;
const tok = (e: Ev) => e.locals.accessToken;

export async function loadAccount(event: Ev) {
	const api = createApi(event);
	return {
		sessions: await api.safe(api.list<any>(EPX.auth.sessions), []),
		passkeys: await api.safe(api.list<any>(EPX.auth.passkeys), [])
	};
}

/** Actions de compte : profil, mot de passe, MFA TOTP, passkeys, sessions. */
export const accountActions = {
	profile: async (event: Ev) => {
		const full_name = String((await event.request.formData()).get('full_name') ?? '').trim();
		if (!full_name) return fail(400, { ok: false, form: 'profile', errors: { full_name: 'auth.errors.required' } });
		try { await createApi(event).patch(EP.users.me, { full_name }); invalidateUserCache(tok(event)); }
		catch (e) { return fail(400, { ok: false, form: 'profile', message: actionError(e).message }); }
		return { ok: true, form: 'profile' };
	},
	password: async (event: Ev) => {
		const d = await event.request.formData();
		const current_password = String(d.get('current_password') ?? '');
		const new_password = String(d.get('new_password') ?? '');
		if (!current_password) return fail(400, { ok: false, form: 'password', errors: { current_password: 'auth.errors.required' } });
		if (new_password.length < 12) return fail(400, { ok: false, form: 'password', errors: { new_password: 'auth.errors.passwordShort' } });
		try { await createApi(event).post(EP.auth.changePassword, { current_password, new_password }); }
		catch (e) { return fail(400, { ok: false, form: 'password', message: actionError(e).message }); }
		return { ok: true, form: 'password' };
	},
	totpSetup: async (event: Ev) => {
		try { const r = await backendJson<{ secret: string; otpauth_uri: string }>(EPX.auth.totpSetup, { method: 'POST', token: tok(event), json: {} }); return { ok: true, form: 'mfa', setup: r }; }
		catch (e) { return fail(400, { ok: false, form: 'mfa', message: actionError(e).message }); }
	},
	totpConfirm: async (event: Ev) => {
		const code = String((await event.request.formData()).get('code') ?? '').trim();
		if (!/^\d{6}$/.test(code)) return fail(400, { ok: false, form: 'mfa', errors: { code: 'auth.errors.invalid' }, setup: true });
		try { const r = await backendJson<{ recovery_codes?: string[] }>(EPX.auth.totpConfirm, { method: 'POST', token: tok(event), json: { code } }); invalidateUserCache(tok(event)); return { ok: true, form: 'mfa', recovery: r.recovery_codes ?? [] }; }
		catch (e) { return fail(400, { ok: false, form: 'mfa', errors: { code: 'auth.errors.invalid' }, message: actionError(e).message }); }
	},
	mfaDisable: async (event: Ev) => {
		const code = String((await event.request.formData()).get('code') ?? '').trim();
		try { await backendJson(EPX.auth.mfaDisable, { method: 'POST', token: tok(event), json: { code } }); invalidateUserCache(tok(event)); return { ok: true, form: 'mfa', disabled: true }; }
		catch (e) { return fail(400, { ok: false, form: 'mfa', message: actionError(e).message }); }
	},
	passkeyDelete: async (event: Ev) => {
		const id = String((await event.request.formData()).get('id'));
		try { await createApi(event).del(`${EPX.auth.passkeys}/${id}`); return { ok: true, form: 'passkeys' }; }
		catch (e) { return fail(400, { ok: false, form: 'passkeys', message: actionError(e).message }); }
	},
	sessionRevoke: async (event: Ev) => {
		const id = String((await event.request.formData()).get('id'));
		try { await createApi(event).del(`${EPX.auth.sessions}/${id}`); return { ok: true, form: 'sessions' }; }
		catch (e) { return fail(400, { ok: false, form: 'sessions', message: actionError(e).message }); }
	}
};
