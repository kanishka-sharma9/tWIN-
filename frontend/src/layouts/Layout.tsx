import { Outlet } from "react-router";

export function Layout() {
	return (
		<main className="mx-auto w-full max-w-3xl p-4 sm:p-8">
			<Outlet />
		</main>
	);
}
