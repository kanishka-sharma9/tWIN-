import createClient from "openapi-fetch";
import { type ApiError, apiErrorFromResponse, networkError } from "./errors";
import type { paths } from "./schema";

// The access token lives in memory only, never in localStorage (D-029).
let accessToken: string | null = null;

export function setAccessToken(token: string | null) {
	accessToken = token;
}

export function getAccessToken() {
	return accessToken;
}

/** Returns a new access token, or throws. E02-S03 implements it against the refresh cookie. */
export type RefreshFn = () => Promise<string>;

const refreshNotImplemented: RefreshFn = () =>
	Promise.reject(new Error("Token refresh is not implemented yet."));

let refresh: RefreshFn = refreshNotImplemented;

export function setRefresh(fn: RefreshFn) {
	refresh = fn;
}

const loggedOutListeners = new Set<() => void>();

/** Called when a refresh fails: the user is logged out. Returns an unsubscribe function. */
export function onLoggedOut(listener: () => void): () => void {
	loggedOutListeners.add(listener);
	return () => loggedOutListeners.delete(listener);
}

// Concurrent 401s share one refresh call.
let inflightRefresh: Promise<string> | null = null;

function refreshOnce(): Promise<string> {
	inflightRefresh ??= refresh().finally(() => {
		inflightRefresh = null;
	});
	return inflightRefresh;
}

async function send(request: Request): Promise<Response> {
	const headers = new Headers(request.headers);
	if (accessToken) headers.set("Authorization", `Bearer ${accessToken}`);
	try {
		return await globalThis.fetch(new Request(request, { headers }));
	} catch {
		throw networkError();
	}
}

/** Attaches the token; on a 401 refreshes once and retries the request once. */
export async function authedFetch(request: Request): Promise<Response> {
	const retry = request.clone();
	const response = await send(request);
	if (response.status !== 401) return response;

	let token: string;
	try {
		token = await refreshOnce();
	} catch {
		accessToken = null;
		for (const listener of loggedOutListeners) listener();
		return response;
	}
	accessToken = token;
	return send(retry);
}

// Absolute, because `Request` needs a full URL outside the browser (tests run in Node).
const baseUrl =
	typeof location === "undefined" ? "http://localhost" : location.origin;

export const api = createClient<paths>({ baseUrl, fetch: authedFetch });

/** Resolves with the data, or throws an ApiError built from the error response. */
export async function unwrap<T>(
	result: Promise<{ data?: T; error?: unknown; response: Response }>,
): Promise<T> {
	const { data, error, response } = await result;
	if (error !== undefined || !response.ok) {
		const apiError: ApiError = await apiErrorFromResponse(response, error);
		throw apiError;
	}
	return data as T;
}
