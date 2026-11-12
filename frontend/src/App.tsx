import { Route, Routes } from "react-router";
import { Layout } from "@/layouts/Layout";
import { Health } from "@/pages/Health";

export function App() {
	return (
		<Routes>
			<Route element={<Layout />}>
				<Route path="/" element={<Health />} />
			</Route>
		</Routes>
	);
}
