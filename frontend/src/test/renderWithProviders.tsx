import { QueryClient } from "@tanstack/react-query";
import { render } from "@testing-library/react";
import type { ReactElement } from "react";
import { MemoryRouter } from "react-router";
import { QueryProvider, retryPolicy } from "@/api/queryClient";

/** A client with the app's retry policy but no waiting between retries. */
export function createTestQueryClient() {
	return new QueryClient({
		defaultOptions: {
			queries: {
				retry: retryPolicy,
				retryDelay: 0,
				refetchOnWindowFocus: false,
			},
		},
	});
}

export function renderWithProviders(
	ui: ReactElement,
	{ route = "/" }: { route?: string } = {},
) {
	return render(
		<QueryProvider client={createTestQueryClient()}>
			<MemoryRouter initialEntries={[route]}>{ui}</MemoryRouter>
		</QueryProvider>,
	);
}
