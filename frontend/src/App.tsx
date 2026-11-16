import { lazy, Suspense } from "react";
import { Route, Routes } from "react-router";
import { Layout } from "@/layouts/Layout";
import { Health } from "@/pages/Health";

// `import.meta.env.DEV` is false in production builds, so this route and its chunk are dropped.
const DevTokens = import.meta.env.DEV
	? lazy(() =>
			import("@/pages/DevTokens").then((m) => ({ default: m.DevTokens })),
		)
	: null;

export function App() {
	return (
		<Routes>
			<Route element={<Layout />}>
				<Route path="/" element={<Health />} />
				{DevTokens && (
					<Route
						path="/dev/tokens"
						element={
							<Suspense fallback={null}>
								<DevTokens />
							</Suspense>
						}
					/>
				)}
			</Route>
		</Routes>
	);
}
