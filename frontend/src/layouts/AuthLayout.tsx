import { Outlet } from "react-router";

/** One column on a phone; a centred card at most 420 px wide on a desktop (D-043). */
export function AuthLayout() {
	return (
		<main className="mx-auto flex min-h-dvh w-full max-w-[420px] flex-col justify-center p-4 sm:p-6">
			<h1 className="mb-6 text-center text-3xl font-bold tracking-tight">
				tWIN!!
			</h1>
			<div className="border-border bg-surface rounded-lg border p-5 sm:p-6">
				<Outlet />
			</div>
		</main>
	);
}
