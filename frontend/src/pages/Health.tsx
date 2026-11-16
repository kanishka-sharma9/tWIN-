import { useEffect, useState } from "react";

type HealthResponse = { status: string; database: string };

type State =
	| { kind: "loading" }
	| { kind: "ok"; health: HealthResponse }
	| { kind: "error"; message: string };

// Plain `fetch` for now; E01-S06 replaces it with the typed client.
export function Health() {
	const [state, setState] = useState<State>({ kind: "loading" });

	useEffect(() => {
		const controller = new AbortController();
		async function load() {
			try {
				const response = await fetch("/api/health", {
					signal: controller.signal,
				});
				if (!response.ok) {
					setState({
						kind: "error",
						message: `The API answered with status ${response.status}.`,
					});
					return;
				}
				setState({
					kind: "ok",
					health: (await response.json()) as HealthResponse,
				});
			} catch {
				if (controller.signal.aborted) return;
				setState({
					kind: "error",
					message: "Could not reach the API. Is it running on port 8000?",
				});
			}
		}
		void load();
		return () => controller.abort();
	}, []);

	return (
		<section className="space-y-2">
			<h1 className="text-2xl font-semibold">tWIN!!</h1>
			{state.kind === "loading" && <p>Checking the API…</p>}
			{state.kind === "ok" && (
				<p>
					API: {state.health.status}, database: {state.health.database}
				</p>
			)}
			{state.kind === "error" && (
				<p role="alert" className="text-destructive">
					{state.message}
				</p>
			)}
		</section>
	);
}
