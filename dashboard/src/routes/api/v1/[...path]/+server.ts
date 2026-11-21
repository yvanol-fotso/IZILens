import type { RequestHandler } from '@sveltejs/kit';
import { proxyToBackend } from '$lib/server/proxy';

/**
 * Proxy navigateur → backend FastAPI (/api/v1/*).
 * Utilisé par le client (aperçus d'images, sondage de statut…). Les routes /auth sont bloquées :
 * les jetons ne transitent jamais par le JavaScript du navigateur.
 */
const handler: RequestHandler = (event) => proxyToBackend(event, { target: '', deny: [/^auth(\/|$)/] });

export const GET = handler;
export const POST = handler;
export const PUT = handler;
export const PATCH = handler;
export const DELETE = handler;
