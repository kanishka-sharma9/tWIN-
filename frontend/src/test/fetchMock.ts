import { vi } from "vitest";

/** Replaces `fetch` for one test; undo with `vi.unstubAllGlobals()`. */
export function mockFetch(impl: (request: Request) => Promise<Response>) {
	const mock = vi.fn(impl);
	vi.stubGlobal("fetch", mock);
	return mock;
}

export function jsonResponse(body: unknown, status = 200) {
	return Promise.resolve(
		new Response(JSON.stringify(body), {
			status,
			headers: { "Content-Type": "application/json" },
		}),
	);
}

export function errorBody(code: string, message: string, details = {}) {
	return { error: { code, message, details } };
}
