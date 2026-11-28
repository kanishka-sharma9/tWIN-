import { baseUrl } from "@/api/client";
import { apiErrorFromResponse, networkError } from "@/api/errors";
import type { components } from "@/api/schema";

export type TokenResponse = components["schemas"]["TokenResponse"];
export type User = components["schemas"]["UserOut"];

// The refresh and logout calls use plain `fetch`, not the client: a 401 from them must not
// start another refresh. The custom header is what the API requires on cookie routes (CSRF).
function cookieRoute(path: string): Request {
	return new Request(new URL(path, baseUrl), {
		method: "POST",
		headers: { "X-Requested-With": "twin" },
		credentials: "same-origin",
	});
}

async function send(request: Request): Promise<Response> {
	try {
		return await globalThis.fetch(request);
	} catch {
		throw networkError();
	}
}

let inflight: Promise<TokenResponse> | null = null;

async function doRefresh(): Promise<TokenResponse> {
	const response = await send(cookieRoute("/api/auth/refresh"));
	if (!response.ok) throw await apiErrorFromResponse(response);
	return (await response.json()) as TokenResponse;
}

/**
 * Exchanges the refresh cookie for a new access token. Refresh tokens rotate, so concurrent
 * callers (a StrictMode double mount, parallel 401s) must share one request.
 */
export function refreshSession(): Promise<TokenResponse> {
	inflight ??= doRefresh().finally(() => {
		inflight = null;
	});
	return inflight;
}

/** Ends the session on the server. Failures are ignored: the person is signed out either way. */
export async function endSession(): Promise<void> {
	try {
		await send(cookieRoute("/api/auth/logout"));
	} catch {
		// Nothing to do: the caller clears local state.
	}
}
