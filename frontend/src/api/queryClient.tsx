import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import type { ReactNode } from "react";
import { ApiError } from "./errors";

/** No retry on 4xx or other API errors; one retry on network errors. */
export function retryPolicy(failureCount: number, error: unknown): boolean {
	return (
		error instanceof ApiError &&
		error.code === "network_error" &&
		failureCount < 1
	);
}

export function createQueryClient() {
	return new QueryClient({
		defaultOptions: {
			queries: { retry: retryPolicy, refetchOnWindowFocus: false },
		},
	});
}

const defaultClient = createQueryClient();

export function QueryProvider({
	children,
	client = defaultClient,
}: {
	children: ReactNode;
	client?: QueryClient;
}) {
	return <QueryClientProvider client={client}>{children}</QueryClientProvider>;
}
