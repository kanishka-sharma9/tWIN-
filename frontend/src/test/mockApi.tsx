import { render } from "@testing-library/react";
import { MemoryRouter } from "react-router";
import { App } from "@/App";
import { setAccessToken } from "@/api/client";
import { QueryProvider } from "@/api/queryClient";
import { AuthProvider } from "@/auth/AuthProvider";
import { errorBody, jsonResponse, mockFetch } from "./fetchMock";
import { createTestQueryClient } from "./renderWithProviders";

export const USER = {
	id: "5b1f6c3e-0000-4000-8000-000000000001",
	email: "ada@example.com",
	has_password: true,
};

export function tokens(user = USER) {
	return {
		access_token: "access-1",
		token_type: "bearer",
		expires_in: 900,
		user,
	};
}

type Handler = (request: Request) => Promise<Response> | Response;
export type Routes = Record<string, Handler | undefined>;

/**
 * Stubs `fetch` with a route table keyed "METHOD /path". Unlisted auth routes behave like a
 * signed-out server: refresh answers 401, providers answers `google: false`.
 */
export function mockApi(routes: Routes = {}) {
	const table: Routes = {
		"POST /api/auth/refresh": () =>
			jsonResponse(errorBody("invalid_refresh_token", "No session."), 401),
		"GET /api/auth/providers": () => jsonResponse({ google: false }),
		"POST /api/auth/logout": () => new Response(null, { status: 204 }),
		...routes,
	};
	return mockFetch(async (request) => {
		const key = `${request.method} ${new URL(request.url).pathname}`;
		const handler = table[key];
		if (!handler) throw new Error(`Unexpected request: ${key}`);
		return handler(request);
	});
}

export function signedInServer(user = USER): Routes {
	return { "POST /api/auth/refresh": () => jsonResponse(tokens(user)) };
}

/** Renders the whole app (router, auth state, pages) at `route`. */
export function renderApp(route: string) {
	setAccessToken(null);
	return render(
		<QueryProvider client={createTestQueryClient()}>
			<MemoryRouter initialEntries={[route]}>
				<AuthProvider>
					<App />
				</AuthProvider>
			</MemoryRouter>
		</QueryProvider>,
	);
}
